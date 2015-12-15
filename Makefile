venv:
	virtualenv venv
	venv/bin/pip install -r requirements.txt

init: venv
	venv/bin/python initial_setup.py --venv

run: venv
	cd wasa2il && ../venv/bin/python ./manage.py runserver
	
