web: gunicorn --bind 0.0.0.0:$PORT --chdir app app:app

release: python manage.py db upgrade
