"""Tests for main module."""

from pathlib import Path
from unittest.mock import Mock, patch

from converter.main import convert_file, get_bitrate


class TestGetBitrate:
    """Tests for get_bitrate function."""

    def test_get_bitrate_with_value(self):
        """Test getting bitrate when value is present."""
        info = {"video": {"bit_rate": "5000000"}}
        assert get_bitrate(info) == 5000000

    def test_get_bitrate_without_value(self):
        """Test getting bitrate when value is missing."""
        info = {"video": {}}
        from config import DEFAULT_SD_BITRATE

        assert get_bitrate(info) == DEFAULT_SD_BITRATE

    def test_get_bitrate_none_value(self):
        """Test getting bitrate when value is None."""
        info = {"video": {"bit_rate": None}}
        from config import DEFAULT_SD_BITRATE

        assert get_bitrate(info) == DEFAULT_SD_BITRATE


class TestConvertFile:
    """Tests for convert_file function."""

    @patch("main.probe")
    @patch("main.classify_video")
    @patch("main.smart_scale")
    @patch("main.encode")
    @patch("main.ORIG_DIR")
    def test_convert_file_h264(
        self, mock_orig_dir, mock_encode, mock_scale, mock_classify, mock_probe
    ):
        """Test converting H.264 file (no repair needed)."""
        # Setup mocks
        mock_probe.return_value = {
            "streams": [{"codec_type": "video", "codec_name": "h264", "bit_rate": "2000000"}]
        }
        mock_classify.return_value = "h264"
        mock_scale.return_value = 1.5
        mock_orig_dir.mkdir = Mock()

        input_path = Path("/test/video.mp4")

        with patch.object(Path, "rename"):
            convert_file(input_path)

        # Verify encode was called
        mock_encode.assert_called_once()
        args = mock_encode.call_args[0]
        assert args[0] == input_path  # No repair for h264
        assert args[2] == 3000  # 2000k * 1.5

    @patch("main.probe")
    @patch("main.classify_video")
    @patch("main.smart_scale")
    @patch("main.repair_mpeg")
    @patch("main.encode")
    @patch("main.ORIG_DIR")
    def test_convert_file_mpeg1(
        self, mock_orig_dir, mock_encode, mock_repair, mock_scale, mock_classify, mock_probe
    ):
        """Test converting MPEG-1 file (needs repair)."""
        # Setup mocks
        mock_probe.return_value = {
            "streams": [{"codec_type": "video", "codec_name": "mpeg1video", "bit_rate": "1200000"}]
        }
        mock_classify.return_value = "mpeg1"
        mock_scale.return_value = 1.2
        mock_repair.return_value = Path("/tmp/repaired.mkv")
        mock_orig_dir.mkdir = Mock()

        input_path = Path("/test/video.mpg")

        with patch.object(Path, "rename"):
            convert_file(input_path)

        # Verify repair was called
        mock_repair.assert_called_once_with(input_path)

        # Verify encode was called with repaired file
        mock_encode.assert_called_once()
        args = mock_encode.call_args[0]
        assert args[0] == Path("/tmp/repaired.mkv")
