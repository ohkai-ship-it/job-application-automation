# Option B: Full Preparation - Getting Started Guide

## Status: 🚀 STARTING IMPLEMENTATION

This guide walks you through Option B (Full Preparation) step-by-step.

---

## Phase 1: Preparation (This Week - 30 Minutes)

### ✅ Step 1: Create Staging Branch (5 minutes)

**What you're doing**: Creating a new branch for testing before production

```bash
# Make sure you're on master
git checkout master
git pull origin master

# Create staging branch from master
git checkout -b staging

# Push to GitHub (creates branch on remote)
git push origin staging

# Verify it worked
git branch -a
# You should see:
#   master
#   * staging
#   remotes/origin/master
#   remotes/origin/staging
```

**Expected output**:
```
Branch 'staging' set up to track 'origin/staging'
```

---

### ✅ Step 2: Protect Staging Branch (GitHub Settings)

**What you're doing**: Preventing accidental breaking of staging branch

**In GitHub (browser)**:
1. Go to: https://github.com/ohkai-ship-it/job-application-automation
2. Settings → Branches → Add rule
3. Fill in:
   - Branch name pattern: `staging`
   - Check: "Require a pull request before merging"
   - Check: "Require status checks to pass before merging"
   - Check: "Require branches to be up to date before merging"
4. Click "Create"

**Result**: Staging branch now protected - can only merge with PR + tests passing

---

### ✅ Step 3: Tag Your First Release (2 minutes)

**What you're doing**: Creating a version marker for your first production release

```bash
# Switch to master branch
git checkout master
git pull origin master

# Create annotated tag (recommended for releases)
git tag -a v1.0.0 -m "Production release: Secure, resilient, observable

- Credential validation at startup
- Exponential backoff retry logic for API failures  
- Graceful degradation for optional services
- Health check endpoint for monitoring
- Comprehensive JSON logging with rotating handlers
- 109 tests passing, 100% backward compatible
- Full production deployment documentation"

# Push tag to GitHub
git push origin v1.0.0

# Verify it worked
git tag -l -n
# Output: v1.0.0    Production release: Secure, resilient...

git describe --tags
# Output: v1.0.0
```

**Expected output**:
```
* [new tag]         v1.0.0 -> v1.0.0
```

---

### ✅ Step 4: Read Key Documentation (15 minutes)

**What you're doing**: Understanding the deployment process

**Read in this order:**

1. **DEPLOYMENT_WALKTHROUGH.md** (10 min)
   - High-level overview
   - Key concepts
   - Common mistakes
   - Next steps
   
2. **DEPLOYMENT_VISUAL_GUIDE.md** (5 min)
   - Visual diagrams
   - Timeline examples
   - You are here diagrams

**Why this order**: Build understanding progressively

---

### ✅ Step 5: Document Your Infrastructure (8 minutes)

**What you're doing**: Recording your deployment information for reference

**Create file: `DEPLOYMENT_NOTES.md`**

```bash
# Create the file
touch DEPLOYMENT_NOTES.md
```

**Add this content** (fill in your choices):

```markdown
# Deployment Infrastructure Notes

## Your Choices

### Hosting Platform
- [ ] Cloud (Heroku, AWS, Google Cloud, etc.)
  - **Which**: _________________
  - **Region**: _________________
  
- [ ] VPS (Linode, Vultr, DigitalOcean, etc.)
  - **Which**: _________________
  - **Region**: _________________
  - **OS**: Linux (Ubuntu 20.04+)
  
- [ ] On-premise
  - **Location**: _________________

### Automation Level
- [ ] Manual (I'll run scripts manually)
- [ ] Semi-automated (Webhook triggers)
- [ ] Fully automated (GitHub Actions)

## Infrastructure Details

### Staging Server (Test)
- **Hostname**: ________________________
- **IP Address**: ________________________
- **SSH User**: ________________________
- **SSH Key**: ________________________
- **Domain**: staging.your-domain.com
- **Port**: 5000 (or other)
- **Path**: /opt/job-automation (suggested)

### Production Server (Live)
- **Hostname**: ________________________
- **IP Address**: ________________________
- **SSH User**: ________________________
- **SSH Key**: ________________________
- **Domain**: your-domain.com
- **Port**: 80/443
- **Path**: /opt/job-automation (suggested)

## Important Files

### Credentials (NEVER COMMIT)
- Location: `config/.env`
- Backup: Stored in password manager ✅
- Last rotated: ________________________

### Database
- Staging: `data/staging.db`
- Production: `data/production.db`
- Backup location: `backups/`
- Backup frequency: Daily at 2 AM UTC

### Logs
- Location: `logs/app.log`
- Rotation: Automatic (10MB files, 5 backups)
- Retention: Keep 30 days

## Contacts

### Team
- Developer: Your Name
- On-call: Your Name
- Emergency: Your Phone

## Release Schedule

- **Deployment day**: Friday at 4:00 PM UTC
- **Maintenance window**: Sundays 2:00-3:00 AM UTC
- **Rollback time**: < 5 minutes

## Health Checks

- **URL**: https://your-domain.com/health
- **Frequency**: Every 5 minutes
- **Alert if**: Status != 200 or response time > 5s

## Backup Procedure

```bash
# Manual backup (if needed)
tar -czf backups/db-manual-$(date +%Y%m%d).tar.gz data/production.db

# Restore from backup
tar -xzf backups/db-20250115.tar.gz
```

## Deployment Procedure (Quick Reference)

```bash
# Create release
git tag -a v1.0.1 -m "Description"
git push origin v1.0.1

# Manual deployment to staging
ssh user@staging.your-domain.com
cd /opt/job-automation
git checkout staging
git pull origin staging
pip install -r requirements.txt
pytest -q
systemctl restart job-automation

# Manual deployment to production
ssh user@production.your-domain.com
cd /opt/job-automation
git checkout v1.0.1
git pull origin main
pip install -r requirements.txt
pytest -q
systemctl restart job-automation
curl https://your-domain.com/health
```

## Known Issues & Workarounds

### None yet!

## Lessons Learned

### None yet!
```

**Add file to git:**
```bash
git add DEPLOYMENT_NOTES.md
git commit -m "Add infrastructure deployment notes"
git push origin master
```

---

## Phase 2: Server Setup (Next Week - Varies)

### 🔄 Step 6: Choose Hosting Platform

**Decision to make this week** (but don't need to act yet):

**Option 1: Cloud (Easiest)**
```
Heroku, AWS, Google Cloud, or DigitalOcean
✅ Easiest setup
✅ Automatic backups
✅ Built-in monitoring
❌ More expensive
⏱️ Setup time: 1-2 hours
```

**Option 2: VPS (Recommended for learning)**
```
Linode, Vultr, or DigitalOcean Droplet
✅ Good balance
✅ Full control
✅ Cheaper than managed cloud
✅ Great for learning
❌ More configuration
⏱️ Setup time: 2-3 hours per server
```

**Option 3: On-premise (Most control)**
```
Your own server/computer
✅ Full control
❌ Your responsibility
❌ Maintenance burden
⏱️ Setup time: 3-4 hours per server
```

**Recommendation**: Start with VPS (Linode or Vultr)
- Good learning experience
- Not too expensive (~$5-10/month)
- Plenty of tutorials available

---

### 🔄 Step 7: Set Up Staging Server (Next Week)

**Timeline**: Monday of next week

**If using Linode/Vultr** (similar for others):

```bash
# 1. Create new Linode/Droplet
#    - OS: Ubuntu 20.04 LTS
#    - Size: 2GB RAM, 1 CPU (minimum)
#    - Region: Choose closest to you
#    - Note: "job-automation-staging"

# 2. SSH into server
ssh root@YOUR_STAGING_IP

# 3. Update system
apt update && apt upgrade -y

# 4. Install Python and dependencies
apt install -y python3.10 python3-pip python3-venv git curl

# 5. Create deployment user
useradd -m -s /bin/bash deploy
su - deploy

# 6. Clone repository
git clone https://github.com/ohkai-ship-it/job-application-automation.git
cd job-application-automation

# 7. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 8. Install Python packages
pip install -r requirements.txt

# 9. Create config/.env file
# (Copy from your local machine)
nano config/.env
# Add:
# OPENAI_API_KEY=your-key
# TRELLO_KEY=your-key
# etc.

# 10. Test locally
python src/app.py
# Visit: http://YOUR_STAGING_IP:5000
# Press Ctrl+C to stop

# 11. Set up systemd service (for auto-start)
sudo nano /etc/systemd/system/job-automation.service
```

**Service file content:**
```ini
[Unit]
Description=Job Application Automation
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/home/deploy/job-automation-automation
Environment="PATH=/home/deploy/job-automation/.venv/bin"
ExecStart=/home/deploy/job-automation/.venv/bin/python src/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable service
sudo systemctl enable job-automation
sudo systemctl start job-automation
sudo systemctl status job-automation
```

---

### 🔄 Step 8: Set Up Production Server (Next Week)

**Timeline**: Wednesday of next week (after staging tested)

**Same steps as staging**, but:
- Create with more resources (for safety)
- Use a different IP/domain
- Extra backups

---

## 📋 Week-by-Week Timeline

### Week 1 (This Week): Preparation ✅
```
Monday-Tuesday:   ✓ Create staging branch (DONE)
Tuesday:          ✓ Create release tag v1.0.0 (DONE)
Wednesday-Friday: ✓ Read documentation (DOING)
Friday:           ✓ Document infrastructure (DOING)

Result: Ready to build servers next week
```

### Week 2 (Next Week): Staging Server Setup
```
Monday:  Set up staging server infrastructure
Tuesday: Deploy to staging + manual testing
Wednesday-Thursday: QA approval + final testing
Friday: Server proven stable, ready for production setup
```

### Week 3 (Following Week): Production
```
Monday: Set up production server infrastructure
Tuesday-Wednesday: Production deployment preparation
Thursday: Deploy to production (v1.0.0 goes live!)
Friday: Monitor, celebrate 🎉
```

---

## 🎯 Checklist: Phase 1 Complete?

- [x] ✅ Create staging branch
- [x] ✅ Protect staging branch (GitHub)
- [x] ✅ Tag v1.0.0 release
- [x] ✅ Read documentation
- [x] ✅ Create DEPLOYMENT_NOTES.md
- [ ] ⏳ Choose hosting platform (complete this week)
- [ ] ⏳ Create staging server (next week)
- [ ] ⏳ Test on staging (next week)
- [ ] ⏳ Deploy to production (following week)

---

## 🎓 What You Learned

**This week you:**
- ✅ Set up proper git workflow (master + staging)
- ✅ Created your first production release (v1.0.0)
- ✅ Documented your deployment strategy
- ✅ Planned your infrastructure

**Next week you:**
- ⏳ Will set up actual servers
- ⏳ Will deploy code to staging
- ⏳ Will test and verify

**Following week:**
- ⏳ Will deploy to production (LIVE!)

---

## 📚 Reference During Execution

**When you get stuck, read:**
- `DEPLOYMENT_STRATEGY.md` - Why you're doing this
- `DEPLOYMENT_VISUAL_GUIDE.md` - How it works
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step procedures

**For server setup:**
- Your hosting provider's documentation
- `PRODUCTION_SETUP.md` - Credential configuration

---

## 🚀 You're Ready!

**Phase 1 is quick** (30 minutes):
1. ✅ Create staging branch (5 min)
2. ✅ Tag v1.0.0 (2 min)
3. ✅ Read docs (15 min)
4. ✅ Document infrastructure (8 min)

**Then you're ready** for Phase 2 (server setup).

---

## Next Steps

1. **Right now**: Run the commands in Step 1-5 above
2. **Today**: Read the documentation
3. **This week**: Choose your hosting platform
4. **Next week**: Set up servers and deploy to staging

**Let's go! 🚀**
