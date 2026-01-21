import json
import subprocess
from pathlib import Path
from typing import Any


def probe(path: Path) -> dict[str, Any] | None:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_streams",
            "-show_format",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    data: dict[str, Any] = json.loads(result.stdout)
    return data
