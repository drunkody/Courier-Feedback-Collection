.PHONY: help test test-unit test-integration test-offline test-jazz test-all test-cov test-fast lint format clean install-jazz dev

help:
	@echo "Available commands:"
	@echo " make dev            - Run development server"
	@echo " make test           - Run all tests"
	@echo " make test-unit      - Run unit tests only"
	@echo " make test-integration - Run integration tests"
	@echo " make test-offline   - Run offline mode tests"
	@echo " make test-jazz      - Run Jazz sync tests"
	@echo " make test-cov       - Run tests with coverage report"
	@echo " make test-fast      - Run tests in parallel"
	@echo " make lint           - Run linters"
	@echo " make format         - Format code"
	@echo " make clean          - Clean test artifacts"
	@echo " make install-jazz   - Install Jazz sync server"

dev:
	reflex run

test: test-all

test-unit:
	pytest tests/ -v -m unit --tb=short

test-integration:
	pytest tests/ -v -m integration --tb=short

test-offline:
	pytest tests/ -v -m offline --tb=short

test-jazz:
	pytest tests/ -v -m jazz --tb=short

test-all:
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-cov:
	pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "\n✅ Coverage report generated in htmlcov/index.html"

test-fast:
	pytest tests/ -v -n auto --tb=short

lint:
	@echo "Running flake8..."
	-flake8 app tests --max-line-length=127 --exclude=__pycache__,*.pyc,.git,__init__.py
	@echo "\nRunning bandit..."
	-bandit -r app -ll
	@echo "\n✅ Linting complete"

format:
	@echo "Formatting with black..."
	black app tests
	@echo "Sorting imports with isort..."
	isort app tests
	@echo "\n✅ Formatting complete"

clean:
	@echo "Cleaning test artifacts..."
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

install-jazz:
	@echo "Installing Jazz sync server..."
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed. Aborting." >&2; exit 1; }
	npm install -g @jazz-tools/sync-server
	@echo "✅ Jazz sync server installed"
	@echo "Run with: jazz-sync-server --port 4000"

# Additional helpful targets
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

db-reset:
	rm -f reflx.db
	reflex db migrate
