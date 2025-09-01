# Copilot Instructions for Social Scrubber

This project is a Python CLI tool for bulk-deleting social media posts from Twitter, Mastodon, and Bluesky platforms.

## Project Structure & Architecture

We use a modular platform-based architecture where each social media platform has its own dedicated module in `social_scrubber/platforms/`. All platforms inherit from a common `BasePlatform` class that defines the standard interface for post deletion operations.

We organize code into these main modules: `cli.py` for command-line interface, `config.py` for configuration management, `utils.py` for shared utilities, and platform-specific modules in the `platforms/` directory.


## Development Workflow

### Feature Development and Bug Fixes
For ANY new features, bug fixes, or changes:

1. **Create a new branch first**: Always create a feature branch before making changes
   ```bash
   git checkout -b feature/your-feature-name
   # OR
   git checkout -b fix/bug-description
   ```

2. **Use the pre-commit script**: Before committing and pushing, ALWAYS run the quality checks script:
   ```bash
   ./scripts/pre-commit-checks.sh
   ```
   This script runs all required quality checks (Black, isort, mypy, flake8, pytest, JSON validation) and ensures CI will pass.

3. **Commit and push**: Only commit and push after the pre-commit script passes
   ```bash
   git add .
   git commit -m "descriptive commit message"
   git push -u origin your-branch-name
   ```

4. **Create Pull Request**: Create a PR for code review and CI validation before merging to main

### Branch Naming Convention
- **Features**: `feature/feature-name` (e.g., `feature/add-twitter-support`)
- **Bug Fixes**: `fix/bug-description` (e.g., `fix/image-attachment-blob-reference`)
- **Documentation**: `docs/description` (e.g., `docs/update-readme`)
- **Refactoring**: `refactor/description` (e.g., `refactor/extract-content-processor`)

## Code Quality Requirements

Before committing any code changes, you MUST run the pre-commit quality checks:

**Recommended**: Use the automated script for all quality checks:
```bash
./scripts/pre-commit-checks.sh
```

**Manual alternative** - run these formatting and validation steps in order:

1. **Format code with Black**: Always run `black .` to ensure proper code formatting across all files
2. **Sort imports with isort**: Always run `isort .` to maintain consistent import ordering across all files
3. **Type check with mypy**: Run `mypy src/ tests/` to catch type annotation issues
4. **Lint with flake8**: Run `flake8 src/ tests/ *.py` to check code quality and style including root directory files
5. **Run tests**: Run `python -m pytest tests/` to ensure all unit tests pass
6. **Validate JSON files**: Run `python -m json.tool sync_state.json > /dev/null` to validate JSON syntax
7. **Update CHANGELOG.md**: Document any new features, bug fixes, or breaking changes in the changelog

## Changelog Management

Always update `docs/CHANGELOG.md` when making changes:

- **New Features**: Add to the `[Unreleased]` section under `### Added`
- **Bug Fixes**: Add to the `[Unreleased]` section under `### Fixed`
- **Breaking Changes**: Add to the `[Unreleased]` section under `### Changed`
- **Deprecations**: Add to the `[Unreleased]` section under `### Deprecated`
- **Removals**: Add to the `[Unreleased]` section under `### Removed`
- **Security Updates**: Add to the `[Unreleased]` section under `### Security`

Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format for consistency.


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
