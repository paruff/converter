"""Tests for main module."""

from pathlib import Path
from unittest.mock import Mock, patch

from converter.main import convert_file


class TestConvertFile:
    """Tests for convert_file function."""

    @patch("converter.main.probe")
    @patch("converter.main.encode")
    @patch("converter.main.ORIG_DIR")
    @patch("subprocess.run")
    def test_convert_file_h264(
        self, mock_subprocess, mock_orig_dir, mock_encode, mock_probe
    ):
        """Test converting H.264 file (repair via H.264-in-AVI)."""
        # Setup mocks
        mock_probe.return_value = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "bit_rate": "2000000",
                    "height": 720,
                    "r_frame_rate": "30/1",
                }
            ],
            "format": {},
        }
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_orig_dir.mkdir = Mock()

        input_path = Path("/test/video.mp4")

        with patch.object(Path, "rename"):
            convert_file(input_path)

        # Verify encode was called
        mock_encode.assert_called_once()
        args = mock_encode.call_args[0]
        # Bitrate: 2000000 * 1.7 (high fps) / 1000 = 3400 kbps
        assert args[2] == 3400

    @patch("converter.main.probe")
    @patch("converter.main.encode")
    @patch("converter.main.ORIG_DIR")
    @patch("subprocess.run")
    def test_convert_file_mpeg1(
        self, mock_subprocess, mock_orig_dir, mock_encode, mock_probe
    ):
        """Test converting MPEG-1 file (needs repair)."""
        # Setup mocks
        mock_probe.return_value = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "mpeg1video",
                    "bit_rate": "1200000",
                    "height": 480,
                    "r_frame_rate": "30/1",
                    "color_space": "bt470bg",
                }
            ],
            "format": {},
        }
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        mock_orig_dir.mkdir = Mock()

        input_path = Path("/test/video.mpg")

        with patch.object(Path, "rename"):
            convert_file(input_path)

        # Verify repair was called (subprocess should be called for ffmpeg)
        assert mock_subprocess.called

        # Verify encode was called
        mock_encode.assert_called_once()
        # Bitrate: 1200000 * 1.2 (SD) / 1000 = 1440 kbps
        args = mock_encode.call_args[0]
        assert args[2] == 1440

    @patch("converter.main.probe")
    @patch("converter.main.encode")
    @patch("converter.main.ORIG_DIR")
    def test_convert_file_no_bitrate(self, mock_orig_dir, mock_encode, mock_probe):
        """Test converting file with missing bitrate (fallback strategy)."""
        # Setup mocks
        mock_probe.return_value = {
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "vp9",
                    "height": 720,
                    "r_frame_rate": "25/1",
                }
            ],
            "format": {},
        }
        mock_orig_dir.mkdir = Mock()

        input_path = Path("/test/video.mkv")

        with patch.object(Path, "rename"):
            convert_file(input_path)

        # Verify encode was called
        mock_encode.assert_called_once()
        args = mock_encode.call_args[0]
        # Fallback bitrate for 720p: 1200000 * 2.5 = 3000000
        # Scale: 1.5 (medium)
        # Final: 3000000 * 1.5 / 1000 = 4500 kbps
        assert args[2] == 4500
