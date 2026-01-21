"""Tests for subprocess wrapper functionality."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from converter.logging_utils import SubprocessResult, run_subprocess


class TestSubprocessResult:
    """Tests for SubprocessResult class."""

    def test_success_property(self):
        """Test success property."""
        result = SubprocessResult(
            returncode=0,
            stdout="output",
            stderr="",
            command=["echo", "test"]
        )
        assert result.success is True

    def test_failure_property(self):
        """Test failure property."""
        result = SubprocessResult(
            returncode=1,
            stdout="",
            stderr="error",
            command=["false"]
        )
        assert result.success is False

    def test_exception_property(self):
        """Test exception in result."""
        result = SubprocessResult(
            returncode=-1,
            stdout="",
            stderr="",
            command=["test"],
            exception=Exception("test error")
        )
        assert result.success is False

    def test_command_str(self):
        """Test command string representation."""
        result = SubprocessResult(
            returncode=0,
            stdout="",
            stderr="",
            command=["echo", "hello", "world"]
        )
        assert result.command_str == "echo hello world"


class TestRunSubprocess:
    """Tests for run_subprocess function."""

    def test_successful_command(self):
        """Test successful command execution."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result = run_subprocess(["echo", "test"])

        assert result.success is True
        assert result.returncode == 0
        assert result.stdout == "output"

    def test_failed_command(self):
        """Test failed command execution."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"

        with patch("subprocess.run", return_value=mock_result):
            result = run_subprocess(["false"])

        assert result.success is False
        assert result.returncode == 1
        assert result.stderr == "error"

    def test_dry_run_mode(self):
        """Test dry run mode."""
        with patch("subprocess.run") as mock_run:
            result = run_subprocess(["echo", "test"], dry_run=True)

        mock_run.assert_not_called()
        assert result.success is True
        assert result.returncode == 0

    def test_path_conversion(self):
        """Test Path objects are converted to strings."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = run_subprocess([Path("/test/path"), "arg"])

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert all(isinstance(arg, str) for arg in args)

    def test_check_raises_on_failure(self):
        """Test check parameter raises on failure."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(subprocess.CalledProcessError):
                run_subprocess(["false"], check=True)

    def test_exception_handling(self):
        """Test exception handling."""
        with patch("subprocess.run", side_effect=Exception("test error")):
            result = run_subprocess(["test"])

        assert result.success is False
        assert result.exception is not None
