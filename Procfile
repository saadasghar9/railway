web: python manage.py migrate && python -m spacy download en_core_web_trf --no-cache-dir || (echo "Failed to download en_core_web_trf" && exit 1) && gunicorn wp.wsgi:application