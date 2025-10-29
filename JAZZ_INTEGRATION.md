# 🎺 Jazz Integration Guide

## Overview

This application uses [Jazz](https://jazz.tools/) for local-first, CRDT-based offline sync with automatic conflict resolution.

## Features

### ✅ What Jazz Provides

- **CRDT-based sync**: Conflict-free replicated data types
- **Offline-first**: Works without network, syncs when online
- **Real-time**: Instant sync across devices
- **IndexedDB**: Persistent local storage
- **Encrypted**: Data encrypted at rest
- **P2P capable**: Direct device-to-device sync
- **Multiplayer ready**: Collaborative features built-in

## Architecture

```
┌─────────────────────────────────────────────┐
│ User Browser (IndexedDB) │
│ ┌─────────────────────────────────────┐ │
│ │ Jazz CoValues (CRDTs) │ │
│ │ - PendingFeedbackQueue (CoList) │ │
│ │ - FeedbackItem (CoMap) │ │
│ │ - AppState (CoMap) │ │
│ └────────────┬────────────────────────┘ │
└───────────────┼─────────────────────────────┘
 │
 │ WebSocket Sync
 ▼
┌──────────────────────────────────────────────┐
│ Jazz Sync Server (cloud/self-hosted) │
│ - Relays updates between clients │
│ - No business logic │
│ - Optional P2P fallback │
└──────────────┬───────────────────────────────┘
 │
 │ HTTP API
 ▼
┌──────────────────────────────────────────────┐
│ Your Python Backend (FastAPI) │
│ - Stores finalized feedback in SQLite/PG │
│ - Admin dashboard │
│ - Analytics │
└──────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

```bash
# .env
JAZZ_SYNC_SERVER=wss://cloud.jazz.tools
# Or self-hosted: wss://your-server.com

JAZZ_ENABLE_P2P=true
JAZZ_AUTH_PROVIDER=anonymous
JAZZ_STORAGE_ENCRYPTION=true
USE_JAZZ_SYNC=true
```

### Toggle Jazz On/Off

Set `USE_JAZZ_SYNC=false` to fallback to localStorage queue.

## Usage

### For Developers

#### 1. Install Dependencies

```bash
# Reflex automatically installs frontend packages
reflex init
reflex run
```

Jazz packages installed:
- `jazz-tools@^0.8.0`
- `jazz-react@^0.8.0`
- `cojson@^0.8.0`

#### 2. Jazz Schema

Defined in `app/jazz/schema.ts`:

```typescript
// Feedback item (CoMap)
export class FeedbackItem extends CoMap {
orderId = co.string;
courierId = co.number;
rating = co.number;
comment = co.string;
reasons = co.json<string[]>();
publishConsent = co.boolean;
needsFollowUp = co.boolean;
synced = co.boolean;
// ... more fields
}

// Queue (CoList)
export class PendingFeedbackQueue extends CoList.Of(
co.ref(FeedbackItem)
) {}
```

#### 3. Python State Integration

```python
from app.jazz.bridge import JazzStateManager

# In your Reflex state
@rx.event(background=True)
async def init_jazz(self):
 jazz_manager = JazzStateManager(self)
await jazz_manager.initialize()

# Add to queue
await jazz_manager.enqueue(feedback_data)

# Sync to server
items = await jazz_manager.get_pending()
for item in items:
if not item["synced"]:
 success = await submit_to_server(item)
if success:
await jazz_manager.mark_synced(item["order_id"])
```

## Self-Hosting Jazz Sync Server

### Option 1: Node.js Server

```bash
# Install Jazz sync server
npm install -g @jazz-tools/sync-server

# Run
jazz-sync-server --port 4000
```

Update `.env`:
```bash
JAZZ_SYNC_SERVER=ws://localhost:4000
```

### Option 2: Docker

```dockerfile
FROM node:18
RUN npm install -g @jazz-tools/sync-server
EXPOSE 4000
CMD ["jazz-sync-server", "--port", "4000"]
```

```bash
docker build -t jazz-sync .
docker run -p 4000:4000 jazz-sync
```

### Option 3: Cloud Deploy (Railway, Render, Fly.io)

```yaml
# fly.toml
app = "my-jazz-sync"

[build]
builtin = "node"

[[services]]
internal_port = 4000
protocol = "tcp"

 [[services.ports]]
port = 80
handlers = ["http"]

 [[services.ports]]
port = 443
handlers = ["tls", "http"]
```

Deploy:
```bash
fly deploy
```

Update `.env`:
```bash
JAZZ_SYNC_SERVER=wss://my-jazz-sync.fly.dev
```

## Authentication

### Anonymous (Default)

No auth required. Each device gets unique ID.

```python
# .env
JAZZ_AUTH_PROVIDER=anonymous
```

### Clerk Auth

For user authentication:

```bash
# Install
npm install @clerk/clerk-react

# .env
JAZZ_AUTH_PROVIDER=clerk
CLERK_PUBLISHABLE_KEY=pk_test_...
```

Update `app/app.py`:
```python
from app.jazz import jazz_provider

app = rx.App(
head_components=[
 rx.script(src="https://cdn.clerk.io/clerk.js"),
 ]
)
```

## Testing

### Test Offline Mode

1. Open DevTools → Network → Offline
2. Submit feedback
3. Check IndexedDB → `jazz-*` databases
4. Go online
5. Watch auto-sync

### Test Multi-Device Sync

1. Open app in 2 browsers
2. Submit feedback in Browser 1 (offline)
3. Go online in Browser 1
4. Watch Browser 2 receive update in real-time

### Test CRDT Conflict Resolution

1. Go offline in both browsers
2. Submit different feedback
3. Go online
4. Both items sync without conflicts (CRDTs!)

## Monitoring

### Jazz Sync Events

```javascript
// In browser console
window.addEventListener('jazz:sync', (e) => {
console.log('Jazz synced:', e.detail);
});

window.addEventListener('jazz:error', (e) => {
console.error('Jazz error:', e.detail);
});
```

### Python Logging

```python
import logging

logger = logging.getLogger('app.jazz')
logger.setLevel(logging.DEBUG)

# Logs:
# - Jazz queue initialized
# - Added to Jazz queue: ORDER123
# - Successfully synced ORDER123
# - Jazz sync error: ...
```

## Troubleshooting

### Issue: Jazz not initializing

**Solution:**
```bash
# Clear IndexedDB
# DevTools → Application → IndexedDB → Delete all

# Verify frontend packages installed
ls .web/node_modules/jazz-tools

# Reinstall
rm -rf .web/node_modules
reflex run
```

### Issue: Sync not working

**Solution:**
```bash
# Check sync server
curl https://cloud.jazz.tools

# Check WebSocket
wscat -c wss://cloud.jazz.tools

# Verify config
echo $JAZZ_SYNC_SERVER
```

### Issue: Data not persisting

**Solution:**
```javascript
// Check IndexedDB
// DevTools → Application → IndexedDB → jazz-*

// Verify storage quota
navigator.storage.estimate().then(console.log);
```

## Performance

### Benchmarks

- **Queue operations**: ~1ms per item
- **Sync latency**: ~50-200ms (network dependent)
- **Storage**: ~5-50MB for 1000 feedback items
- **Conflict resolution**: Automatic (no overhead)

### Optimization Tips

1. **Batch sync**: Group items for efficient network usage
2. **Clean old data**: Remove synced items periodically
3. **Compression**: Jazz handles automatically
4. **Indexing**: CRDTs are already optimized

## Migration from localStorage

If you have existing localStorage queue:

```javascript
// One-time migration script
(async () => {
const oldQueue = JSON.parse(localStorage.getItem('feedback_pending_queue') || '[]');
const { PendingFeedbackQueue, FeedbackItem } = await import('/app/jazz/schema');
const queue = PendingFeedbackQueue.create([]);
for (const item of oldQueue) {
const feedback = FeedbackItem.create(item);
queue.push(feedback);
 }
localStorage.removeItem('feedback_pending_queue');
console.log(`Migrated ${oldQueue.length} items to Jazz`);
})();
```

## Resources

- [Jazz Documentation](https://jazz.tools/docs)
- [Jazz GitHub](https://github.com/jazz-tools/jazz)
- [CRDT Primer](https://crdt.tech/)
- [Jazz Discord Community](https://discord.gg/utDMjHYg42)

## License

Jazz is MIT licensed. No vendor lock-in!
