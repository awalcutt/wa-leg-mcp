# Contributing to wa-leg-mcp

First off, thank you for considering contributing to wa-leg-mcp! This project aims to make Washington State Legislature data more accessible through AI assistants.

## Quick Start

1. Fork the repository
2. Clone your fork and set up your development environment:
   ```bash
   git clone https://github.com/YOUR-USERNAME/wa-leg-mcp.git
   cd wa-leg-mcp
   make install
   ```
3. Make your changes
4. Ensure your code is properly formatted and passes all tests:
   ```bash
   make format  # Format code with black and ruff
   make lint    # Check code style
   make test    # Run tests with coverage
   ```
5. Submit a pull request

## Development Environment

The package uses a standard Python development setup:

- Python 3.10+ is required
- All development dependencies are specified in the `[dev]` extra
- Use `black` and `ruff` for code formatting and linting

## Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate
2. Update the version number in `src/wa_leg_mcp/__version__.py` following [Semantic Versioning](https://semver.org/)
3. Make sure all tests pass and code is properly formatted
4. The pull request will be merged once reviewed

## Code Style

This project follows standard Python code style practices:

- Use Black for code formatting
- Follow PEP 8 naming conventions
- Write docstrings for all public functions, classes, and modules

## Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in the GitHub issues
2. If not, create a new issue with:
   - A clear title and description
   - As much relevant information as possible
   - A code sample or test case demonstrating the issue if possible

## Contact

For questions or discussions about the project, please open an issue in the GitHub repository.

---

This project is maintained by Alex Adacutt and is licensed under the MIT License.
