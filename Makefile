.PHONY: help install install-dev lint test test-coverage clean format benchmark e2e regression update-golden

help:
	@echo "Available targets:"
	@echo "  install       - Install package"
	@echo "  install-dev    - Install package with dev dependencies"
	@echo "  lint          - Run linters"
	@echo "  test          - Run tests"
	@echo "  test-coverage - Run tests with coverage"
	@echo "  format        - Format code"
	@echo "  clean         - Clean build artifacts"
	@echo "  benchmark     - Run performance benchmarks"
	@echo "  e2e           - Run end-to-end structure tests"
	@echo "  regression    - Run regression tests"
	@echo "  update-golden - Update golden DOCX files for regression tests"

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

benchmark:
	pytest benchmarks/ --benchmark-only --benchmark-sort=mean

e2e:
	pytest tests/e2e/ -v

regression:
	pytest tests/regression/ -v

update-golden:
	pytest tests/regression/ --update-golden
