# For deployment purpose only
# For local testing run app.py with debug=True

gunicorn --config gunicorn_config.py app:app
