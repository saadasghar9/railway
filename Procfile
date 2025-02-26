web: python manage.py migrate && python -m pip uninstall -y en-core-web-sm && python -m spacy download en_core_web_trf --no-cache-dir && exec gunicorn wp.wsgi:application --bind 0.0.0.0:8080
