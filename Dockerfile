# Usage:
#   docker build -t wasa2il .
#   docker run -t -i wasa2il
FROM python:2-onbuild

CMD ./initial_setup.py && cd wasa2il && ./manage.py runserver $(hostname -i):8000
