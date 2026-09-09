# Render Deployment Guide for Alumni Management System

## Environment Variables to Set on Render

These should be added in the Render dashboard under Environment:

```
SECRET_KEY=<your_django_secret_key>
DEBUG=False
SENDGRID_API_KEY=<your_sendgrid_api_key>
DATABASE_URL=<your_postgres_connection_string>
```

## Build Command

```
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

## Start Command

```
gunicorn alumni_management_system.wsgi:application
```

## Troubleshooting CSRF Issues

If you encounter CSRF issues after deploying:

1. **Verify your URL scheme**: Make sure you're accessing the site via HTTPS, not HTTP

2. **Check for proxy headers**: If Render is using a proxy, ensure it correctly passes the HTTPS scheme

3. **Try clearing browser cache/cookies**: Sometimes old CSRF tokens can cause issues

4. **Debug by temporarily setting**:
   ```python
   CSRF_COOKIE_SECURE = False
   SESSION_COOKIE_SECURE = False
   ```

5. **For form submissions**: Ensure all forms include `{% csrf_token %}`

## Deployment Checklist

- [x] Updated DEBUG setting to use environment variable
- [x] Added proper ALLOWED_HOSTS
- [x] Configured STATIC_ROOT and STATICFILES_STORAGE
- [x] Added WhiteNoise middleware
- [x] Added proper security settings for production
- [x] Set up CSRF_TRUSTED_ORIGINS
- [x] Updated requirements.txt
- [ ] Run `python manage.py collectstatic` before deploying
- [ ] Set all required environment variables in Render dashboard
- [ ] Test all forms and authentication flows after deployment