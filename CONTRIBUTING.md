# Contributing to Social Scrubber

Thank you for your interest in contributing to Social Scrubber! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/social-scrubber.git
   cd social-scrubber
   ```

3. Set up the development environment:
   ```bash
   make setup
   source .venv/bin/activate  # macOS/Linux
   make install-dev
   ```

4. Create a `.env` file for testing:
   ```bash
   cp .env.example .env
   # Add your test credentials (use test accounts!)
   ```

## Development Workflow

1. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards
3. Run tests and ensure they pass:
   ```bash
   make test
   ```

4. Format your code:
   ```bash
   make format
   ```

5. Run linting:
   ```bash
   make lint
   ```

6. Commit your changes with a descriptive message
7. Push to your fork and create a pull request

## Coding Standards

- Follow PEP 8 for Python code style
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Add tests for new functionality
- Keep functions focused and single-purpose
- Use async/await for I/O operations

## Testing

- Write unit tests for new functionality
- Use pytest for testing
- Mock external API calls in tests
- Aim for at least 80% test coverage
- Test both success and error scenarios

## Adding New Platforms

To add support for a new social media platform:

1. Create a new file in `social_scrubber/platforms/` (e.g., `newplatform.py`)
2. Implement the `BasePlatform` interface:
   - `authenticate()`: Handle platform authentication
   - `get_posts()`: Retrieve posts within date range
   - `delete_post()`: Delete a single post
3. Add configuration to `config.py`
4. Update the main CLI to include the new platform
5. Add tests for the new platform
6. Update documentation

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include examples in the `examples/` directory
- Update this CONTRIBUTING.md for development changes

## Submitting Issues

When submitting bug reports or feature requests:

1. Check existing issues to avoid duplicates
2. Use the provided issue templates
3. Include relevant details:
   - Python version
   - Operating system
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Log output (sanitize any credentials!)

## Security Considerations

- Never commit real credentials to the repository
- Use test accounts for development and testing
- Be mindful of rate limits when testing API integrations
- Sanitize logs and error messages to remove sensitive data

## Code Review Process

1. All changes must be submitted via pull request
2. PRs require at least one review from a maintainer
3. Automated tests must pass
4. Code coverage must not decrease significantly
5. Documentation must be updated for user-facing changes

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Questions?

If you have questions about contributing, feel free to open an issue with the "question" label.
