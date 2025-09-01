# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Twitter/X platform integration (planned)
- Support for filtering posts by keywords or post IDs
- Support for batch operations with progress bars
- Configuration profiles for different deletion strategies

### Changed

### Deprecated

### Removed

### Fixed

### Security

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
