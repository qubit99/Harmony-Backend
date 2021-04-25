web: gunicorn --bind 0.0.0.0:$PORT --chdir app app:app

release: python app/manage.py db upgrade
