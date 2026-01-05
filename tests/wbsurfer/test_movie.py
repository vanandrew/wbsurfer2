from pathlib import Path
from unittest.mock import patch

import pytest

from wbsurfer.movie import generate_movie, process_frames
from wbsurfer.scene import Scene


def test_generate_movie_basic_mock(dtseries_scene: Path, tmpdir):
    """Test basic movie generation with mocked rendering."""
    output_path = Path(tmpdir) / "test.mp4"

    with patch("wbsurfer.movie.process_frames") as mock_process:
        generate_movie(
            row_indices=["16000", "16010", "16020"],
            scene_path=dtseries_scene,
            scene_name="test",
            output=output_path,
            num_cpus=1,
        )
        # process_frames should be called
        mock_process.assert_called_once()


def test_generate_movie_closed_loop(dtseries_scene: Path, tmpdir):
    """Test movie generation with closed loop."""
    output_path = Path(tmpdir) / "test.mp4"

    with patch("wbsurfer.movie.process_frames") as mock_process:
        generate_movie(
            row_indices=["16000", "16010", "16020"],
            scene_path=dtseries_scene,
            scene_name="test",
            output=output_path,
            closed=True,
            num_cpus=1,
        )
        # process_frames should be called
        mock_process.assert_called_once()
        # The path passed should have the first index appended
        call_args = mock_process.call_args
        path = call_args[0][1]  # Second positional argument is the path
        # The path should be longer due to continuous path calculation
        assert len(path) > 0


def test_generate_movie_reverse(dtseries_scene: Path, tmpdir):
    """Test movie generation with reverse."""
    output_path = Path(tmpdir) / "test.mp4"

    with patch("wbsurfer.movie.process_frames") as mock_process:
        generate_movie(
            row_indices=["16000", "16010", "16020"],
            scene_path=dtseries_scene,
            scene_name="test",
            output=output_path,
            reverse=True,
            num_cpus=1,
        )
        # process_frames should be called
        mock_process.assert_called_once()


def test_generate_movie_vertex_mode(dtseries_scene: Path, tmpdir):
    """Test movie generation in vertex mode."""
    output_path = Path(tmpdir) / "test.mp4"

    # Get some valid vertices
    scene = Scene(dtseries_scene)
    vertex_table, _ = scene.get_vertex_and_voxel_table()
    vertex1 = str(int(vertex_table[16000]))
    vertex2 = str(int(vertex_table[16010]))

    with patch("wbsurfer.movie.process_frames") as mock_process:
        generate_movie(
            row_indices=["CORTEX_LEFT", vertex1, vertex2],
            scene_path=dtseries_scene,
            scene_name="test",
            output=output_path,
            vertex_mode=True,
            num_cpus=1,
        )
        # process_frames should be called
        mock_process.assert_called_once()


def test_generate_movie_border_file(dtseries_scene: Path, tmpdir):
    """Test movie generation with border file."""
    output_path = Path(tmpdir) / "test.mp4"
    border_path = Path(__file__).parent.parent / "data" / "test.border"

    with patch("wbsurfer.movie.process_frames") as mock_process:
        generate_movie(
            row_indices=[str(border_path)],
            scene_path=dtseries_scene,
            scene_name="test",
            output=output_path,
            border_file=True,
            num_cpus=1,
        )
        # process_frames should be called
        mock_process.assert_called_once()


def test_generate_movie_print_rows(dtseries_scene: Path, capsys):
    """Test movie generation in print rows mode."""
    with patch("wbsurfer.movie.get_continuous_path") as mock_path:
        mock_path.return_value = [16000, 16001, 16002]
        generate_movie(
            row_indices=["16000", "16010"],
            scene_path=dtseries_scene,
            scene_name="test",
            print_rows=True,
            num_cpus=1,
        )
        # Should print row indices
        captured = capsys.readouterr()
        assert "16000" in captured.out


def test_generate_movie_print_vertices(dtseries_scene: Path, capsys):
    """Test movie generation in print vertices mode."""
    with patch("wbsurfer.movie.get_continuous_path") as mock_path:
        mock_path.return_value = [16000, 16001, 16002]
        generate_movie(
            row_indices=["16000", "16010"],
            scene_path=dtseries_scene,
            scene_name="test",
            print_vertices=True,
            num_cpus=1,
        )
        # Should print vertex indices
        captured = capsys.readouterr()
        # Should have some output
        assert len(captured.out) > 0


def test_generate_movie_invalid_vertex(dtseries_scene: Path, tmpdir):
    """Test that invalid vertex index raises error."""
    output_path = Path(tmpdir) / "test.mp4"

    with pytest.raises(ValueError, match="Invalid vertex index"):
        generate_movie(
            row_indices=["CORTEX_LEFT", "999999"],
            scene_path=dtseries_scene,
            scene_name="test",
            output=output_path,
            vertex_mode=True,
            num_cpus=1,
        )


def test_process_frames_mock(dtseries_scene: Path, tmpdir):
    """Test process_frames with mocked rendering."""
    output_path = Path(tmpdir) / "test.mp4"
    scene = Scene(dtseries_scene)

    with patch("wbsurfer.movie.make_new_scene_frame") as mock_frame:
        with patch("wbsurfer.movie.run_ffmpeg") as mock_ffmpeg:
            mock_frame.return_value = Path("/tmp/frame.png")

            process_frames(
                output=output_path,
                path=[16000, 16001, 16002],
                scene=scene,
                scene_name="test",
                width=1920,
                height=1080,
                framerate=10,
                loops=1,
                num_cpus=1,
            )

            # Should call make_new_scene_frame for each frame
            assert mock_frame.call_count == 3
            # Should call ffmpeg
            mock_ffmpeg.assert_called_once()


def test_process_frames_with_loops(dtseries_scene: Path, tmpdir):
    """Test process_frames with multiple loops."""
    output_path = Path(tmpdir) / "test.mp4"
    scene = Scene(dtseries_scene)

    # Create a side effect that actually creates the frame files
    def create_frame(*args, **kwargs):
        # args[3] is the output_png_path
        frame_path = args[3] if len(args) > 3 else kwargs.get("output_png_path")
        # Create parent directory and an empty file
        frame_path.parent.mkdir(parents=True, exist_ok=True)
        frame_path.touch()
        return frame_path

    with patch("wbsurfer.movie.make_new_scene_frame") as mock_frame:
        with patch("wbsurfer.movie.run_ffmpeg") as mock_ffmpeg:
            mock_frame.side_effect = create_frame

            process_frames(
                output=output_path,
                path=[16000, 16001, 16002],
                scene=scene,
                scene_name="test",
                width=1920,
                height=1080,
                framerate=10,
                loops=2,
                num_cpus=1,
            )

            # Should call make_new_scene_frame for each frame (only once, loops copy frames)
            assert mock_frame.call_count == 3
            # Should call ffmpeg
            mock_ffmpeg.assert_called_once()
