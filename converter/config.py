import os
from pathlib import Path

ROOT = Path.cwd()
LOG_DIR = ROOT / "logs"
TMP_DIR = ROOT / "tmp_fix"
ORIG_DIR = ROOT / "originals"

DEFAULT_SD_BITRATE = 1_200_000  # 1200 kbps

# Parallel encoding settings
MAX_WORKERS = int(os.environ.get("CONVERTER_MAX_WORKERS", "4"))  # Default to 4 workers
