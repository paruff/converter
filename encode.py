import subprocess
from pathlib import Path

def encode(path: Path, target: Path, bitrate_kbps: int):
    # Try VideoToolbox first
    result = subprocess.run([
        "ffmpeg", "-i", str(path),
        "-c:v", "h264_videotoolbox", "-b:v", f"{bitrate_kbps}k",
        "-c:a", "aac", "-b:a", "192k",
        str(target)
    ])

    if result.returncode == 0:
        return

    # Fallback to libx264
    subprocess.run([
        "ffmpeg", "-i", str(path),
        "-c:v", "libx264", "-preset", "veryfast",
        "-b:v", f"{bitrate_kbps}k",
        "-c:a", "aac", "-b:a", "192k",
        str(target)
    ])
