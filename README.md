# 🚚 Courier Feedback System

A modern, mobile-first feedback collection platform for courier delivery services with comprehensive admin dashboard and analytics.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Reflex](https://img.shields.io/badge/Reflex-0.4+-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### User Features
- ⭐ **Star Rating System** - Intuitive 1-5 star ratings
- 💬 **Detailed Feedback** - Comment section with 500 character limit
- ✅ **Reason Selection** - Multi-select checkboxes for feedback categories
- 📱 **Mobile-First Design** - Optimized for smartphone users
- 🔒 **Duplicate Prevention** - One feedback per order ID
- 📞 **Courier Contact Display** - Phone and messaging links after submission

### Admin Features
- 🔐 **Secure Authentication** - BCrypt password hashing
- 📊 **Dashboard Analytics** - Comprehensive feedback overview
- 🔍 **Advanced Filtering** - By date range and star rating
- 📥 **CSV Export** - Download filtered feedback data
- 🚨 **Auto Follow-up Flagging** - Low ratings (≤4) automatically flagged
- 📈 **Real-time Updates** - Live feedback monitoring

## 🏗️ Architecture

```
courier-feedback-app/
├── app/
│ ├── __init__.py
│ ├── app.py # Main application entry
│ ├── database.py # SQLModel models & DB setup
│ ├── services.py # Business logic layer
│ ├── api_routes.py # FastAPI endpoints
│ ├── components/
│ │ ├── __init__.py
│ │ └── admin_dashboard.py # Admin UI components
│ ├── pages/
│ │ ├── __init__.py
│ │ ├── feedback.py # User feedback form
│ │ ├── login.py # Admin login
│ │ └── admin_dashboard.py # Dashboard page
│ └── states/
│ ├── __init__.py
│ ├── feedback_state.py # Feedback form state
│ └── admin_state.py # Admin dashboard state
├── assets/ # Static assets
├── config.py # Application configuration
├── requirements.txt # Python dependencies
├── .env.example # Environment variables template
├── .gitignore
└── README.md

```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone
cd courier-feedback-app
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Initialize database**
```bash
# Database tables and default admin will be created on first run
```

### Running the Application

**Development Mode:**
```bash
reflex run
```

The application will start on:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

**Production Mode:**
```bash
reflex run --env prod
```

## 📖 Usage Guide

### For End Users (Customers)

1. **Access Feedback Form**
- Navigate to: `http://localhost:3000/?order_id=YOUR_ORDER&courier_id=123`
- Replace `YOUR_ORDER` with actual order ID
- Replace `123` with actual courier ID

2. **Submit Feedback**
- Select star rating (1-5)
- Write optional comment (max 500 chars)
- Check applicable reason boxes
- Optionally consent to publish feedback
- Click "Submit Feedback"

3. **View Confirmation**
- See thank you message
- View courier contact information
- Call or message courier directly

### For Administrators

1. **Login**
- Navigate to: `http://localhost:3000/admin`
- Default credentials:
- Username: `admin`
- Password: `admin`
- ⚠️ **Change default password in production!**

2. **Dashboard Features**
- **Filter by Date**: Select from/to dates
- **Filter by Rating**: Click star buttons (1-5)
- **Export Data**: Click "Export CSV" button
- **View Details**: Check follow-up flags, comments, reasons

3. **Logout**
- Click "Logout" button in top-right corner

## 🔌 API Endpoints

### Base URL: `http://localhost:8000/api`

#### POST /feedback
Create new feedback entry.

**Request Body:**
```json
{
"order_id": "ORD123",
"courier_id": 123,
"rating": 5,
"comment": "Excellent service!",
"reasons": ["Punctuality", "Politeness"],
"publish_consent": true
}
```

**Response:** `201 Created`
```json
{
"id": 1,
"order_id": "ORD123",
"rating": 5,
"needs_follow_up": false,
"created_at": "2024-01-15T10:30:00"
}
```

#### GET /feedback
List all feedback (with optional courier filter).

**Query Parameters:**
- `courier_id` (optional): Filter by courier ID

**Response:** `200 OK`
```json
[
{
"id": 1,
"order_id": "ORD123",
"courier_id": 123,
"rating": 5,
"comment": "Great!",
"created_at": "2024-01-15T10:30:00"
}
]
```

#### GET /feedback/{feedback_id}
Get single feedback by ID.

**Response:** `200 OK`

#### GET /courier/{courier_id}
Get courier information.

**Response:** `200 OK`
```json
{
"id": 123,
"name": "Alex Doe",
"phone": "+1-800-555-0101",
"contact_link": "https://t.me/alex_courier"
}
```

## 🗄️ Database Schema

### Tables

#### `courier`
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY |
| name | VARCHAR | NOT NULL |
| phone | VARCHAR | NOT NULL |
| contact_link | VARCHAR | NULLABLE |
| created_at | DATETIME | DEFAULT NOW |

#### `feedback`
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY |
| order_id | VARCHAR | UNIQUE, INDEX |
| courier_id | INTEGER | FOREIGN KEY → courier.id |
| rating | INTEGER | CHECK (1-5) |
| comment | VARCHAR(500) | NULLABLE |
| reasons | TEXT (JSON) | NOT NULL |
| publish_consent | BOOLEAN | DEFAULT FALSE |
| needs_follow_up | BOOLEAN | DEFAULT FALSE |
| created_at | DATETIME | DEFAULT NOW |

#### `adminuser`
| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY |
| username | VARCHAR | UNIQUE, INDEX |
| password_hash | VARCHAR | NOT NULL |
| created_at | DATETIME | DEFAULT NOW |

## 🔧 Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```env
# Database (SQLite for development)
DATABASE_URL=sqlite:///./reflx.db

# PostgreSQL for production (example)
# DATABASE_URL=postgresql://user:pass@localhost:5432/courier_feedback

# Admin defaults
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

### Database Migration (SQLite → PostgreSQL)

For production, switch to PostgreSQL:

1. Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

2. Update `.env`:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

3. Run application (tables auto-create):
```bash
reflex run
```

## 🛡️ Security Considerations

### Production Checklist

- [ ] Change default admin password
- [ ] Use strong passwords (12+ characters)
- [ ] Enable HTTPS/TLS
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `APP_ENV=production`
- [ ] Configure proper CORS settings
- [ ] Add rate limiting to API endpoints
- [ ] Implement session timeouts
- [ ] Regular security audits
- [ ] Keep dependencies updated

### Password Security

- Passwords hashed with BCrypt (salt rounds: 12)
- Never store plain-text passwords
- Use environment variables for secrets

## 🧪 Testing

### Manual Testing

1. **Test Feedback Submission:**
```bash
curl -X POST http://localhost:8000/api/feedback \
-H "Content-Type: application/json" \
-d '{
"order_id": "TEST001",
"courier_id": 123,
"rating": 5,
"comment": "Test feedback",
"reasons": ["Punctuality"],
"publish_consent": true
}'
```

2. **Test Duplicate Prevention:**
- Submit same order_id twice
- Should receive 409 Conflict

3. **Test Admin Login:**
- Visit `/admin`
- Enter credentials
- Verify redirect to dashboard

## 📊 Sample Data

The application auto-seeds a sample courier on first run:

- **ID:** 123
- **Name:** Alex Doe
- **Phone:** +1-800-555-0101
- **Contact:** https://t.me/alex_courier

Test URL:
```
http://localhost:3000/?order_id=TEST001&courier_id=123
```

## 🐛 Troubleshooting

### Common Issues

**Issue:** Database locked error (SQLite)
```
Solution: Close all connections, restart app
```

**Issue:** Module not found
```bash
Solution: pip install -r requirements.txt
```

**Issue:** Port already in use
```bash
Solution: Kill process on port 3000/8000
# Linux/Mac: lsof -ti:3000 | xargs kill -9
# Windows: netstat -ano | findstr :3000
```

**Issue:** Admin login fails
```
Solution: Check .env file, verify username/password
Default: admin/admin
```

## 📝 License

MIT License - feel free to use for commercial or personal projects.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📧 Support

For issues or questions:
- Open GitHub issue
- Check documentation
- Review API examples

## 🗺️ Roadmap

- [ ] Email notifications for low ratings
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Webhook integrations
- [ ] SMS feedback collection
- [ ] QR code generation for orders

---

**Built with ❤️ using Reflex Framework**

## 🔌 Offline Support & Local Storage

### Features

- **📦 Offline Queue** - Submit feedback even without internet
- **🔄 Auto-Sync** - Automatic synchronization when connection restored
- **💾 Local Storage** - Persistent queue across browser sessions
- **🔔 Toast Notifications** - Real-time user feedback
- **📊 Queue Status** - Visual indicator of pending submissions

### How It Works

1. **Offline Submission**: When offline, feedback is saved to browser's `localStorage`
2. **Queue Management**: Max 50 items in queue (configurable via `MAX_QUEUE_SIZE`)
3. **Auto-Sync**: Listens for `online` event and processes queue automatically
4. **Duplicate Prevention**: Checks for existing feedback before syncing
5. **Error Recovery**: Failed items remain in queue for retry

### Testing Offline Mode

**Chrome DevTools:**
```
1. Open DevTools (F12)
2. Go to Network tab
3. Select "Offline" from throttling dropdown
4. Submit feedback
5. Check Application → Local Storage → pending_queue
6. Go back online
7. Watch auto-sync in action
```

**Firefox:**
```
1. Open DevTools (F12)
2. Network tab → Toggle offline mode
3. Submit feedback
4. Storage → Local Storage
```

### Configuration

Edit `.env`:

```env
# Enable/disable offline mode
ENABLE_OFFLINE_MODE=true

# Maximum queue size (default: 50)
MAX_QUEUE_SIZE=50

# Retry attempts for failed syncs
SYNC_RETRY_ATTEMPTS=3

# Delay between retries (seconds)
SYNC_RETRY_DELAY=2
```

### Queue Data Structure

Stored in `localStorage` as JSON:

```json
[
  {
    "order_id": "ORD123",
    "courier_id": 123,
    "rating": 5,
    "comment": "Great service!",
    "reasons": ["Punctuality", "Politeness"],
    "publish_consent": true,
    "timestamp": "2024-01-15T10:30:00",
    "request_id": "a1b2c3d4e5f6"
  }
]
```

### Browser Compatibility

| Browser | Local Storage | Online Events | Status |
|---|---|---|---|
| Chrome 90+ | ✅ | ✅ | Fully Supported |
| Firefox 88+ | ✅ | ✅ | Fully Supported |
| Safari 14+ | ✅ | ✅ | Fully Supported |
| Edge 90+ | ✅ | ✅ | Fully Supported |
| Mobile Safari | ✅ | ⚠️ | Limited (use visibility API) |
| Chrome Mobile | ✅ | ✅ | Fully Supported |

### Limitations

- **Storage Limit**: ~5-10MB per domain (browser-dependent)
- **No Server Sync**: Queue only syncs from this device
- **Cache Clearing**: Manual cache clear removes queue
- **Private Browsing**: May not persist across sessions

### Advanced Usage

**Manual Queue Management:**

```javascript
// Access queue in browser console
const queue = JSON.parse(localStorage.getItem('feedback_pending_queue') || '[]');
console.log('Pending items:', queue.length);

// Clear queue (use with caution!)
localStorage.removeItem('feedback_pending_queue');
```

**Force Sync:**

```python
# In your state/component
await FeedbackState.process_queue()
```

## 🚨 Troubleshooting Offline Mode

### Queue Not Syncing

**Issue**: Items remain in queue after going online

**Solutions:**
1. Check browser console for errors
2. Verify network connectivity: `fetch('https://example.com')`
3. Check max queue size not exceeded
4. Manually trigger: `FeedbackState.process_queue()`

### Storage Quota Exceeded

**Issue**: "QuotaExceededError" in console

**Solutions:**
1. Reduce `MAX_QUEUE_SIZE` in `.env`
2. Clear old data: localStorage.clear()
3. Sync and clear queue regularly

### Duplicate Submissions

**Issue**: Same feedback submitted multiple times

**Solutions:**
- Queue management checks `order_id` before sync
- Database has `UNIQUE` constraint on `order_id`
- Duplicate detection runs before insertion

## 📊 Monitoring & Analytics

### Queue Metrics

Monitor these in your admin dashboard:

- **Pending Count**: `len(pending_queue)`
- **Sync Success Rate**: Track in logs
- **Average Queue Time**: Time between save and sync
- **Error Rate**: Failed sync attempts

### Logging

Offline events are logged:

```
2024-01-15 10:30:00 - INFO - Queued feedback for ORD123 (offline)
2024-01-15 10:35:00 - INFO - Processing 3 queued items...
2024-01-15 10:35:02 - INFO - Successfully synced order ORD123
2024-01-15 10:35:03 - WARNING - 1 items failed to sync
```

Check `app.log` in production mode.
