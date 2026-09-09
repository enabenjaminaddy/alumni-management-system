# Development vs Production Settings

This document explains the differences between development and production settings in this Django project.

## How the Environment Detection Works

In `settings.py`, we use this logic to detect the environment:

```python
IS_DEVELOPMENT = os.environ.get('DJANGO_ENV') == 'development' or 'render.com' not in ALLOWED_HOSTS[0]
DEBUG = IS_DEVELOPMENT if os.environ.get('DEBUG') is None else os.environ.get('DEBUG', 'False').lower() == 'true'
```

This means:
1. If `DJANGO_ENV=development` is set, we're in development mode
2. Or if the first allowed host doesn't contain "render.com", we assume development
3. You can manually override this by setting `DEBUG=true` or `DEBUG=false`

## Development Mode (`DEBUG=True`)

In development mode:
- SSL redirect is disabled (`SECURE_SSL_REDIRECT = False`)
- Secure cookies are disabled
- HSTS is disabled
- More verbose error pages are shown
- Django Debug Toolbar may be available

## Production Mode (`DEBUG=False`)

In production mode:
- HTTPS is enforced
- Secure cookies are enabled
- HSTS security headers are set
- CSRF trusted origins are restricted
- Static files are served by WhiteNoise
- Error details are hidden from users

## How to Run in Different Modes

### Development (Local Testing)

Use the provided batch file:
```
local_dev.bat
```

Or set the environment variables manually:
```
DJANGO_ENV=development python manage.py runserver
```

### Production (Render)

Production settings are automatically applied on Render based on the environment variables you've set in the dashboard.

## Troubleshooting Common Issues

### Redirect Loops
If you're experiencing redirect loops in development:
1. Make sure `DEBUG=True`
2. Clear browser cache and cookies
3. Try a private/incognito browser window
4. Check that `SECURE_SSL_REDIRECT = False` is applied

### CSRF Failures
If you get CSRF errors:
1. Check that you're using the same domain in the URL as in ALLOWED_HOSTS
2. For production, verify CSRF_TRUSTED_ORIGINS includes your domain
3. Make sure you have {% csrf_token %} in your forms