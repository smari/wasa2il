
# NOTE: This is not the most perfect makefile.
# There's a few things we could do to improve performance.
# But since this is new, we can strive for clarity and simplicity here.
# Could use many of these suggestions:
# 	https://docs.cloudposse.com/reference/best-practices/make-best-practices/


# On _some_ systems, make might not default to bash, which might produce
# unexpected output/errors. It's assumed that all of the recipes here are written
# in bash syntax.
SHELL = /bin/bash
.SHELLFLAGS = -e -u -o pipefail -c


default: help


# TODO: Add more descriptions to makefile targets
.PHONY: help
help:
	@echo -e "\nThese are some useful commands to work with this project."
	@echo -e "Please refer to the README.md for more details.\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo -e "\nFor more information, please read the Makefile\n"


.env:
	@echo "Missing '.env' file. Creating one using 'env.example' as a template"
	@cp env.example .env
	@echo "Please open the '.env' file and adjust to your local setup!"
	@exit 1


.venv: .env  ## Creates a virtualenv at `./.venv`
	@python -m venv .venv


.PHONY: setup
setup: .env .venv requirements.txt.log requirements-mysql.txt.log requirements-postgresql.txt.log  ## Sets up the project (installs dependencies etc.)


requirements.txt.log: requirements.txt
	@. .venv/bin/activate && pip install -r requirements.txt | tee .requirements.txt.tmp.log
	@mv .requirements.txt.tmp.log requirements.txt.log

requirements-mysql.txt.log: .env requirements-mysql.txt
	@. .venv/bin/activate && (grep '^W2_DATABASE_ENGINE' .env | grep 'mysql' > /dev/null && pip install -r requirements-mysql.txt || echo "Not using MySQL") | tee .requirements-mysql.txt.tmp.log
	@mv .requirements-mysql.txt.tmp.log requirements-mysql.txt.log

requirements-postgresql.txt.log: .env requirements-postgresql.txt
	@. .venv/bin/activate && (grep '^W2_DATABASE_ENGINE' .env | grep 'postgresql' > /dev/null && pip install -r requirements-postgresql.txt || echo "Not using PostgreSQL") | tee .requirements-postgresql.txt.tmp.log
	@mv .requirements-postgresql.txt.tmp.log requirements-postgresql.txt.log


.PHONY: test
test: setup  ## Runs the unit tests
	@. .venv/bin/activate && ./manage.py test


.PHONY: migrate
migrate: setup  ## Runs the migrate Django management command
	@. .venv/bin/activate && ./manage.py migrate


.PHONY: load_fake_data
load_fake_data: setup  ## Loads up fake data using custom Django management command
	@. .venv/bin/activate && ./manage.py load_fake_data --full --reset

.PHONY: run
run: setup  ## Runs the Django development server
	@. .venv/bin/activate && ./manage.py runserver


.PHONY: clean
clean:  ## Removes cached python files and virtualenv
	@echo "Deleting '__pycache__/' directories"
	@find . -name "__pycache__" -exec rm -rf {} \+
	@echo "Deleting requirement log files"
	@rm requirements*.log 2>/dev/null || true
	@echo "Deleting the virtualenv ('./.venv/')"
	@rm -rf .venv 2>/dev/null || true


.PHONY: docker/build
docker/build:  ## Builds a Docker image and tags
	docker build -t wasa2il .

