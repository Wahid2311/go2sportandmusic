release: bash -c "cd /app && python manage.py migrate --fake events 0008_remove_service_charge_limit && python manage.py migrate && python manage.py populate_categories"
web: python manage.py collectstatic --noinput && gunicorn go2events.wsgi
