.PHONY: build

MODULE:=dtc


test:
	poetry run pytest -s

pdb:
	poetry run pytest --pdb

coverage:
	poetry run py.test  --cov $(MODULE) --cov-report term-missing

install: base_install tools

base_install:
	poetry env use 3.7
	poetry run python -m pip install -U pip
	poetry install

tools:
	poetry run python -m pip install ipdb ipython



push:
	git status
	git push origin --all
	git push origin --tags


clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name 'requirements*' -exec rm -f {} +
	rm -rf docs/_build/



clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -rf .pytest_cache/
	rm -rf .cache


style:
	poetry run reorder-python-imports dtc/__init__.py tests/test_*