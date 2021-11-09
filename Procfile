release: python manage.py makemigrations --noinput
release: python manage.py migrate
web: gunicorn AMS.wsgi