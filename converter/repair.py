import logging
from pathlib import Path

from .config import TMP_DIR
from .logging_utils import run_subprocess


def repair_mpeg(path: Path, dry_run: bool = False) -> Path:
    """Repair MPEG-1 video stream.

    Args:
        path: Input video path
        dry_run: If True, skip actual repair

    Returns:
        Path to repaired file
    """
    logger = logging.getLogger("converter")
    out = TMP_DIR / (path.stem + "_fixed.mkv")

    if dry_run:
        logger.info(f"[DRY-RUN] Would repair MPEG-1: {path} -> {out}")
        return out

    logger.info(f"Repairing MPEG-1: {path.name}")
    TMP_DIR.mkdir(exist_ok=True)

    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-fflags",
            "+genpts",
            "-err_detect",
            "ignore_err",
            "-i",
            str(path),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            str(out),
        ],
        logger=logger,
        check=True,
    )

    logger.info(f"MPEG-1 repair complete: {out.name}")
    return out


def repair_wmv(path: Path, dry_run: bool = False) -> Path:
    """Repair WMV video stream.

    Args:
        path: Input video path
        dry_run: If True, skip actual repair

    Returns:
        Path to repaired file
    """
    logger = logging.getLogger("converter")
    out = TMP_DIR / (path.stem + "_fixed.mkv")

    if dry_run:
        logger.info(f"[DRY-RUN] Would repair WMV: {path} -> {out}")
        return out

    logger.info(f"Repairing WMV: {path.name}")
    TMP_DIR.mkdir(exist_ok=True)

    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-fflags",
            "+genpts",
            "-err_detect",
            "ignore_err",
            "-i",
            str(path),
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            str(out),
        ],
        logger=logger,
        check=True,
    )

    logger.info(f"WMV repair complete: {out.name}")
    return out


def repair_xvid(path: Path, dry_run: bool = False) -> Path:
    """Repair XviD video stream.

    Args:
        path: Input video path
        dry_run: If True, skip actual repair

    Returns:
        Path to repaired file
    """
    logger = logging.getLogger("converter")
    out = TMP_DIR / (path.stem + "_fixed.avi")

    if dry_run:
        logger.info(f"[DRY-RUN] Would repair XviD: {path} -> {out}")
        return out

    logger.info(f"Repairing XviD: {path.name}")
    TMP_DIR.mkdir(exist_ok=True)

    run_subprocess(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(path),
            "-c",
            "copy",
            "-bsf:v",
            "mpeg4_unpack_bframes",
            str(out),
        ],
        logger=logger,
        check=True,
    )

    logger.info(f"XviD repair complete: {out.name}")
    return out
