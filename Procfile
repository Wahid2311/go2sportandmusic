release: python manage.py fix_and_migrate && python manage.py populate_categories
web: python manage.py collectstatic --noinput && gunicorn go2events.wsgi
