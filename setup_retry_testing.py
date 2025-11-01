#!/usr/bin/env python
"""
Setup script for cover letter retry testing with debug truncation.

This script:
1. Switches to development database
2. Enables debug truncation mode
3. Prepares the environment for UI testing

Usage:
    python setup_retry_testing.py
    python ./src/app.py
"""

import os
import sys
from pathlib import Path

# Get project root
project_root = Path(__file__).parent

print("=" * 80)
print("COVER LETTER RETRY TESTING - SETUP")
print("=" * 80)

# Step 1: Switch to development database
print("\n[1/3] Setting up development database...")
os.environ['APP_ENV'] = 'development'
os.environ['DB_PATH'] = str(project_root / 'db' / 'applications_dev.db')
print(f"✓ Environment: {os.environ['APP_ENV']}")
print(f"✓ DB Path: {os.environ['DB_PATH']}")

# Step 2: Enable debug truncation mode
print("\n[2/3] Enabling debug truncation mode...")
os.environ['DEBUG_TRUNCATE'] = 'true'
print("✓ DEBUG_TRUNCATE=true")

# Step 3: Show how to use it
print("\n[3/3] Ready for testing!")
print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("\n1. Start the web app in another terminal:")
print("   python ./src/app.py")
print("\n2. Open browser: http://localhost:5000/")
print("\n3. Enable debug mode in browser console (F12 → Console):")
print("   localStorage.setItem('debug_truncate', 'true');")
print("\n4. Now when you submit a job, it will automatically truncate!")
print("\n5. Watch the status:")
print("   - First attempt: cover_letter_failed (120 words - TRUNCATED)")
print("   - Click 'Retry' button: success (full response - NO TRUNCATION)")
print("\n6. Check server logs to see truncation:")
print("   [DEBUG] Truncated cover letter to 120 words...")
print("\n" + "=" * 80)
print("\nSetup complete! Ready to start app.py")
print("=" * 80)
