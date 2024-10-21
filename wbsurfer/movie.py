"""Movie generation functions."""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from subprocess import CalledProcessError, run
from tempfile import TemporaryDirectory

from wbsurfer.geodesic import get_continuous_path
from wbsurfer.logging import run_process
from wbsurfer.scene import Scene

logger = logging.getLogger(__name__)


def find_wb_command() -> str:
    """Find the wb_command executable."""
    wb_command = os.getenv("WBSURFER_WBCOMMAND", None)
    if wb_command is None:
        # try automatically finding wb_command from shell
        try:
            output = run("which wb_command", shell=True, capture_output=True, text=True, check=True)
            wb_command = str(Path(output.stdout.strip()).resolve())
        except CalledProcessError as e:
            raise FileNotFoundError(
                "wb_command not found in PATH. "
                "Please set WBSURFER_WBCOMMAND environment variable or add wb_command to your PATH."
            ) from e
    return wb_command


WB_COMMAND = find_wb_command()


def generate_movie(
    path: list[int],
    scene_path: Path | str,
    scene_name: str,
    output: Path | str,
    width: int = 1920,
    height: int = 1080,
    framerate: int = 10,
    num_cpus: int = 1,
):
    """Generate a movie from a list of row indices.

    Parameters
    ----------
    path : list[int]
        The list of row indices to generate the movie from.
    scene_path : Path | str
        The scene file to use.
    scene_name : str
        The name of the scene in the scene file.
    output : Path | str
        The output file path.
    width : int, optional
        The width of the output movie, by default 1920.
    height : int, optional
        The height of the output movie, by default 1080.
    framerate : int, optional
        The framerate of the output movie, by default 10.
    num_cpus : int, optional
        The number of CPUs to use for processing, by default 1.
    """
    # convert to Path objects
    scene_path = Path(scene_path)
    output = Path(output)

    # load scene
    scene = Scene(scene_path, scene_name)

    # first compute the continuous path
    continuous_path = get_continuous_path(path, scene)
    logger.info(f"Processing Row Indices: {continuous_path}")

    # generate new scenes for each point on path
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        # create new scene
        new_scene = Scene(scene_path, scene_name)
        with ThreadPoolExecutor(max_workers=num_cpus) as executor:
            futures = []
            scenes_path = tmp_path / "scenes"
            scenes_path.mkdir(parents=True, exist_ok=True)
            frames_path = tmp_path / "frames"
            frames_path.mkdir(parents=True, exist_ok=True)
            for idx, point in enumerate(continuous_path):
                # set the current point
                new_scene.change_connectivity_active_row(point)
                # save the scene
                new_scene.save(scenes_path / f"frame{idx:09d}.scene")
                logger.info(f"Processing Frame: {idx}")
                futures.append(
                    executor.submit(
                        run_process,
                        [
                            WB_COMMAND,
                            "-show-scene",
                            str(scenes_path / f"frame{idx:09d}.scene"),
                            scene_name,
                            str(frames_path / f"frame{idx:09d}.png"),
                            str(width),
                            str(height),
                        ],
                        {"OMP_NUM_THREADS": "1"},
                        suppress_output=True,
                    )
                )
            logger.info("Waiting for workbench rendering to complete...")
            for future in futures:
                future.result()
            logger.info("Workbench rendering complete.")
            logger.info("Generating movie...")
            in_images = str(Path(frames_path) / "frame%09d.png")
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

        # print output
        logger.info(f"Movie saved to: {output}")
