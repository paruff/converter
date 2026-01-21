import logging
from pathlib import Path

from .logging_utils import run_subprocess


def encode(path: Path, target: Path, bitrate_kbps: int, dry_run: bool = False) -> None:
    """Encode video file to H.264/AAC MKV.
    
    Args:
        path: Input video path
        target: Output video path
        bitrate_kbps: Target bitrate in kbps
        dry_run: If True, skip actual encoding
    """
    logger = logging.getLogger("converter")
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would encode {path} to {target} at {bitrate_kbps}kbps")
        return
    
    # Try VideoToolbox first
    logger.info(f"Encoding {path.name} to {target.name} at {bitrate_kbps}kbps")
    result = run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            f"{bitrate_kbps}k",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(target),
        ],
        logger=logger,
    )

    if result.success:
        logger.info(f"Successfully encoded with VideoToolbox")
        return

    # Fallback to libx264
    logger.warning(f"VideoToolbox failed, falling back to libx264")
    result = run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-b:v",
            f"{bitrate_kbps}k",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(target),
        ],
        logger=logger,
        check=True,  # Raise exception if fallback also fails
    )
    
    logger.info(f"Successfully encoded with libx264")
