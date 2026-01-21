from pathlib import Path
from ffprobe_utils import probe
from file_classifier import classify_video
from smart_mode import smart_scale
from repair import repair_mpeg, repair_wmv, repair_xvid
from encode import encode
from config import ORIG_DIR, DEFAULT_SD_BITRATE

def get_bitrate(info: dict) -> int:
    br = info["video"].get("bit_rate")
    if not br:
        return DEFAULT_SD_BITRATE
    return int(br)

def convert_file(path: Path):
    info = probe(path)
    if not info:
        print(f"Cannot read {path}")
        return

    video_stream = next(s for s in info["streams"] if s["codec_type"] == "video")
    codec = classify_video(video_stream)

    scale = smart_scale({"video": video_stream})
    bitrate = get_bitrate({"video": video_stream})
    target_kbps = int((bitrate / 1000) * scale)

    # Repair pipeline
    if codec == "mpeg1":
        repaired = repair_mpeg(path)
    elif codec == "wmv":
        repaired = repair_wmv(path)
    elif codec == "xvid":
        repaired = repair_xvid(path)
    else:
        repaired = path

    out = path.with_suffix(".mkv")
    encode(repaired, out, target_kbps)

    # Move original
    ORIG_DIR.mkdir(exist_ok=True)
    path.rename(ORIG_DIR / path.name)

def convert_directory(root: Path):
    for path in root.iterdir():
        if path.suffix.lower() in {".avi", ".mpg", ".mpeg", ".wmv", ".mov"}:
            convert_file(path)

if __name__ == "__main__":
    import sys
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    convert_directory(root)
