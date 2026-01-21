import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional

def probe(path: Path) -> Optional[Dict[str, Any]]:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_streams", "-show_format", str(path)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)
