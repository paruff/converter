import logging
from typing import Any


class SmartMode:
    """Smart Mode bitrate scaling with SD/HD heuristics and codec-aware adjustments.

    Provides methods for:
    - Bitrate scaling based on video properties
    - SD/HD classification heuristics
    - Codec-aware adjustments
    """

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initialize SmartMode.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger("converter")

    def is_sd(self, height: int, color_space: str = "") -> bool:
        """Determine if video is SD quality.

        Args:
            height: Video height in pixels
            color_space: Color space identifier

        Returns:
            True if video is SD quality
        """
        return color_space == "bt470bg" or height <= 480

    def calculate_scale_factor(
        self, height: int, fps: float, color_space: str = ""
    ) -> float:
        """Calculate bitrate scale factor based on video properties.

        Args:
            height: Video height in pixels
            fps: Frames per second
            color_space: Color space identifier

        Returns:
            Scale factor to apply to base bitrate
        """
        if self.is_sd(height, color_space):
            return 1.2
        if fps < 25:
            return 1.3
        if fps >= 29.5:
            return 1.7
        return 1.5

    def get_codec_adjustment(self, codec_name: str) -> float:
        """Get codec-specific bitrate adjustment factor.

        Args:
            codec_name: Codec name (e.g., 'h264', 'mpeg1video')

        Returns:
            Adjustment factor (1.0 = no adjustment)
        """
        # Future enhancement: codec-specific adjustments
        # For now, return neutral adjustment
        return 1.0

    def scale_bitrate(
        self, video_stream: dict[str, Any], base_bitrate: int
    ) -> int:
        """Scale bitrate using smart mode heuristics.

        Args:
            video_stream: Video stream metadata from ffprobe
            base_bitrate: Base bitrate in bits per second

        Returns:
            Scaled bitrate in bits per second
        """
        height = video_stream.get("height", 480)
        fps = video_stream.get("r_frame_rate", "30/1")
        
        # Parse fps from fraction format (e.g., "30000/1001")
        if isinstance(fps, str) and "/" in fps:
            num, denom = fps.split("/")
            fps_float = float(num) / float(denom)
        else:
            fps_float = float(fps)
        
        color_space = video_stream.get("color_space", "")
        codec_name = video_stream.get("codec_name", "")

        scale_factor = self.calculate_scale_factor(height, fps_float, color_space)
        codec_adjustment = self.get_codec_adjustment(codec_name)
        
        final_scale = scale_factor * codec_adjustment
        scaled_bitrate = int(base_bitrate * final_scale)
        
        self.logger.debug(
            f"Smart Mode: height={height}px, fps={fps_float:.2f}, "
            f"scale={scale_factor:.1f}, codec_adj={codec_adjustment:.1f}, "
            f"final_scale={final_scale:.2f}"
        )
        
        return scaled_bitrate


# Backward compatibility: maintain the original function interface
def smart_scale(info: dict) -> float:
    """Legacy function for backward compatibility.

    Args:
        info: Dictionary with 'video' key containing stream metadata

    Returns:
        Scale factor to apply to base bitrate
    """
    video = info["video"]
    height = video.get("height", 480)
    fps = video.get("fps", 30.0)
    color_space = video.get("color_space", "")
    
    sm = SmartMode()
    return sm.calculate_scale_factor(height, fps, color_space)
