# Release Notes - v0.2.1

**Release Date:** October 27, 2025

## Overview

v0.2.1 is a maintenance and quality release focused on **Python compatibility**, **test stability**, and **repository organization** in preparation for production deployment.

## What's New

### 🔧 Python 3.10+ Compatibility
- Fixed `datetime.UTC` compatibility issue (not available in Python 3.10)
- Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`
- All code now works on Python 3.10.11, 3.11, 3.12, and 3.13+
- CI pipeline verified on Python 3.10 and 3.13

**Files Updated:**
- `src/utils/error_reporting.py`
- `src/app.py`
- `src/logging_config.py`

### ✅ Test Suite Improvements
- Fixed 3 failing unit tests with proper mocking strategies
- All 109 tests now passing on CI and locally
- Improved test coverage and reliability

**Tests Fixed:**
- `test_cover_letter_happy_path` - Enhanced file I/O mocking
- `test_load_env` - Corrected module namespace mocking
- `test_create_card_with_labels_and_custom_fields` - Fixed environment variable names

### 📦 CI/CD Enhancements
- Made Codecov upload non-blocking to prevent CI failures from external rate limits
- Improved CI resilience and stability

### 📁 Repository Organization
- Moved 40 development scripts to `scripts/` folder (not tracked by GitHub)
- Organized ~130+ development documentation to `docs/` folder (not tracked by GitHub)
- Simplified `.gitignore` patterns for better maintainability
- Root directory now contains only essential production files

**Root Directory (Production Only):**
- `README.md` - Project overview
- `SETUP_GUIDE.md` - Installation guide
- `CONTRIBUTING.md` - Development guidelines
- `BACKLOG.md` - Project roadmap
- `CHANGELOG.md` - Version history
- `API.md` - API documentation

## Technical Details

### Breaking Changes
None. This is a fully backward-compatible maintenance release.

### Deprecations
None.

### Known Issues
None.

### Dependencies
No new dependencies added. All changes are internal to existing code.

## Testing

✅ **All 109 Tests Passing**
- 1 integration test
- 108 unit tests across 20 test files
- Code coverage: 47%

**Tested On:**
- Python 3.10.11
- Python 3.13.9

## Migration Guide

No migration needed. Simply update to v0.2.1:

```bash
git checkout v0.2.1
pip install -r requirements.txt
```

## Contributors

This release includes improvements and fixes from development work focused on production readiness.

## Download

- **GitHub Release:** https://github.com/ohkai-ship-it/job-application-automation/releases/tag/v0.2.1
- **Source Code:** Available via `git clone` or direct download from GitHub

## Support

For issues or questions:
1. Check the [README.md](README.md) for quick start guide
2. Review [SETUP_GUIDE.md](SETUP_GUIDE.md) for installation help
3. See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
4. Visit [GitHub Issues](https://github.com/ohkai-ship-it/job-application-automation/issues)

---

**Release Manager:** Automated Release Process  
**Tag:** v0.2.1  
**Commit:** See GitHub for full commit history
