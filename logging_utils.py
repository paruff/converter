from pathlib import Path

def write_log(path: Path, text: str):
    path.write_text(text, encoding="utf-8")
