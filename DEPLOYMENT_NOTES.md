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

---

## Infrastructure Details

### Staging Server (Test)
- **Hostname**: ________________________
- **IP Address**: ________________________
- **SSH User**: ________________________
- **SSH Key Location**: ________________________
- **Domain**: staging.your-domain.com
- **Port**: 5000 (or other)
- **Root Path**: /opt/job-automation (suggested)
- **Python Version**: 3.10+
- **OS**: Ubuntu 20.04 LTS

### Production Server (Live)
- **Hostname**: ________________________
- **IP Address**: ________________________
- **SSH User**: ________________________
- **SSH Key Location**: ________________________
- **Domain**: your-domain.com
- **Port**: 80/443
- **Root Path**: /opt/job-automation (suggested)
- **Python Version**: 3.10+
- **OS**: Ubuntu 20.04 LTS

---

## Important Files & Locations

### Credentials (NEVER COMMIT ⚠️)
- **Location**: `config/.env`
- **Backup Location**: Stored in password manager ✅
- **Last Rotated**: ________________________
- **Rotation Schedule**: Every 3 months (reminder set: ________)

### Database Files
- **Staging Database**: `data/staging.db`
- **Production Database**: `data/production.db`
- **Backup Location**: `backups/` (on server)
- **Backup Frequency**: Daily at 2 AM UTC
- **Retention**: Keep 30 days

### Logs
- **Location**: `logs/app.log`
- **Rotation**: Automatic (10MB files, 5 backups kept)
- **Retention**: Keep 30 days
- **Log Viewer Command**: `tail -f logs/app.log`

---

## Team & Contacts

### Team
- **Primary Developer**: Your Name
- **On-Call Contact**: Your Name / Number
- **Emergency Escalation**: Your Manager

### Hosting Provider Support
- **Provider**: ________________________
- **Support URL**: ________________________
- **Account Email**: ________________________

---

## Deployment Schedule

- **Regular Deployment Day**: Friday at 4:00 PM UTC
- **Maintenance Window**: Sundays 2:00-3:00 AM UTC (expected downtime: 15-30 min)
- **Maximum Rollback Time**: < 5 minutes
- **Communication Channel**: Slack / Email / Other: ________________________

---

## Health Checks

### Automated Monitoring
- **Health Check URL**: https://your-domain.com/health
- **Check Frequency**: Every 5 minutes
- **Alert Trigger**: Status != 200 or response time > 5 seconds
- **Alert Notification**: Slack / Email / SMS: ________________________

### Manual Monitoring
```bash
# Check if service is running
curl https://your-domain.com/health

# Check logs for errors
ssh user@your-domain.com
tail -50 logs/app.log | grep ERROR
```

---

## Backup & Recovery Procedures

### Automated Backup (runs daily)
```bash
# Location: /home/deploy/backups/
# Pattern: db-YYYYMMDD.tar.gz
# Kept: 30 days
# Frequency: 2 AM UTC daily
```

### Manual Backup (if needed)
```bash
ssh user@production.your-domain.com

# Create backup
tar -czf backups/db-manual-$(date +%Y%m%d).tar.gz data/production.db

# List recent backups
ls -lh backups/
```

### Database Restore (if needed)
```bash
ssh user@production.your-domain.com

# Stop service
sudo systemctl stop job-automation

# Restore from backup
tar -xzf backups/db-20250115.tar.gz

# Start service
sudo systemctl start job-automation

# Verify
curl https://your-domain.com/health
```

---

## Deployment Procedure (Quick Reference)

### Create Release
```bash
# On your local machine
git checkout master
git pull origin master

# Create annotated tag
git tag -a v1.0.1 -m "Brief description of changes"

# Push tag
git push origin v1.0.1
```

### Deploy to Staging
```bash
# SSH into staging server
ssh user@staging.your-domain.com

# Navigate to project
cd /opt/job-automation

# Pull staging branch
git checkout staging
git pull origin staging

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest -q

# Restart service
sudo systemctl restart job-automation

# Verify
curl http://staging.your-domain.com/health
```

### Deploy to Production
```bash
# SSH into production server
ssh user@production.your-domain.com

# Navigate to project
cd /opt/job-automation

# Backup current database
cp data/production.db data/production.db.backup

# Checkout specific version
git checkout v1.0.1

# Pull updates
git pull origin master

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest -q

# Restart service
sudo systemctl restart job-automation

# Verify
curl https://your-domain.com/health

# Monitor logs (first 5 minutes)
tail -f logs/app.log
```

---

## Troubleshooting

### Service won't start
```bash
# Check logs
journalctl -u job-automation -n 50

# Check if port is in use
lsof -i :5000

# Try manual start
cd /opt/job-automation
source .venv/bin/activate
python src/app.py
```

### Database locked
```bash
# Check who's using database
lsof | grep production.db

# Restart service
sudo systemctl restart job-automation
```

### API key invalid
```bash
# Check config/.env
cat config/.env | grep OPENAI_API_KEY

# Verify key is still valid at https://platform.openai.com/account/api-keys

# Update if needed
nano config/.env

# Restart service
sudo systemctl restart job-automation
```

### High CPU/Memory usage
```bash
# Check current usage
top

# Check logs for errors
tail -50 logs/app.log | grep ERROR

# Restart service
sudo systemctl restart job-automation
```

---

## Known Issues & Workarounds

### Issue 1: _________________________
- **Cause**: 
- **Workaround**: 
- **Permanent Fix**: 

---

## Lessons Learned

### Lesson 1: _________________________
- **Date**: 
- **What happened**: 
- **How we fixed it**: 
- **How to prevent**: 

---

## Version History

| Version | Date | Changes | Deployed By |
|---------|------|---------|------------|
| v1.0.0 | TBD | Initial production release | ___________ |
| | | | |
| | | | |

---

## Useful Links

- **Repository**: https://github.com/ohkai-ship-it/job-application-automation
- **Deployment Guides**: See DEPLOYMENT_*.md files
- **OpenAI Console**: https://platform.openai.com/account/api-keys
- **Trello App Key**: https://trello.com/app-key
- **Hosting Dashboard**: ________________________

---

## Security Reminders ⚠️

- ✅ Never commit `.env` file
- ✅ Never share API keys in chat/email
- ✅ Never hardcode secrets in code
- ✅ Rotate API keys every 3 months
- ✅ Keep backups in secure location
- ✅ Review access logs monthly
- ✅ Use strong SSH keys (4096 bit)
- ✅ Keep server OS patched & updated

---

## Checklist: Before First Deployment

- [ ] Staging branch created ✅
- [ ] v1.0.0 tag created ✅
- [ ] Hosting platform chosen
- [ ] Staging server provisioned
- [ ] Production server provisioned
- [ ] SSH keys configured
- [ ] config/.env file prepared
- [ ] Database backups configured
- [ ] Health monitoring configured
- [ ] Team trained on procedures
- [ ] Emergency contacts documented
- [ ] Rollback procedure tested (on staging)

---

**Last Updated**: January 15, 2025
**Next Review**: February 15, 2025
