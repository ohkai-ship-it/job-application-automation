# Deployment Process Visual Guide

## Current State (You Are Here)

```
Feature branches
     ↓
   Code review
     ↓
Merge to master (current)
     ↓
✅ Ready for production
```

---

## Recommended: Enhanced Deployment Pipeline

### Simple View (What Happens)

```
┌─ Local Development
│   - Write code
│   - Test locally
│   - Push feature branch
│
├─ GitHub Review
│   - Code review
│   - Automated tests
│   - Merge to staging
│
├─ Staging Environment (Test Server)
│   - Auto-deploy
│   - Manual testing
│   - QA sign-off
│
├─ Production Release
│   - Tag release (v1.0.0)
│   - Merge to main
│   - Auto-deploy to production
│
└─ Production Monitoring
    - Health checks
    - Error monitoring
    - Performance tracking
```

---

## Detailed Git Flow (What You'll Do)

### For a New Feature

```
Day 1: Development
├─ git checkout -b feature/my-awesome-feature
├─ # Edit files, test locally
├─ python -m pytest -q  ✓ All tests pass
├─ git add .
├─ git commit -m "Add awesome feature"
└─ git push origin feature/my-awesome-feature

Day 2: Code Review
├─ Create Pull Request on GitHub
│  └─ Target: staging branch
├─ Another developer reviews
├─ GitHub runs tests automatically
├─ Feedback loop (if needed)
└─ Merge to staging ✓

Day 3: Testing
├─ Automatic deployment to staging server
├─ http://staging.your-domain.com works
├─ Manual testing passes
├─ QA signs off ✓
└─ Create PR: staging → main

Day 4: Production Release
├─ git checkout main
├─ git pull origin main
├─ git tag -a v1.0.1 -m "Add awesome feature"
├─ git push origin v1.0.1
├─ Automatic deployment to production
└─ https://your-domain.com works ✓
```

---

## The Three Branches (Setup These)

### 1️⃣ Master/Main (Protected)
```
main branch (protected)
├─ v1.0.0 ────── Release 1
├─ v1.0.1 ────── Bug fix
├─ v1.1.0 ────── Release 2
├─ v1.1.1 ────── Bug fix
└─ v1.1.2 ────── Critical hotfix

Where: Production (live users)
Deploys to: https://your-domain.com
Protected: Yes (require PR + tests)
```

### 2️⃣ Staging (Protected)
```
staging branch (protected)
├─ Has feature/awesome-feature
├─ Has feature/linkedin-integration
└─ Has bug-fixes

Where: Staging server (test environment)
Deploys to: http://staging.your-domain.com
Protected: Yes (require PR + tests)
```

### 3️⃣ Feature Branches (Temporary)
```
feature/awesome-feature (temporary)
feature/linkedin-integration (temporary)
hotfix/critical-bug (temporary)
develop/* (temporary)

Where: Developer laptops + GitHub
Merged into: staging → main (then deleted)
Protected: No
```

---

## Deployment Timeline

```
Monday 9:00 AM     Feature complete → Create PR to staging
Monday 10:00 AM    Tests pass → Merge to staging
Monday 10:05 AM    Auto-deploy to staging begins
Monday 10:15 AM    Deployment complete ✓
Monday 10:15 AM    Manual testing begins
Monday 5:00 PM     QA approves → Create PR to main
Monday 5:05 PM     Code review complete → Merge to main
Monday 5:10 PM     Create tag v1.1.0
Monday 5:12 AM     Auto-deploy to production begins
Monday 5:15 PM     Deployment complete ✓
Monday 5:15 PM     Monitoring + health checks
Monday 5:30 PM     All clear, feature live ✓
```

---

## Manual Steps (Don't Automate Yet)

### Create Staging Branch (One-time Setup)

```bash
# This week (5 minutes)

git checkout -b staging
git push origin staging

# Then in GitHub:
# Settings → Branches → Add branch protection rule
# - Branch name: staging
# - Require PR reviews: Yes
# - Require status checks: Yes
# - Dismiss approvals on push: Yes
```

### Tag a Release

```bash
# When ready to go to production (2 minutes)

git checkout main
git pull origin main

# Create tag
git tag -a v1.0.0 -m "First production release"

# Push tag (triggers deployment)
git push origin v1.0.0

# Verify
git tag -l -n
# Output: v1.0.0    First production release
```

### Check Health

```bash
# Anytime to verify health (10 seconds)

curl https://your-domain.com/health

# Output:
# {
#   "status": "healthy",
#   "timestamp": "2025-01-15T10:30:45",
#   "services": {
#     "database": "ok",
#     "trello": "ok",
#     "openai": "ok"
#   }
# }
```

---

## Automated Steps (Webhook)

### When You Push a Tag to GitHub

```
You: git push origin v1.0.0
     ↓
GitHub: Tag v1.0.0 created
     ↓
GitHub Webhook triggered
     ↓
Production Server receives:
  - Branch: main (or tag: v1.0.0)
  - Runs: git pull
  - Runs: pip install -r requirements.txt
  - Runs: pytest -q
  - Runs: systemctl restart job-automation
     ↓
Production Service restarts with new code
     ↓
Health check: curl /health
     ↓
Alert if deployment fails
     ↓
Notification: Deployment complete ✓
```

---

## Decision Points During Deployment

```
Start deployment
    ↓
Tests pass?
├─ No → Stop, fix locally, start over
└─ Yes → Continue
    ↓
Health check passes?
├─ No → Rollback to v0.9.9
└─ Yes → Continue
    ↓
Monitor logs for 5 minutes
├─ Errors found?
│  └─ Yes → Rollback
└─ No errors → Continue
    ↓
Deployment complete ✓
```

---

## Rollback Decision Tree

```
Is production broken?
├─ Yes, critical issue
│  ├─ Option 1: Revert to v0.9.9 (fastest)
│  │  └─ git checkout v0.9.9 && git push (2 min)
│  ├─ Option 2: Restore database backup (5 min)
│  │  └─ cp production.db.backup production.db
│  └─ Option 3: Create hotfix (30 min)
│     └─ git checkout -b hotfix/... → merge → tag
│
└─ No, just monitor
   └─ tail -f logs/app.log
```

---

## Services & Environments

```
┌──────────────────────────────────────────┐
│ Your Local Machine                       │
├──────────────────────────────────────────┤
│ Feature: feature/my-feature              │
│ Branch: Local only                       │
│ Database: data/dev.db                    │
│ Server: http://localhost:5000            │
│ Status: Testing                          │
└──────────────────────────────────────────┘
         ↓ (git push)
┌──────────────────────────────────────────┐
│ Staging Server                           │
├──────────────────────────────────────────┤
│ Branch: staging                          │
│ Database: data/staging.db                │
│ Server: http://staging.your-domain.com   │
│ Status: Testing (QA)                     │
│ Auto-deploy on merge                     │
└──────────────────────────────────────────┘
         ↓ (git tag)
┌──────────────────────────────────────────┐
│ Production Server                        │
├──────────────────────────────────────────┤
│ Branch: main (tagged v1.0.0)             │
│ Database: data/production.db             │
│ Server: https://your-domain.com          │
│ Status: Live (Real Users)                │
│ Auto-deploy on tag                       │
└──────────────────────────────────────────┘
```

---

## Files Changed During Deployment

### What Gets Updated

```
Local: feature branch
├─ src/main.py (modified)
├─ tests/test_*.py (added)
└─ CHANGELOG.md (updated)

Staging: staging branch
├─ All files from feature branch
├─ Tested
└─ Ready for production

Production: main branch + tag
├─ All files from staging
├─ Tagged with version (v1.0.0)
├─ Live to users
└─ Backed up

Backup
└─ data/production.db.v1.0.0
```

---

## What Doesn't Change During Deployment

```
🔒 NEVER deployed:
├─ config/.env (credentials)
├─ data/*.db (production data)
├─ logs/*.log (existing logs)
└─ .git (git history)

✅ Already there, stays there:
├─ Credentials (from config/.env)
├─ API keys (loaded from environment)
├─ Database (persists, only backed up)
└─ Logs (appended to, not replaced)
```

---

## Monitoring Dashboard (During Deployment)

```
v1.0.0 Deployment Status
├─ Tests: ✓ PASSED (109/109)
├─ Deploy to staging: ✓ COMPLETE (10:05 AM)
├─ Staging tests: ✓ PASSED
├─ Manual testing: ⏳ IN PROGRESS
├─ QA approval: ⏳ PENDING
├─ Deploy to production: ⏳ WAITING
├─ Health check: ⏳ WAITING
└─ Monitoring: ⏳ WAITING

When all complete:
✅ v1.0.0 LIVE
```

---

## Typical Issues & Resolution

| Issue | Cause | Fix | Time |
|-------|-------|-----|------|
| Health check fails | Code bug | Rollback to v0.9.9 | 2 min |
| Database locked | Permission issue | Check file permissions | 5 min |
| API key invalid | Expired key | Update config/.env | 1 min |
| Tests fail | New bug in code | Fix locally, push again | 15 min |
| Trello down | External service | Continue (graceful degradation) | 0 min |
| Rate limit hit | API overload | Auto-retry 3x | 0 min |

---

## Success Indicators

✅ **Deployment Successful If:**
```
Version: v1.0.0
├─ Git tag created ✓
├─ Tests passed ✓
├─ Deployed in < 5 minutes ✓
├─ Health check: 200 OK ✓
├─ No errors in logs ✓
├─ Response time: < 2s ✓
└─ Live to users ✓
```

❌ **Rollback If:**
```
├─ Health check: 503 ✗
├─ > 5 errors in first minute ✗
├─ Response time: > 10s ✗
├─ Cannot access database ✗
└─ Service crashes ✗
```

---

## Next Week Timeline

```
Monday     ✅ Create staging branch
Tuesday    ✅ Tag v1.0.0 release
Wednesday  ⏳ Deploy to staging server
Thursday   ⏳ Manual testing on staging
Friday     ⏳ Deploy to production
Saturday   ⏳ Monitor production
Sunday     ⏳ Celebrate 🎉
```

---

## You're Ready!

This is the deployment process for your Job Application Automation tool:

1. **Develop** → Feature branch → Local testing
2. **Staging** → PR to staging → Auto-deploy → QA testing
3. **Production** → Tag release → Auto-deploy → Live

Simple, safe, and scalable! 🚀
