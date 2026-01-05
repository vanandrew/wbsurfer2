import sys
from pathlib import Path
from unittest.mock import patch

import pytest


def test_cli_basic_args(dtseries_scene: Path, tmpdir):
    """Test CLI with basic arguments."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()


def test_cli_version(capsys):
    """Test CLI --version flag."""
    test_args = ["wb_surfer2", "--version"]

    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            from wbsurfer.cli import main

            main()

    captured = capsys.readouterr()
    # Should print version information
    assert "wb_surfer2" in captured.out or "wbsurfer" in captured.out


def test_cli_width_height(dtseries_scene: Path, tmpdir):
    """Test CLI with custom width and height."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "--width",
        "800",
        "--height",
        "600",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["width"] == 800
            assert call_kwargs["height"] == 600


def test_cli_framerate(dtseries_scene: Path, tmpdir):
    """Test CLI with custom framerate."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "-r",
        "30",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["framerate"] == 30


def test_cli_closed_loop(dtseries_scene: Path, tmpdir):
    """Test CLI with --closed flag."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "--closed",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["closed"] is True


def test_cli_reverse(dtseries_scene: Path, tmpdir):
    """Test CLI with --reverse flag."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "--reverse",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["reverse"] is True


def test_cli_loops(dtseries_scene: Path, tmpdir):
    """Test CLI with --loops flag."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "-l",
        "3",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["loops"] == 3


def test_cli_print_vertices(dtseries_scene: Path):
    """Test CLI with --print-vertices flag."""
    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "--print-vertices",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["print_vertices"] is True


def test_cli_print_rows(dtseries_scene: Path):
    """Test CLI with --print-rows flag."""
    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "--print-rows",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["print_rows"] is True


def test_cli_vertex_mode(dtseries_scene: Path, tmpdir):
    """Test CLI with --vertex-mode flag."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "--vertex-mode",
        "CORTEX_LEFT",
        "100",
        "200",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["vertex_mode"] is True


def test_cli_border_file(dtseries_scene: Path, tmpdir):
    """Test CLI with --border-file flag."""
    output_path = Path(tmpdir) / "test.mp4"
    border_path = Path(__file__).parent.parent / "data" / "test.border"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "--border-file",
        str(border_path),
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["border_file"] is True


def test_cli_num_cpus(dtseries_scene: Path, tmpdir):
    """Test CLI with --num-cpus flag."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "--num-cpus",
        "4",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with patch("wbsurfer.cli.generate_movie") as mock_gen:
            from wbsurfer.cli import main

            main()
            mock_gen.assert_called_once()
            call_kwargs = mock_gen.call_args[1]
            assert call_kwargs["num_cpus"] == 4


def test_cli_insufficient_row_indices(dtseries_scene: Path, tmpdir):
    """Test CLI with insufficient row indices."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "16000",  # Only one index
    ]

    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            from wbsurfer.cli import main

            main()


def test_cli_no_border_file_specified(dtseries_scene: Path, tmpdir):
    """Test CLI with --border-file but no file specified."""
    output_path = Path(tmpdir) / "test.mp4"

    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "-o",
        str(output_path),
        "--border-file",
    ]

    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            from wbsurfer.cli import main

            main()


def test_cli_no_output_without_print_mode(dtseries_scene: Path):
    """Test CLI without output and without print mode."""
    test_args = [
        "wb_surfer2",
        "-s",
        str(dtseries_scene),
        "-n",
        "connectivity",
        "16000",
        "16010",
    ]

    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            from wbsurfer.cli import main

            main()
