# Testing Guide - Offline Mode

## Manual Test Cases

### Test 1: Online Submission ✅
**Steps:**
1. Navigate to `/?order_id=TEST001&courier_id=123`
2. Fill form with rating 5
3. Submit
4. Verify success message
5. Check database: `SELECT * FROM feedback WHERE order_id='TEST001'`

**Expected:** Immediate success, no queue

---

### Test 2: Offline Submission 📦
**Steps:**
1. Open DevTools → Network → Offline
2. Navigate to feedback form
3. Fill and submit
4. Check toast: "Saved offline"
5. Check localStorage: `pending_queue` has 1 item

**Expected:** Item in queue, status = "queued"

---

### Test 3: Auto-Sync 🔄
**Steps:**
1. Complete Test 2 (have item in queue)
2. Go back online (Network → Online)
3. Wait 2 seconds
4. Check toast: "Synced 1 item"
5. Verify localStorage queue empty

**Expected:** Auto-sync, queue cleared

---

### Test 4: Duplicate Prevention 🚫
**Steps:**
1. Submit feedback for ORD123
2. Go offline
3. Submit again for ORD123
4. Go online
5. Check sync behavior

**Expected:** Second submission rejected as duplicate

---

### Test 5: Queue Limit 📊
**Steps:**
1. Set `MAX_QUEUE_SIZE=3` in .env
2. Go offline
3. Submit 4 different orders
4. Check queue length

**Expected:** Queue has 3 items (FIFO, oldest removed)

---

### Test 6: Mixed Online/Offline 🌐
**Steps:**
1. Submit 2 online (success)
2. Go offline
3. Submit 2 (queued)
4. Go online
5. Submit 1 (direct success)
6. Check sync

**Expected:** 2 queued items sync, 1 direct submit

---

## Automated Tests

### Unit Tests (Python)

```python
# test_utils.py
from app.utils import QueueManager, validate_feedback_data

def test_queue_manager_add():
    queue = []
    item = {"order_id": "TEST", "rating": 5}
    result = QueueManager.add_to_queue(queue, item, max_size=2)
    assert len(result) == 1

def test_queue_manager_fifo():
    queue = [{"order_id": "1"}, {"order_id": "2"}]
    new_item = {"order_id": "3"}
    result = QueueManager.add_to_queue(queue, new_item, max_size=2)
    assert result[0]["order_id"] == "2"  # Oldest removed
    assert len(result) == 2

def test_validate_feedback():
    valid_data = {
        "order_id": "TEST",
        "courier_id": 123,
        "rating": 5,
        "comment": "Good"
    }
    is_valid, msg = validate_feedback_data(valid_data)
    assert is_valid == True

def test_validate_rating_range():
    invalid_data = {
        "order_id": "TEST",
        "courier_id": 123,
        "rating": 6  # Invalid
    }
    is_valid, msg = validate_feedback_data(invalid_data)
    assert is_valid == False
    assert "Rating" in msg
```

Run tests:
```bash
pytest tests/test_utils.py -v
```

---

## Browser Console Tests

### Check Online Status
```javascript
console.log('Online:', navigator.onLine);
```

### Inspect Queue
```javascript
const queue = JSON.parse(localStorage.getItem('feedback_pending_queue') || '[]');
console.table(queue);
```

### Simulate Offline Event
```javascript
window.dispatchEvent(new Event('offline'));
```

### Simulate Online Event
```javascript
window.dispatchEvent(new Event('online'));
```

### Manual Sync Trigger
```javascript
// Dispatch custom event
window.dispatchEvent(new CustomEvent('reflex:update_online_status', {
    detail: {is_online: true}
}));
```

---

## Performance Tests

### Queue Processing Speed

**Test:** Time to sync 50 items

```python
import time
from app.states.feedback_state import FeedbackState

# Populate queue with 50 items
state = FeedbackState()
state.pending_queue = [
    {"order_id": f"TEST{i}", "courier_id": 123, "rating": 5}
    for i in range(50)
]

# Measure sync time
start = time.time()
await state.process_queue()
duration = time.time() - start

print(f"Synced 50 items in {duration:.2f}s")
# Target: < 10 seconds
```

### Storage Usage

```javascript
// Check localStorage size
const size = new Blob(Object.values(localStorage)).size;
console.log('Storage used:', (size / 1024).toFixed(2), 'KB');
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Offline Mode

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest

      - name: Run unit tests
        run: pytest tests/ -v

      - name: Test offline functionality
        run: |
          python -m pytest tests/test_offline.py -v
```

---

## Regression Checklist

Before each release:

- [ ] Online submission works
- [ ] Offline submission queues correctly
- [ ] Auto-sync triggers on online event
- [ ] Duplicate prevention works
- [ ] Queue limit enforced (FIFO)
- [ ] Toast notifications display
- [ ] localStorage persists across reload
- [ ] Error handling graceful
- [ ] No console errors
- [ ] Mobile browsers supported

---

## Known Issues

### Issue: Safari Private Mode
**Problem:** localStorage not available in private browsing
**Workaround:** Detect and show warning message

```javascript
try {
    localStorage.setItem('test', 'test');
    localStorage.removeItem('test');
} catch (e) {
    alert('Private browsing detected. Offline mode unavailable.');
}
```

### Issue: iOS Background Sync
**Problem:** Online events don't fire when app backgrounded
**Workaround:** Use `visibilitychange` event

```javascript
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && navigator.onLine) {
        // Trigger sync
    }
});
```
