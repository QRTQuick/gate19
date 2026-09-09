.PHONY: install test lint format build publish clean doctor

install:
	pip install -e ".[dev]"

test:
	pytest -v --cov=gate19

lint:
	ruff check gate19 tests || true
	mypy gate19 || true

format:
	black gate19 tests
	isort gate19 tests
	ruff format gate19 tests || true

build:
	gate19 build

publish:
	gate19 publish

clean:
	gate19 clean --all
	rm -rf dist build *.egg-info

doctor:
	gate19 doctor

help:
	gate19 --help
