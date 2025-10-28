# 🚀 Deployment Modes Guide

## Quick Start

### 1️⃣ Jazz-Only (No Backend!)

**Perfect for**: Prototypes, offline-first apps, no server cost

```bash
# .env
APP_MODE=jazz_only
JAZZ_SYNC_SERVER=wss://cloud.jazz.tools
```

```bash
# Run (no database needed!)
reflex run
```

**Features**:
- ✅ Fully offline
- ✅ No backend server
- ✅ No database
- ✅ Free Jazz cloud sync
- ✅ Works on mobile
- ❌ No server-side validation
- ❌ Limited to Jazz storage limits

**Architecture**:
```
┌─────────────┐
│   Browser   │ ← All logic here
│  (Jazz DB)  │
└──────┬──────┘
       │
       │ WebSocket (optional)
       ▼
┌─────────────┐
│ Jazz Cloud  │ ← Just relays data
└─────────────┘
```

---

### 2️⃣ Hybrid (Recommended)

**Perfect for**: Production apps, best of both worlds

```bash
# .env
APP_MODE=hybrid
DATABASE_URL=sqlite:///./reflx.db
JAZZ_SYNC_SERVER=wss://cloud.jazz.tools
```

```bash
# Run
reflex run
```

**Features**:
- ✅ Offline-first with Jazz
- ✅ Server validation
- ✅ SQL analytics
- ✅ Best UX
- ⚠️ Requires backend

**Architecture**:
```
┌─────────────┐
│   Browser   │
│ (Jazz sync) │
└──────┬──────┘
       │
       ├─→ Jazz Cloud (real-time)
       │
       └─→ Your Backend (validation, analytics)
           └─→ PostgreSQL/SQLite
```

---

### 3️⃣ Traditional (Legacy)

**Perfect for**: If you don't want Jazz

```bash
# .env
APP_MODE=traditional
DATABASE_URL=sqlite:///./reflx.db
```

**Features**:
- ✅ Simple
- ❌ No offline mode
- ❌ No real-time sync

---

### 4️⃣ Offline-First

**Perfect for**: Mobile, unreliable networks

```bash
# .env
APP_MODE=offline_first
DATABASE_URL=sqlite:///./reflx.db
JAZZ_SYNC_SERVER=wss://cloud.jazz.tools
```

**Features**:
- ✅ Works 100% offline
- ✅ Syncs to backend when online
- ✅ Jazz as primary storage
- ✅ Backend as backup

---

## Comparison Table

| Feature | Traditional | Jazz-Only | Hybrid | Offline-First |
|---------|------------|-----------|---------|---------------|
| **Backend Required** | ✅ Yes | ❌ No | ✅ Yes | ⚠️ Optional |
| **Database Required** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Offline Support** | ❌ No | ✅ Full | ✅ Full | ✅ Full |
| **Real-time Sync** | ❌ No | ✅ Jazz | ✅ Jazz | ✅ Jazz |
| **Multi-device** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Cost** | 💰 Server | 🆓 Free* | 💰 Server | 💰 Server |
| **Scalability** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Complexity** | ⭐ Simple | ⭐⭐ Easy | ⭐⭐⭐ Medium | ⭐⭐⭐⭐ Advanced |

*Free tier: 100MB storage, 1000 users on Jazz Cloud

---

## Self-Hosting Jazz (Any Mode)

### Local Development
```bash
# Install Jazz sync server
npm install -g @jazz-tools/sync-server

# Run
jazz-sync-server --port 4000

# Update .env
JAZZ_SYNC_SERVER=ws://localhost:4000
```

### Production (Docker)
```dockerfile
# docker-compose.yml
version: '3.8'
services:
  jazz-sync:
    image: node:18
    command: npx @jazz-tools/sync-server --port 4000
    ports:
      - "4000:4000"
    environment:
      - NODE_ENV=production
```

```bash
docker-compose up -d

# Update .env
JAZZ_SYNC_SERVER=wss://your-domain.com
```

---

## Migration Between Modes

### From Traditional → Hybrid
```bash
# 1. Add Jazz to .env
APP_MODE=hybrid
JAZZ_SYNC_SERVER=wss://cloud.jazz.tools

# 2. Existing data stays in SQL
# 3. New submissions go to both Jazz + SQL
```

### From Jazz-Only → Hybrid
```bash
# 1. Set up database
DATABASE_URL=postgresql://...

# 2. Update mode
APP_MODE=hybrid

# 3. Run migration script (see below)
python scripts/migrate_jazz_to_sql.py
```

### Migration Script
```python
# scripts/migrate_jazz_to_sql.py
"""Migrate Jazz data to SQL database."""
import asyncio
from app.jazz.dashboard import JazzDashboardBridge
from app.database import engine, Feedback
from sqlmodel import Session

async def migrate():
    # Get all Jazz data
    jazz_bridge = JazzDashboardBridge()
    feedback_items = await jazz_bridge.get_all_feedback()

    # Insert into SQL
    with Session(engine) as session:
        for item in feedback_items:
            feedback = Feedback(**item)
            session.add(feedback)
        session.commit()

    print(f"✅ Migrated {len(feedback_items)} items")

if __name__ == "__main__":
    asyncio.run(migrate())
```

---

## FAQ

### Q: Can I use Jazz-only mode in production?
**A**: Yes! But consider:
- Data is in browsers (backed up to Jazz Cloud)
- No server-side validation
- Storage limits (100MB free, paid plans available)

### Q: What's the best mode for my use case?
**A**:
- **Prototype/Demo**: Jazz-only
- **Production app**: Hybrid
- **Mobile app**: Offline-first
- **Simple CRUD**: Traditional

### Q: Can I switch modes later?
**A**: Yes! All modes are compatible. Use migration scripts.

### Q: Does Jazz-only need internet?
**A**: No! Works 100% offline. Internet only needed for multi-device sync.

### Q: What if Jazz Cloud goes down?
**A**: Your app still works offline! Self-host or switch to local-only mode.

---

## Performance

### Jazz-Only
- ⚡ **Fastest** - No network calls
- 📦 **Smallest** - No backend
- 💾 **Limited** - Browser storage (~100MB)

### Hybrid
- ⚡ **Fast** - Jazz for UI, SQL for analytics
- 📦 **Medium** - Full stack
- 💾 **Unlimited** - SQL database

### Offline-First
- ⚡ **Very Fast** - Local Jazz cache
- 📦 **Large** - Both Jazz + SQL
- 💾 **Unlimited** - SQL backup

---

## Security

### Jazz-Only
- 🔒 **Encryption**: At rest (optional)
- 🔐 **Auth**: Anonymous or Clerk
- ⚠️ **Validation**: Client-side only

### Hybrid/Offline-First
- 🔒 **Encryption**: Jazz + TLS
- 🔐 **Auth**: Server-side
- ✅ **Validation**: Server-side

---

## Next Steps

1. Choose your mode from table above
2. Update `.env` file
3. Run `reflex run`
4. Test offline mode (DevTools → Network → Offline)
5. Deploy!

**Need help?** Check the troubleshooting guide or open an issue.
