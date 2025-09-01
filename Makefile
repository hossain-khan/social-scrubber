.PHONY: help install install-dev run clean test lint format check-env setup pre-commit

# Default target
help:
	@echo "Available commands:"
	@echo "  setup        - Set up the development environment"
	@echo "  install      - Install the package and dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  run          - Run the social scrubber"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  pre-commit   - Run all pre-commit quality checks"
	@echo "  clean        - Clean up build artifacts"
	@echo "  check-env    - Check if .env file exists"

# Set up development environment
setup:
	@echo "Setting up Social Scrubber development environment..."
	python -m venv .venv
	@echo ""
	@echo "Virtual environment created! Activate it with:"
	@echo "  source .venv/bin/activate  (macOS/Linux)"
	@echo "  .venv\\Scripts\\activate     (Windows)"
	@echo ""
	@echo "Then run: make install"

# Install package and dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

# Install development dependencies
install-dev:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .
	@echo "💡 Consider installing pre-commit hooks: pre-commit install"

# Run the application
run: check-env
	social-scrubber

# Check if .env file exists
check-env:
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found!"; \
		echo "Please create .env file from template:"; \
		echo "  cp .env.example .env"; \
		echo "Then edit .env with your credentials."; \
		exit 1; \
	fi

# Run tests
test:
	pytest tests/ -v

# Run linting
lint:
	flake8 social_scrubber/ tests/ examples/
	mypy social_scrubber/ --ignore-missing-imports --no-strict-optional
	bandit -r social_scrubber/ --quiet

# Format code
format:
	black social_scrubber/ tests/ examples/
	isort social_scrubber/ tests/ examples/

# Run pre-commit quality checks
pre-commit:
	@if [ -f scripts/pre-commit-checks.sh ]; then \
		chmod +x scripts/pre-commit-checks.sh; \
		./scripts/pre-commit-checks.sh; \
	else \
		echo "❌ scripts/pre-commit-checks.sh not found"; \
		exit 1; \
	fi

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
