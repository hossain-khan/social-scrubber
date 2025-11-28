# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **GitHub Actions CI/CD pipeline** with comprehensive quality checks
- **Pre-commit hooks** configuration for local development  
- **Development scripts** for quality assurance (`scripts/pre-commit-checks.sh`)
- **Modern Python project configuration** (`pyproject.toml`)
- **Automated dependency updates** workflow
- **Release automation** workflow for PyPI publishing
- **New test file** `test_utils.py` with comprehensive tests for utility functions
- **New tests for BasePlatform** including `bulk_delete_posts` and `_archive_post` methods
- **New tests for TwitterConfig** validation
- **New tests for ScrubConfig** edge cases (invalid dates, start_date='today')
- **Shared test fixtures** in `conftest.py` for consistent test setup across files
- **New test file** `test_mastodon.py` with comprehensive tests for Mastodon platform
- **New test file** `test_twitter.py` with tests for Twitter platform (WIP implementation)
- **New test file** `test_cli_methods.py` with tests for SocialScrubber CLI methods
- **New tests for Bluesky** authenticate and delete_post methods
- Twitter/X platform integration (planned)
- Support for filtering posts by keywords or post IDs
- Support for batch operations with progress bars
- Configuration profiles for different deletion strategies

### Changed
- **Improved timezone handling** using `dateutil.parser` for robust datetime parsing
- **Enhanced import organization** - moved all imports to top of files
- **Better test environment handling** using pytest monkeypatch fixtures
- **Enhanced error handling** for datetime parsing failures
- **Reduced test code duplication** in CLI platform filtering tests using shared context managers
- **Improved test comments** to accurately describe what each test validates
- **Refactored test fixtures** - moved shared fixtures to conftest.py to reduce duplication

### Fixed
- **Import statement organization** following Python conventions
- **Timezone conversion issues** in Bluesky and Mastodon platforms
- **Test environment variable cleanup** using proper pytest fixtures
- **Datetime parsing robustness** with better error handling
- **Removed misleading noqa comments** in test files

## [0.1.0] - 2025-08-31

### Added
- Initial release of Social Scrubber
- **Bluesky platform support** - Full authentication, post retrieval, and deletion
- **Mastodon platform support** - Full authentication, post retrieval, and deletion
- **Interactive CLI interface** with rich formatting and user-friendly prompts
- **Dry-run mode** enabled by default for safe testing
- **Post archival system** - Automatically archives posts as JSON before deletion
- **Date range filtering** - Delete posts within specific time periods
- **Configurable post limits** - Limit number of posts processed per run
- **Environment-based configuration** - Secure credential management via .env files
- **Cross-platform support** - Works on Windows, macOS, and Linux
- **Comprehensive logging** - Detailed logs with configurable levels
- **Safety confirmations** - User prompts before destructive operations
- **Rich CLI output** - Tables, progress indicators, and colored output
- **Development tooling**:
  - Makefile for common development tasks
  - pytest test suite with async support
  - Code formatting with black
  - Linting with flake8
  - Type checking support
- **Documentation**:
  - Comprehensive README with setup instructions
  - Contributing guidelines
  - Example usage scripts
  - API documentation via docstrings
- **Project structure**:
  - Modular platform architecture for easy extension
  - Base platform interface for consistent implementation
  - Utility functions for common operations
  - Separate configuration management
  - Test suite with unit and integration tests

### Security
- **Credential protection** - Environment variables for sensitive data
- **No hardcoded secrets** - Template-based configuration
- **Safe defaults** - Dry-run mode enabled by default
- **Archive functionality** - Posts backed up before deletion
- **Rate limiting respect** - Follows platform API guidelines
