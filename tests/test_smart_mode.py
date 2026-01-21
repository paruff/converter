"""Tests for smart_mode module."""

from smart_mode import smart_scale


class TestSmartScale:
    """Tests for smart_scale function."""

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
