release: python cleanup_raw.py; python manage.py migrate && python manage.py populate_categories
web: python manage.py collectstatic --noinput && gunicorn go2events.wsgi
