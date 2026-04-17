.PHONY: help install install-dev lint test test-coverage clean format

help:
	@echo "Available targets:"
	@echo "  install       - Install package"
	@echo "  install-dev    - Install package with dev dependencies"
	@echo "  lint          - Run linters"
	@echo "  test          - Run tests"
	@echo "  test-coverage - Run tests with coverage"
	@echo "  format        - Format code"
	@echo "  clean         - Clean build artifacts"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,math]"

lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff format src/ tests/

test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=src/typst_gost_docx --cov-report=html

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .mypy_cache/ .coverage htmlcov/
