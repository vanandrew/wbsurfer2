import os
from pathlib import Path
from unittest.mock import patch

import pytest

from wbsurfer.utils import (
    find_command,
    make_new_scene_frame,
    run_ffmpeg,
    run_wb_command,
)


def test_find_command_from_path():
    """Test finding a command from PATH."""
    # Test with a command that should always exist
    python_path = find_command("python3")
    assert python_path.exists()
    assert "python" in str(python_path).lower()


def test_find_command_from_env_var():
    """Test finding a command from environment variable."""
    with patch.dict(os.environ, {"TEST_COMMAND_PATH": "/usr/bin/test"}):
        result = find_command("test", "TEST_COMMAND_PATH")
        assert result == Path("/usr/bin/test")


def test_find_command_not_found():
    """Test that finding a non-existent command raises error."""
    with pytest.raises(FileNotFoundError, match="not found in PATH"):
        find_command("nonexistent_command_xyz123", "NONEXISTENT_ENV_VAR")


def test_run_ffmpeg_mock():
    """Test run_ffmpeg with mocked process."""
    with patch("wbsurfer.utils.run_process") as mock_run:
        mock_run.return_value = 0
        run_ffmpeg("input%09d.png", "/tmp/output.mp4", 10)
        # Verify run_process was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ffmpeg" in args
        assert "10" in args
        assert "input%09d.png" in args


def test_run_ffmpeg_failure():
    """Test that run_ffmpeg raises error on failure."""
    with patch("wbsurfer.utils.run_process") as mock_run:
        mock_run.return_value = 1  # Failure
        with pytest.raises(RuntimeError, match="ffmpeg failed"):
            run_ffmpeg("input%09d.png", "/tmp/output.mp4", 10)


def test_run_wb_command_mock():
    """Test run_wb_command with mocked process."""
    with patch("wbsurfer.utils.run_process") as mock_run:
        mock_run.return_value = 0
        run_wb_command("/tmp/scene.scene", "test_scene", "/tmp/output.png", 1920, 1080)
        # Verify run_process was called
        mock_run.assert_called_once()
        # Get the first positional argument (the command list)
        args = mock_run.call_args[0][0]
        assert "-scene-capture-image" in args
        assert "/tmp/scene.scene" in args
        assert "test_scene" in args
        assert "/tmp/output.png" in args
        assert "1920" in args
        assert "1080" in args


def test_run_wb_command_failure():
    """Test that run_wb_command raises error on failure."""
    with patch("wbsurfer.utils.run_process") as mock_run:
        mock_run.return_value = 1  # Failure
        with pytest.raises(RuntimeError, match="Failed to render scene"):
            run_wb_command(
                "/tmp/scene.scene", "test_scene", "/tmp/output.png", 1920, 1080
            )


def test_run_wb_command_with_logging():
    """Test run_wb_command with logging enabled."""
    # Need to reload the module to pick up the environment variable
    import importlib
    import wbsurfer.utils

    with patch.dict(os.environ, {"EXTERNAL_COMMAND_LOG": "1"}):
        # Reload the module to pick up the new env var
        importlib.reload(wbsurfer.utils)
        with patch("wbsurfer.utils.run_process") as mock_run:
            with patch("wbsurfer.utils.setup_logging") as mock_setup:
                mock_run.return_value = 0
                wbsurfer.utils.run_wb_command(
                    "/tmp/scene.scene", "test_scene", "/tmp/output.png", 1920, 1080
                )
                # setup_logging should be called
                mock_setup.assert_called_once()
        # Reload again to reset
        importlib.reload(wbsurfer.utils)


def test_make_new_scene_frame_mock(tmpdir):
    """Test make_new_scene_frame with mocked Scene and wb_command."""
    dtseries_scene_path = Path(__file__).parent.parent / "data" / "dtseries.scene"
    output_scene_path = Path(tmpdir) / "output.scene"
    output_png_path = Path(tmpdir) / "output.png"

    with patch("wbsurfer.utils.run_wb_command") as mock_wb:
        result = make_new_scene_frame(
            dtseries_scene_path,
            "test",
            output_scene_path,
            output_png_path,
            1920,
            1080,
            100,
        )

        # Should return the output png path
        assert result == output_png_path
        # Scene file should be created
        assert output_scene_path.exists()
        # wb_command should have been called
        mock_wb.assert_called_once()
