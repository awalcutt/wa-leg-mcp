.PHONY: all check release lint test format clean build quick-build validate-dist install

all: check

check: lint test

release: check build validate-dist

lint:
	black --check .
	ruff check .

format:
	black .
	ruff check --fix .

test:
	pytest --cov --cov-fail-under=90

build: clean
	python -m build

validate-dist: build
	python -m twine check dist/*

quick-build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	pip install -e ".[dev]"