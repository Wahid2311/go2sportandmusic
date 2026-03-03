release: bash -c "cd /app && echo 'Starting release process...' && python fix_broken_db.py || true && echo 'Patching CSRF settings...' && python patch_csrf_settings.py || true && echo 'Patching middleware settings...' && python patch_middleware_settings.py || true && echo 'Running migrations...' && python manage.py migrate || true"
web: python manage.py collectstatic --noinput && gunicorn go2events.wsgi
# Branding update: Domain changed from go2sportandmusic.com to tickethouse.net - Mar 03 2026
