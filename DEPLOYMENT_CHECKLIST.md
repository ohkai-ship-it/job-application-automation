# Production Deployment Checklist

## Pre-Deployment (Code Freeze)

### Code Quality
- [ ] All tests passing (109/109)
  ```bash
  python -m pytest -q
  ```
- [ ] No linting errors
  ```bash
  python -m flake8 src/
  ```
- [ ] Code review completed
- [ ] No TODOs left in code
- [ ] Documentation updated

### Security
- [ ] No hardcoded secrets in code
- [ ] API keys stored in `config/.env` only
- [ ] `.env` file in `.gitignore` (confirmed)
- [ ] Credentials validation enabled
- [ ] No debug mode enabled in production

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Manual smoke test on staging
- [ ] Error recovery tested (missing API key, rate limit)
- [ ] Graceful degradation tested

---

## Staging Deployment

### Deploy to Staging
```bash
# SSH into staging server
ssh user@staging.your-domain.com

# Navigate to project
cd /opt/job-application-automation

# Update code
git checkout staging
git pull origin staging

# Install dependencies
pip install -r requirements.txt

# Run tests one more time
python -m pytest -q

# Restart service
systemctl restart job-automation

# Verify
curl http://localhost:5000/health
```

### Testing on Staging
- [ ] Web UI loads (http://staging.your-domain.com)
- [ ] Can enter job URL
- [ ] Can process a test job posting
- [ ] Trello card created successfully
- [ ] Cover letter generated
- [ ] Logs appear in `logs/app.log`
- [ ] Health endpoint responds (http://staging.your-domain.com/health)
- [ ] Database is accessible
- [ ] No errors in logs

### QA Sign-Off
- [ ] Product owner approves changes
- [ ] All features work as expected
- [ ] No regressions detected
- [ ] Performance acceptable

---

## Production Deployment

### Create Release Tag
```bash
# Go to master branch
git checkout master
git pull origin master

# Create annotated tag
git tag -a v1.0.0 -m "Production release: [brief description]"

# Push tag (triggers deployment)
git push origin v1.0.0
```

### Deploy to Production
```bash
# SSH into production server
ssh user@production.your-domain.com

# Navigate to project
cd /opt/job-application-automation

# Update code to specific tag
git checkout v1.0.0

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest -q

# Backup current database
cp data/production.db data/production.db.backup

# Restart service
systemctl restart job-automation

# Verify
curl https://your-domain.com/health
```

### Post-Deployment Verification
- [ ] Web UI loads (https://your-domain.com)
- [ ] Health check passes
- [ ] No errors in logs (grep ERROR logs/app.log)
- [ ] Can process a test job
- [ ] Trello integration working
- [ ] Database accessible
- [ ] API keys validated successfully

### Monitoring (First Hour)
- [ ] Check logs every 5 minutes for errors
- [ ] Monitor CPU usage (should be <50%)
- [ ] Monitor memory usage (should be <300MB)
- [ ] Monitor disk space (should be >1GB free)
- [ ] Check response times (should be <2s)

---

## Production Monitoring (Ongoing)

### Daily
- [ ] Check health endpoint
  ```bash
  curl https://your-domain.com/health | python -m json.tool
  ```
- [ ] Check error logs
  ```bash
  grep ERROR logs/app.log | tail -20
  ```
- [ ] Verify database size (should be <100MB)
  ```bash
  ls -lh data/production.db
  ```

### Weekly
- [ ] Review logs for patterns
- [ ] Check for duplicate job processing
- [ ] Verify Trello integration status
- [ ] Check cover letter generation success rate
- [ ] Review any warning messages

### Monthly
- [ ] Backup database
- [ ] Review performance metrics
- [ ] Update dependencies
- [ ] Rotate API keys if needed

---

## Emergency Procedures

### If Something Breaks (Quick Rollback)

**Option 1: Rollback to previous version** (Fastest - 2 min)
```bash
# SSH into production
ssh user@production.your-domain.com
cd /opt/job-application-automation

# Go back to previous version
git checkout v0.9.9
git push origin v0.9.9 --force

# Restart
systemctl restart job-automation

# Verify
curl https://your-domain.com/health
```

**Option 2: Restore from backup** (5 min)
```bash
# Stop service
systemctl stop job-automation

# Restore database
cp data/production.db.backup data/production.db

# Restart
systemctl start job-automation

# Verify
curl https://your-domain.com/health
```

**Option 3: Hot fix** (15-30 min)
```bash
# Create hotfix branch
git checkout master
git checkout -b hotfix/critical-issue

# Fix the bug
# ... edit files ...

# Test locally
python -m pytest -q

# Commit and push
git add .
git commit -m "Fix: critical issue"
git push origin hotfix/critical-issue

# Create PR, merge to master
# Tag and deploy
git checkout master
git pull origin master
git tag -a v0.9.10 -m "Critical hotfix"
git push origin v0.9.10
```

---

## Rollback Scenarios

### "404 page not found"
```bash
# Service crashed, restart it
systemctl restart job-automation
curl https://your-domain.com/health
```

### "Could not connect to database"
```bash
# Check database file exists
ls -la data/production.db

# Check permissions
chmod 666 data/production.db

# Restart service
systemctl restart job-automation
```

### "Authentication failed: OpenAI API"
```bash
# Check credentials
grep OPENAI_API_KEY config/.env

# Verify key is valid at https://platform.openai.com/account/api-keys

# Restart service
systemctl restart job-automation
```

### "Trello connection timeout"
```bash
# This is non-critical, service continues
# Check Trello status at https://www.trellostatus.com

# No action needed, graceful degradation handles it
tail -f logs/app.log | grep -i trello
```

### "Rate limit exceeded"
```bash
# Check logs to see retry attempts
grep "Rate limit" logs/app.log

# Service auto-retries, no action needed
# If persistent, consider upgrading API plan
```

---

## Performance Baseline

Record these values after first deployment:

| Metric | Baseline | Alert If |
|--------|----------|----------|
| Response time (p50) | ___ ms | > 2000 ms |
| Response time (p95) | ___ ms | > 5000 ms |
| CPU usage | __% | > 80% |
| Memory usage | ___ MB | > 500 MB |
| Disk usage | ___ MB | > 80% full |
| Error rate | __% | > 1% |
| Uptime | __% | < 99.5% |

---

## Communication

### Before Deployment
```
📢 Notification: Deployment planned today at 4:00 PM UTC
   - Expected downtime: 2-5 minutes
   - Features: [list changes]
   - No action required from users
```

### After Deployment
```
✅ Deployment complete: v1.0.0
   - All systems operational
   - No issues detected
   - Ready for use
```

### If Rollback Needed
```
⚠️ Issue detected: Rolling back to v0.9.9
   - Service may be unavailable for 5 minutes
   - Investigating root cause
   - Will update in 1 hour
```

---

## Maintenance Windows

### Weekly (Tuesday 10 PM UTC)
- Log rotation
- Database optimization
- Temporary spike in resource usage acceptable

### Monthly (First Sunday, 2 AM UTC)
- Major dependency updates
- Database maintenance
- Expected downtime: 15-30 minutes

---

## Success Criteria

### Deployment is successful if:
- ✅ Web UI loads without errors
- ✅ Health endpoint returns 200 OK
- ✅ Can process a job posting
- ✅ No errors in logs (first 30 min)
- ✅ Response times normal
- ✅ CPU/memory usage acceptable
- ✅ Database accessible

### Rollback triggers:
- ❌ Health endpoint returns 500+
- ❌ > 5 errors in first 5 minutes
- ❌ Response time > 10 seconds
- ❌ Service crash (restarts continuously)
- ❌ Data corruption detected

---

## Files to Keep Safe

```
📁 Production Server
├─ config/.env (CRITICAL - never lose!)
├─ data/production.db (CRITICAL - backup daily)
├─ logs/app.log (Important - keep 30 days)
└─ backups/ (CRITICAL - keep offsite)
```

**Backup Procedure**:
```bash
# Daily at 2 AM
0 2 * * * tar -czf backups/db-$(date +\%Y\%m\%d).tar.gz data/production.db

# Keep 30 days
find backups/ -mtime +30 -delete

# Copy to offsite storage (S3, Google Drive, etc)
# aws s3 cp backups/ s3://my-backups/job-automation/ --recursive
```

---

## Deployment Automation (GitHub Actions)

When ready to automate, use this template:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags: [v*]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run tests
        run: python -m pytest -q
      
      - name: Deploy to production
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
        run: |
          ssh -i $DEPLOY_KEY user@$DEPLOY_HOST 'cd /opt/job-automation && git pull && systemctl restart job-automation'
      
      - name: Health check
        run: curl https://your-domain.com/health
```

---

## Quick Reference

### Deploy to Staging
```bash
git push origin feature-branch
# → Pull request to staging
# → Merge when ready
# → Automatic deployment
```

### Deploy to Production
```bash
git tag -a v1.0.0 -m "Release message"
git push origin v1.0.0
# → Automatic deployment to production
```

### Rollback to Previous Version
```bash
git checkout v0.9.9
git push origin v0.9.9 --force
# → Service auto-updates
```

### Check Health
```bash
curl https://your-domain.com/health
```

### View Logs
```bash
ssh user@production.your-domain.com
tail -f /opt/job-automation/logs/app.log
```

---

## Next Steps

1. ✅ This week: Create staging branch
2. ✅ This week: Tag v1.0.0 release
3. ⏳ Next week: Deploy to staging server
4. ⏳ Following week: Deploy to production
5. ⏳ Ongoing: Monitor and maintain

**You're ready to go live! 🚀**
