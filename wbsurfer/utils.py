import logging
import os
from pathlib import Path
from subprocess import CalledProcessError, run

from .logging import run_process
from .scene import Scene

logger = logging.getLogger(__name__)


def find_command(command: str, env_var: str | None = None) -> Path:
    """Find location of an executable.

    Parameters
    ----------
    command : str
        The command to find.
    env_var : str, optional
        An environment variable to check for the command, by default None.

    Returns
    -------
    str
        The full path to the command.
    """
    command_path = None
    if env_var is not None:
        command_path = os.getenv(env_var, None)
    if command_path is None:
        # try automatically finding command from shell
        try:
            output = run(f"command -v {command}", shell=True, capture_output=True, text=True, check=True)
            command_path = str(Path(output.stdout.strip()).resolve())
        except CalledProcessError as e:
            raise FileNotFoundError(
                f"`{command}` not found in PATH. "
                f"Please set `{env_var}` environment variable or add `{command}` to your PATH."
            ) from e
    return Path(command_path).resolve()


WB_COMMAND = str(find_command("wb_command", "WBCOMMAND_BINARY_PATH"))
FFMPEG_COMMAND = str(find_command("ffmpeg", "FFMPEG_BINARY_PATH"))


def run_ffmpeg(in_images: str, output: Path | str, framerate: int) -> None:
    """Run ffmpeg to generate a movie from a list of images.

    Parameters
    ----------
    in_images : str
        Format string for input images.
    output : Path | str
        Path to the output movie.
    framerate : int
        The framerate of the output movie.
    """
    run_process(
        [
            "ffmpeg",
            "-hide_banner",
            "-y",
            "-r",
            str(framerate),
            "-start_number",
            "0",
            "-i",
            in_images,
            "-c:v",
            "libx264",
            "-r",
            str(framerate),
            "-pix_fmt",
            "yuv420p",
            str(output),
        ],
    )


def run_wb_command(scene_path: Path | str, scene_name: str, output_path: Path | str, width: int, height: int) -> None:
    """Run wb_command with a command and arguments.

    Parameters
    ----------
    scene_path : Path | str
        The scene file to use.
    scene_name : str
        The name of the scene in the scene file.
    output_path : Path | str
        The output png file path.
    width : int
        The width of the output image.
    height : int
        The height of the output image.
    """
    run_process(
        [
            WB_COMMAND,
            "-scene-capture-image",
            str(scene_path),
            scene_name,
            str(output_path),
            "-size-width-height",
            str(width),
            str(height),
        ],
        {"OMP_NUM_THREADS": "1"},
        suppress_output=True,
    )


def make_new_scene_frame(
    scene_path: Path | str,
    scene_name: str,
    output_scene_path: Path | str,
    output_png_path: Path | str,
    width: int,
    height: int,
    row_index: int,
) -> Path:
    """Make a new scene frame.

    Parameters
    ----------
    scene_path : Path | str
        The scene file to use.
    scene_name : str
        The name of the scene in the scene file.
    output_scene_path : Path | str
        The output scene file path.
    output_png_path : Path | str
        The output png file path.
    width : int
        The width of the output image.
    height : int
        The height of the output image.
    row_index : int
        The row index to use.

    Returns
    -------
    Path
        The output png file path.
    """
    # set paths
    output_scene_path = Path(output_scene_path)
    output_png_path = Path(output_png_path)
    # load the scene
    new_scene = Scene(scene_path, scene_name)
    # change the active row
    new_scene.change_connectivity_active_row(row_index)
    # save the scene
    new_scene.save(output_scene_path)
    # render scene to png
    run_wb_command(output_scene_path, scene_name, output_png_path, width, height)
    return output_png_path
