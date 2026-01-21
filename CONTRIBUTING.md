# Contributing to Media Converter

Thank you for your interest in contributing to Media Converter! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/converter.git
   cd converter
   ```

2. **Install development dependencies**
   ```bash
   make install-dev
   # or
   pip install -r requirements.txt
   ```

3. **Create a branch for your changes**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We follow strict code quality standards:

- **Black** for code formatting (100 character line length)
- **Ruff** for linting
- **Mypy** for type checking

Run all checks before submitting:
```bash
make check
```

Or individually:
```bash
make format    # Format code with black
make lint      # Run ruff linter
make type-check # Run mypy type checking
```

### Testing

All new features must include tests:

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_your_module.py -v

# Run with coverage
pytest tests/ --cov --cov-report=html
```

**Requirements:**
- Maintain or improve test coverage (currently 61%)
- All tests must pass before merging
- Use mocks for external dependencies (ffmpeg, ffprobe)

### Type Hints

All functions must have complete type hints:

```python
from pathlib import Path
from typing import Optional

def convert_file(
    path: Path,
    output_dir: Optional[Path] = None,
    keep_original: bool = False
) -> bool:
    """Convert a video file.
    
    Args:
        path: Path to the video file
        output_dir: Optional output directory
        keep_original: Whether to keep the original file
        
    Returns:
        True if successful, False otherwise
    """
    ...
```

### Commit Messages

Follow conventional commit format:

```
type(scope): short description

Longer description if needed

- Bullet points for details
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

Examples:
- `feat(repair): add support for AV1 codec`
- `fix(encode): handle missing audio stream gracefully`
- `docs(readme): update installation instructions`
- `test(smart_mode): add tests for 4K content`

## Architecture Guidelines

### Module Responsibilities

- **ffprobe_utils.py**: FFprobe JSON parsing only
- **file_classifier.py**: Codec detection and classification
- **smart_mode.py**: Bitrate scaling logic
- **repair.py**: Video repair pipelines
- **encode.py**: Encoding with hardware/software fallback
- **cli.py**: Command-line interface
- **gui.py**: Graphical interface
- **config.py**: Configuration constants

### Design Principles

1. **Use Pathlib** instead of string paths
2. **Parse JSON** from ffprobe, never stderr
3. **Modular functions** with single responsibility
4. **Type hints everywhere**
5. **Fail gracefully** with meaningful error messages
6. **Provide fallbacks** for hardware encoding

### Adding New Features

#### New Codec Support

1. Update `file_classifier.py` to detect the codec
2. Add repair pipeline in `repair.py` if needed
3. Update tests in `tests/test_file_classifier.py`
4. Update documentation

#### New Encoding Option

1. Add function to `encode.py`
2. Update CLI arguments in `cli.py`
3. Add GUI controls in `gui.py`
4. Add tests
5. Update README

## Pull Request Process

1. **Update tests** for your changes
2. **Run all checks**: `make check`
3. **Update documentation** (README, docstrings)
4. **Create Pull Request** with clear description
5. **Respond to review** feedback

### PR Checklist

- [ ] Tests pass locally (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)
- [ ] No merge conflicts

## Questions or Problems?

- Open an issue for bugs or feature requests
- Use discussions for questions
- Check `.github/copilot-instructions.md` for AI-assisted development

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
