.EXPORT_ALL_VARIABLES:

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

FULLNAME=${PROJECT_NAME}-${PROJECT_VERSION}
PACKAGE_NAME=${FULLNAME}-py3-none-any.whl

default: isset-PROJECT_NAME
	@echo "Tasks in \033[1;32m${PROJECT_NAME}\033[0m:"
	@cat Makefile

isset-%:
	@if [ -z '${${*}}' ]; then echo 'ERROR: variable$ * not set' && exit 1; fi

dev:
	# install the package in development mode
	python -m pip install --upgrade pip
	pip install -e .[dev]

lint: dev
	# run pylint
	python linter.py

test: dev
	# run tests and modules separately to avoid circular imports
	pytest tests/ -vv --cov=. --cov-report=html --cov-report=term-missing --junitxml=junit/coverage-results.xml

build: clean
	# build package
	python -m pip install --upgrade pip
	pip install build wheel
	python setup.py bdist_wheel

clean:
	# clean all latex auxiliary files, build and test compiled files
	@rm -rf docs/*.aux docs/*.fdb_latexmk docs/*.fls docs/*.log docs/*.out docs/*.toc docs/*synctex.gz docs/*.gz
	@rm -rf .pytest_cache/ */.pytest_cache/ .mypy_cache/ junit/ build/ dist/ htmlcov/ .coverage
	@find . -not -path './.venv*' -path '*/__pycache__*' -delete
	@find . -not -path './.venv*' -path '*/*.egg-info*' -delete
