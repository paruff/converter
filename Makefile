.PHONY: help install install-dev test lint format type-check check clean build docker-build docker-run

help:
	@echo "Media Converter - Makefile Commands"
	@echo "===================================="
	@echo "install          - Install package"
	@echo "install-dev      - Install package with dev dependencies"
	@echo "test             - Run tests with coverage"
	@echo "lint             - Run ruff linter"
	@echo "format           - Format code with black"
	@echo "type-check       - Run mypy type checking"
	@echo "check            - Run all checks (lint, type-check, test)"
	@echo "clean            - Remove build artifacts and cache"
	@echo "build            - Build distribution packages"
	@echo "docker-build     - Build Docker image"
	@echo "docker-run       - Run Docker container"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

lint:
	ruff check .

format:
	black .

type-check:
	mypy *.py --exclude tests

check: lint type-check test
	@echo "All checks passed!"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf tmp_fix/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build: clean
	python -m build

docker-build:
	docker build -t media-converter:latest .

docker-run:
	docker run -it --rm -v $(PWD)/media:/media media-converter:latest
