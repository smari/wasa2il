# Usage:
#   docker build -t wasa2il .
#   docker run -it -p 8000:8000 wasa2il
FROM python:2-onbuild

CMD python initial_setup.py && cd wasa2il && python manage.py runserver $(hostname -i):8000
