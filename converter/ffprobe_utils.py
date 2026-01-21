import json
import logging
from pathlib import Path
from typing import Any

from .logging_utils import run_subprocess


def probe(path: Path, dry_run: bool = False) -> dict[str, Any] | None:
    """Probe a video file using ffprobe.
    
    Args:
        path: Path to video file
        dry_run: If True, skip actual probe
        
    Returns:
        Probe data as dict, or None on failure
    """
    logger = logging.getLogger("converter")
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would probe: {path}")
        # Return minimal mock data for dry-run with required fields
        return {
            "streams": [{
                "codec_type": "video", 
                "codec_name": "h264",
                "height": 480,
                "fps": 30.0,
                "bit_rate": "1200000",
            }],
            "format": {}
        }
    
    result = run_subprocess(
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
        logger=logger,
        capture_output=True
    )
    
    if not result.success:
        logger.error(f"Failed to probe {path}")
        return None
    
    try:
        data: dict[str, Any] = json.loads(result.stdout)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse ffprobe JSON: {e}")
        return None
