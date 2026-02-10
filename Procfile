release: python manage.py fix_database && python manage.py migrate && python manage.py populate_categories
web: python manage.py collectstatic --noinput && gunicorn go2events.wsgi
