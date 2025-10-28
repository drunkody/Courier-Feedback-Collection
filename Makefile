.PHONY: help test test-unit test-integration test-offline test-all test-cov test-fast lint format clean

help:
	@echo "Available commands:"
	@echo " make test           - Run all tests"
	@echo " make test-unit      - Run unit tests only"
	@echo " make test-integration - Run integration tests"
	@echo " make test-offline   - Run offline mode tests"
	@echo " make test-cov       - Run tests with coverage report"
	@echo " make test-fast      - Run tests in parallel"
	@echo " make lint           - Run linters"
	@echo " make format         - Format code"
	@echo " make clean          - Clean test artifacts"

test:
	pytest tests/ -v

test-unit:
	pytest tests/ -v -m unit

test-integration:
	pytest tests/ -v -m integration

test-offline:
	pytest tests/ -v -m offline

test-all:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-cov:
	pytest tests/ --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

test-fast:
	pytest tests/ -v -n auto

lint:
	flake8 app tests
	mypy app
	bandit -r app

format:
	black app tests
	isort app tests

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
