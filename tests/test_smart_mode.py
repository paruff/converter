"""Tests for smart_mode module."""

from converter.smart_mode import SmartMode, smart_scale


class TestSmartModeClass:
    """Tests for SmartMode class."""

    def test_is_sd_bt470bg(self):
        """Test SD detection with bt470bg color space."""
        sm = SmartMode()
        assert sm.is_sd(720, "bt470bg") is True

    def test_is_sd_low_height(self):
        """Test SD detection with low height."""
        sm = SmartMode()
        assert sm.is_sd(480, "") is True
        assert sm.is_sd(360, "") is True

    def test_is_not_sd(self):
        """Test HD detection."""
        sm = SmartMode()
        assert sm.is_sd(720, "") is False
        assert sm.is_sd(1080, "") is False

    def test_calculate_scale_factor_sd_bt470bg(self):
        """Test scale factor for SD video with bt470bg."""
        sm = SmartMode()
        assert sm.calculate_scale_factor(480, 29.97, "bt470bg") == 1.2

    def test_calculate_scale_factor_sd_low_height(self):
        """Test scale factor for SD video with low height."""
        sm = SmartMode()
        assert sm.calculate_scale_factor(360, 29.97, "") == 1.2

    def test_calculate_scale_factor_low_fps(self):
        """Test scale factor for low FPS video."""
        sm = SmartMode()
        assert sm.calculate_scale_factor(720, 24, "") == 1.3

    def test_calculate_scale_factor_high_fps(self):
        """Test scale factor for high FPS video."""
        sm = SmartMode()
        assert sm.calculate_scale_factor(1080, 30, "") == 1.7

    def test_calculate_scale_factor_medium(self):
        """Test scale factor for medium quality video."""
        sm = SmartMode()
        assert sm.calculate_scale_factor(720, 25, "") == 1.5

    def test_get_codec_adjustment(self):
        """Test codec adjustment (currently neutral)."""
        sm = SmartMode()
        assert sm.get_codec_adjustment("h264") == 1.0
        assert sm.get_codec_adjustment("mpeg1video") == 1.0

    def test_scale_bitrate_basic(self):
        """Test bitrate scaling with basic stream."""
        sm = SmartMode()
        stream = {
            "height": 480,
            "r_frame_rate": "30/1",
            "color_space": "bt470bg",
            "codec_name": "h264",
        }
        # 1200000 * 1.2 = 1440000
        assert sm.scale_bitrate(stream, 1_200_000) == 1_440_000

    def test_scale_bitrate_with_fraction_fps(self):
        """Test bitrate scaling with fractional FPS."""
        sm = SmartMode()
        stream = {
            "height": 1080,
            "r_frame_rate": "30000/1001",  # 29.97 fps
            "color_space": "",
            "codec_name": "h264",
        }
        # 1200000 * 1.7 = 2040000
        assert sm.scale_bitrate(stream, 1_200_000) == 2_040_000

    def test_scale_bitrate_with_defaults(self):
        """Test bitrate scaling with missing fields."""
        sm = SmartMode()
        stream = {}
        # Should use defaults: height=480, fps=30, color_space=""
        # Since height <= 480, scale = 1.2
        assert sm.scale_bitrate(stream, 1_200_000) == 1_440_000

    def test_get_bitrate_from_stream(self):
        """Test bitrate extraction from stream."""
        sm = SmartMode()
        stream = {"bit_rate": "2500000", "height": 720}
        assert sm.get_bitrate(stream) == 2_500_000

    def test_get_bitrate_from_format(self):
        """Test bitrate extraction from format when stream has none."""
        sm = SmartMode()
        stream = {"height": 720}
        format_info = {"bit_rate": "3000000"}
        assert sm.get_bitrate(stream, format_info) == 3_000_000

    def test_get_bitrate_fallback_sd(self):
        """Test fallback bitrate for SD resolution."""
        sm = SmartMode()
        stream = {"height": 480}
        # Should use DEFAULT_SD_BITRATE (1200000)
        assert sm.get_bitrate(stream) == 1_200_000

    def test_get_bitrate_fallback_hd(self):
        """Test fallback bitrate for HD resolution."""
        sm = SmartMode()
        stream = {"height": 720}
        # Should use DEFAULT_SD_BITRATE * 2.5 = 3000000
        assert sm.get_bitrate(stream) == 3_000_000

    def test_get_bitrate_fallback_full_hd(self):
        """Test fallback bitrate for Full HD resolution."""
        sm = SmartMode()
        stream = {"height": 1080}
        # Should use DEFAULT_SD_BITRATE * 5 = 6000000
        assert sm.get_bitrate(stream) == 6_000_000

    def test_get_bitrate_invalid_string(self):
        """Test fallback when bitrate string is invalid."""
        sm = SmartMode()
        stream = {"bit_rate": "invalid", "height": 480}
        # Should fallback to SD default
        assert sm.get_bitrate(stream) == 1_200_000


class TestSmartScaleLegacy:
    """Tests for legacy smart_scale function (backward compatibility)."""

    def test_scale_sd_bt470bg(self):
        """Test scaling for SD video with bt470bg color space."""
        info = {"video": {"height": 480, "fps": 29.97, "color_space": "bt470bg"}}
        assert smart_scale(info) == 1.2

    def test_scale_sd_low_height(self):
        """Test scaling for SD video with low height."""
        info = {"video": {"height": 360, "fps": 29.97, "color_space": ""}}
        assert smart_scale(info) == 1.2

    def test_scale_low_fps(self):
        """Test scaling for low FPS video."""
        info = {"video": {"height": 720, "fps": 24, "color_space": ""}}
        assert smart_scale(info) == 1.3

    def test_scale_high_fps(self):
        """Test scaling for high FPS video."""
        info = {"video": {"height": 1080, "fps": 30, "color_space": ""}}
        assert smart_scale(info) == 1.7

    def test_scale_medium(self):
        """Test scaling for medium quality video."""
        info = {"video": {"height": 720, "fps": 25, "color_space": ""}}
        assert smart_scale(info) == 1.5

    def test_scale_missing_color_space(self):
        """Test scaling with missing color space."""
        info = {"video": {"height": 720, "fps": 29.97}}
        assert smart_scale(info) == 1.7
