# Usage:
#   docker build -t wasa2il .
#   docker run -t wasa2il
FROM python:2-onbuild

RUN /usr/src/app/initial_setup.py

CMD /usr/src/app/wasa2il/manage.py runserver $(hostname -i):8000
