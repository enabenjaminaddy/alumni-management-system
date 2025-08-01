@echo off
REM Script to set SendGrid API key environment variable for testing
REM Replace the placeholder with your actual SendGrid API key

set SENDGRID_API_KEY=SG.your_actual_api_key_here

echo.
echo SendGrid API key set for this terminal session
echo To test your configuration, run:
echo python manage.py shell ^< test_sendgrid.py
echo.