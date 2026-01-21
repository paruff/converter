def smart_scale(info: dict) -> float:
    video = info["video"]
    height = video["height"]
    fps = video["fps"]
    chroma = video.get("color_space", "")

    if chroma == "bt470bg" or height <= 480:
        return 1.2
    if fps < 25:
        return 1.3
    if fps >= 29.5:
        return 1.7
    return 1.5
