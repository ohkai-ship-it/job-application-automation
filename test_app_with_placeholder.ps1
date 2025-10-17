# Test script to run Flask app with placeholder cover letters
# This bypasses OpenAI API calls for testing

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Flask App with Placeholder Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "OpenAI is DISABLED - using 200-word placeholder" -ForegroundColor Yellow
Write-Host ""

$env:USE_PLACEHOLDER_COVER_LETTER = "true"

& .venv\Scripts\python.exe src\app.py
