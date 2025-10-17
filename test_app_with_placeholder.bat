@echo off
REM Test script to run Flask app with placeholder cover letters
REM This bypasses OpenAI API calls for testing

echo ========================================
echo Starting Flask App with Placeholder Mode
echo ========================================
echo.
echo OpenAI is DISABLED - using 200-word placeholder
echo.

set USE_PLACEHOLDER_COVER_LETTER=true

.venv\Scripts\python.exe src\app.py

pause
