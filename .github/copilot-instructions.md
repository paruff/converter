# GitHub Copilot Instructions for the Media Converter Project

## Project Purpose
This repository contains a Python-based media conversion engine designed to:
- Repair damaged or legacy video formats (MPEG-1, WMV, AVI/XviD)
- Normalize codecs and containers for Plex and Samsung TV compatibility
- Apply dynamic bitrate scaling (“Smart Mode”)
- Provide clean logs and predictable behavior
- Support future enhancements such as parallel encoding and queue management

## Copilot Behavior Guidelines
When generating code, Copilot should:
1. Prefer **modular, testable Python** over monolithic scripts.
2. Use **ffprobe JSON parsing**, never stderr parsing.
3. Follow the existing architecture:
   - `ffprobe_utils.py`
   - `file_classifier.py`
   - `smart_mode.py`
   - `repair.py`
   - `encode.py`
   - `main.py`
4. Use **type hints** everywhere.
5. Use **Pathlib** instead of string paths.
6. Avoid shell-specific hacks; prefer Python subprocess with lists.
7. Ensure all ffmpeg commands:
   - Fail gracefully
   - Provide meaningful error messages
   - Use fallback encoders when needed
8. When adding features, prefer:
   - Extensible classes
   - Dependency injection
   - Clear separation of concerns
9. When modifying Smart Mode:
   - Keep logic deterministic
   - Avoid magic numbers without comments
10. When adding repair pipelines
 - Never overwrite originals
 - - Always write to `tmp_fix/`
   - - Always return a valid Path

## Copilot Should Avoid 
- Generating monolithic scripts
- - Using `os.system`
- Using string-based command concatenation
- Adding features without docstrings
- Introducing global state unless in `config.py`
- Hardcoding paths
## Documentation Expectations Copilot should: 
- Generate docstrings for all public functions
- Update README when adding features
- Suggest improvements to architecture when appropriate

## Testing Expectations Copilot should: 
- Generate pytest-compatible tests
-  Mock subprocess calls where possible
- Validate ffprobe parsing logic
- Validate Smart Mode scaling logic

## Style Expectations 
- Follow PEP8
- Use `black` formatting
- Use `ruff` for linting
- Use `mypy` for type checking
