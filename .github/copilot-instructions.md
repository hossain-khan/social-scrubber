# Copilot Instructions for Social Scrubber

This project is a Python CLI tool for bulk-deleting social media posts from Twitter, Mastodon, and Bluesky platforms.

## Project Structure & Architecture

We use a modular platform-based architecture where each social media platform has its own dedicated module in `social_scrubber/platforms/`. All platforms inherit from a common `BasePlatform` class that defines the standard interface for post deletion operations.

We organize code into these main modules: `cli.py` for command-line interface, `config.py` for configuration management, `utils.py` for shared utilities, and platform-specific modules in the `platforms/` directory.

## Code Style & Standards

We follow strict Python code quality standards enforced by our CI/CD pipeline. Use Black for code formatting with line length 88, isort for import sorting with Black-compatible profile, flake8 for linting with complexity limit of 10, mypy for type checking with gradual typing approach, and bandit for security scanning.

All new code should include proper type hints using Python 3.9+ syntax. We prefer explicit typing over implicit, especially for function parameters and return values.

## Dependencies & Package Management

We use standard pip with requirements.txt for runtime dependencies and requirements-dev.txt for development dependencies. The project supports Python 3.9+ and we maintain compatibility across all supported versions.

For API integrations, we use tweepy for Twitter API, Mastodon.py for Mastodon API, and atproto for Bluesky AT Protocol. All API clients should be properly configured and authenticated before use.

## Configuration Management

We use Pydantic models for configuration validation and environment-based configuration with python-dotenv. Configuration files are stored in the user's home directory under `.social_scrubber/` by default.

All sensitive information like API keys and tokens should be stored in environment variables or secure configuration files, never hardcoded in source code.

## Error Handling & Logging

We use Python's built-in logging module with rich console output for better user experience. All platform operations should have proper error handling with meaningful error messages that help users understand what went wrong.

Rate limiting and API quota management are handled gracefully with appropriate retry mechanisms and user feedback about delays.

## Testing & Quality Assurance

We use pytest for all testing with async test support for API operations. Tests should mock external API calls to avoid dependencies on live services during CI/CD runs.

All new features should include comprehensive tests covering both success and failure scenarios. We maintain test coverage reporting through Codecov integration.

## Development Workflow

We use pre-commit hooks for automated quality checks before commits. Developers should run `make pre-commit` before submitting changes to ensure all quality gates pass locally.

The CI/CD pipeline runs on every PR and includes multi-platform testing, code quality checks, security scanning, and package build verification.

## Platform-Specific Guidelines

When adding support for new social media platforms, create a new module in `social_scrubber/platforms/` that inherits from `BasePlatform` and implements all required methods including authentication, post fetching, and deletion operations.

Each platform should handle its own rate limiting, error recovery, and API-specific quirks while maintaining a consistent interface for the CLI.

## Security Considerations

We scan all dependencies weekly for security vulnerabilities using bandit and safety tools. When handling user credentials, always use secure storage mechanisms and provide clear warnings about data sensitivity.

All API operations should use HTTPS and proper authentication headers. We never log or store user passwords or sensitive authentication tokens in plain text.
