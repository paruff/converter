"""Tests for encode module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from encode import encode


class TestEncode:
    """Tests for encode function."""
    
    def test_encode_videotoolbox_success(self):
        """Test successful encode with VideoToolbox."""
        input_path = Path("/test/input.mkv")
        output_path = Path("/test/output.mkv")
        
        mock_result = Mock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            encode(input_path, output_path, 2000)
        
        # Should call ffmpeg once with VideoToolbox
        assert mock_run.call_count == 1
        args = mock_run.call_args[0][0]
        assert "h264_videotoolbox" in args
        assert "2000k" in args
    
    def test_encode_fallback_to_libx264(self):
        """Test fallback to libx264 when VideoToolbox fails."""
        input_path = Path("/test/input.mkv")
        output_path = Path("/test/output.mkv")
        
        # First call fails, second succeeds
        mock_results = [Mock(returncode=1), Mock(returncode=0)]
        
        with patch('subprocess.run', side_effect=mock_results) as mock_run:
            encode(input_path, output_path, 2000)
        
        # Should call ffmpeg twice
        assert mock_run.call_count == 2
        
        # Second call should use libx264
        args = mock_run.call_args[0][0]
        assert "libx264" in args
        assert "2000k" in args
