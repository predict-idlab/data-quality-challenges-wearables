.DEFAULT_GOAL := all
isort = isort code_utils
black = black code_utils

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: lint-pythoni
lint-python:
	ruff code_utils --ignore=E501
	$(isort) --check-only --df
	$(black) --check --diff


.PHONY: lint
lint: lint-python

.PHONY: mypy
mypy:
	mypy code_utils


.PHONY: all
all: lint mypy test

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '*.cpython-*' `
	rm -rf dist
	rm -rf build
	rm -rf target
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -rf .ruff*
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build