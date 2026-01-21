# Media Converter Engine (Python)

A robust, modular media conversion engine designed to repair, normalize, and encode legacy or corrupted video files for Plex and Samsung TV compatibility.

## Features
- Automatic codec detection (H.264, MPEG-1, MPEG-2, WMV3, XviD)
- Smart Mode dynamic bitrate scaling
- Pre-repair pipelines for:
  - MPEG-1 timestamp and GOP repair
  - WMV packet resync
  - XviD packed B-frame unpacking
- Hardware encoding (VideoToolbox) with libx264 fallback
- Clean directory structure:
  - `logs/`
  - `originals/`
  - `tmp_fix/`
- Extensible Python architecture
- GitHub Actions CI for linting, testing, and packaging

## Project Structure
converter/
main.py
ffprobe_utils.py
file_classifier.py
smart_mode.py
repair.py
encode.py
logging_utils.py
config.py


## Requirements
- Python 3.10+
- ffmpeg with ffprobe
- macOS (VideoToolbox support)

## Installation
pip install -r requirements.txt


## Usage
Convert a directory:
python -m converter.main  /path/to/media


## Development
This project uses:
- black (formatting)
- ruff (linting)
- mypy (type checking)
- pytest (testing)

Run all checks:
make check

## Contributing
See `.github/copilot-instructions.md` for AI-assisted development guidelines.
