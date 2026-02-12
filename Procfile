release: bash -c "cd /app && echo 'Starting release process...' && python fix_broken_db.py || true && echo 'Running migrations...' && python manage.py migrate && echo 'Populating categories...' && python manage.py populate_categories && echo 'Release complete!'"
web: python manage.py collectstatic --noinput && gunicorn go2events.wsgi
