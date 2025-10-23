#!/usr/bin/env python
"""Quick test to verify changes don't break core functionality"""
import sys
import subprocess

result = subprocess.run([sys.executable, '-m', 'pytest', '-q', '--tb=short'], 
                       capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
sys.exit(result.returncode)
