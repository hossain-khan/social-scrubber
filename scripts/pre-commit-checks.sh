#!/bin/bash

# Pre-commit quality checks script for Social Scrubber
# Run this before committing to ensure CI will pass

set -e  # Exit on any error

echo "🔍 Running pre-commit quality checks for Social Scrubber..."

# Ensure we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️ No virtual environment detected. Run 'source .venv/bin/activate' first."
    exit 1
fi

echo
echo "1️⃣ Code Formatting (Black)..."
black --check --diff social_scrubber/ tests/ examples/
echo "✅ Black formatting passed"

echo
echo "2️⃣ Import Sorting (isort)..."
isort --check-only --diff social_scrubber/ tests/ examples/
echo "✅ Import sorting passed"

echo
echo "3️⃣ Type Checking (mypy)..."
mypy social_scrubber/ --ignore-missing-imports --no-strict-optional
echo "✅ Type checking passed"

echo
echo "4️⃣ Linting (flake8)..."
flake8 social_scrubber/ tests/ examples/ --count --statistics
echo "✅ Linting passed"

echo
echo "5️⃣ Security Check (bandit)..."
bandit -r social_scrubber/ -f json --quiet || echo "⚠️ Security warnings found (non-blocking)"
echo "✅ Security check completed"

echo
echo "6️⃣ All Tests (pytest)..."
python -m pytest tests/ --tb=short -v
echo "✅ All tests passed"

echo
echo "7️⃣ Package Build Test..."
python setup.py check
echo "✅ Package build check passed"

echo
echo "🎉 All quality checks passed! Ready for commit and push."
echo "💡 Tip: CI will run the same checks plus additional security scans."
