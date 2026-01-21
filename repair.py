import subprocess
from pathlib import Path
from config import TMP_DIR

def repair_mpeg(path: Path) -> Path:
    out = TMP_DIR / (path.stem + "_fixed.mkv")
    subprocess.run([
        "ffmpeg", "-fflags", "+genpts", "-err_detect", "ignore_err",
        "-i", str(path),
        "-c:v", "copy", "-c:a", "copy",
        str(out)
    ])
    return out

def repair_wmv(path: Path) -> Path:
    out = TMP_DIR / (path.stem + "_fixed.mkv")
    subprocess.run([
        "ffmpeg", "-fflags", "+genpts", "-err_detect", "ignore_err",
        "-i", str(path),
        "-c:v", "copy", "-c:a", "copy",
        str(out)
    ])
    return out

def repair_xvid(path: Path) -> Path:
    out = TMP_DIR / (path.stem + "_fixed.avi")
    subprocess.run([
        "ffmpeg", "-i", str(path),
        "-c", "copy",
        "-bsf:v", "mpeg4_unpack_bframes",
        str(out)
    ])
    return out
