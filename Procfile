web: python -m spacy download en_core_web_trf --no-cache-dir && python manage.py migrate && exec gunicorn wp.wsgi:application --bind 0.0.0.0:8000
