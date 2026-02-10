release: bash cleanup_migrations.sh && python manage.py migrate && python manage.py populate_categories
web: python manage.py collectstatic --noinput && gunicorn go2events.wsgi
