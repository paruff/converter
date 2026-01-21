def classify_video(stream: dict) -> str:
    codec = stream.get("codec_name")
    if codec == "mpeg4":
        return "xvid"
    if codec == "h264":
        return "h264"
    if codec == "mpeg1video":
        return "mpeg1"
    if codec == "mpeg2video":
        return "mpeg2"
    if codec == "wmv3":
        return "wmv"
    return "other"
