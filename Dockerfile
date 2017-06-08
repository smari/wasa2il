# Please use "docker-compose up" to build, not "docker build"
# Usage:
#   docker build -t wasa2il .
#   docker run -it -p 8000:8000 wasa2il
FROM python:2-onbuild

WORKDIR /usr/src/app

CMD python manage.py runserver 0.0.0.0:8000
