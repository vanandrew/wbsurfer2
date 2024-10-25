"""Movie generation functions."""

import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory
from typing import cast

import numpy as np
from nibabel.cifti2.cifti2_axes import BrainModelAxis
from rich.progress import track

from wbsurfer.border import Border
from wbsurfer.geodesic import get_continuous_path
from wbsurfer.scene import Scene
from wbsurfer.utils import make_new_scene_frame, run_ffmpeg
from wbsurfer.volume import volume_interpolation

logger = logging.getLogger(__name__)


def process_frames(
    output: Path,
    path: list[int],
    scene: Scene,
    scene_name: str,
    width: int,
    height: int,
    framerate: int,
    loops: int,
    num_cpus: int,
):
    """Process frames for a path

    Parameters
    ----------
    output : Path
        The output file path.
    path : list[int]
        The path to process.
    scene : Scene
        The scene object.
    scene_name : str
        The name of the scene in the scene file.
    width : int
        The width of the frames.
    height : int
        The height of the frames.
    framerate : int
        The framerate of the movie.
    loops : int
        The number of loops to make.
    num_cpus : int
        The number of CPUs to use for processing.
    """
    # generate new scenes for each point on path
    logger.info(f"Processing Row Indices: {path}")
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        scenes_path = tmp_path / "scenes"
        scenes_path.mkdir(parents=True, exist_ok=True)
        frames_path = tmp_path / "frames"
        frames_path.mkdir(parents=True, exist_ok=True)
        with ProcessPoolExecutor(max_workers=num_cpus) as executor:
            if num_cpus == 1:
                map_func = map
            else:
                map_func = executor.map
            logger.info("Waiting for workbench rendering to complete...")
            list(
                track(
                    map_func(
                        make_new_scene_frame,
                        [scene.scene_path] * len(path),
                        [scene_name] * len(path),
                        [scenes_path / f"frame{idx:09d}.scene" for idx in range(len(path))],
                        [frames_path / f"frame{idx:09d}.png" for idx in range(len(path))],
                        [width] * len(path),
                        [height] * len(path),
                        path,
                    ),
                    description="Rendering frames...",
                    total=len(path),
                )
            )
            logger.info("Workbench rendering complete.")

        # loop the movie based on the number of loops set
        offset = 0
        for _ in range(loops - 1):
            offset += len(path)
            for idx in range(len(path)):
                new_frame = frames_path / f"frame{offset + idx:09d}.png"
                old_frame = frames_path / f"frame{idx:09d}.png"
                copyfile(old_frame, new_frame)

        # generate the movie
        logger.info("Generating movie...")
        in_images = str(Path(frames_path) / "frame%09d.png")
        run_ffmpeg(in_images, output, framerate)

        # print output
        logger.info(f"Movie saved to: {output}")


def generate_movie(
    row_indices: list[str],
    scene_path: Path | str,
    scene_name: str,
    output: Path | str,
    closed: bool = False,
    reverse: bool = False,
    loops: int = 1,
    vertex_mode: bool = False,
    border_file: bool = False,
    width: int = 1920,
    height: int = 1080,
    framerate: int = 10,
    num_cpus: int = 1,
):
    """Generate a movie from a list of row indices.

    Parameters
    ----------
    row_indices : list[int]
        The list of row indices to generate the movie from.
    scene_path : Path | str
        The scene file to use.
    scene_name : str
        The name of the scene in the scene file.
    output : Path | str
        The output file path.
    closed : bool, optional
        If enabled, a closed loop will be generated. This appends the first row index to the end of the row index
        traversal list., by default False.
    reverse : bool, optional
        If enabled, a reverse of the traversal list will be appended to the row index traversal list., by default False.
    loops : int, optional
        How many times to loop the movie, by default 1.
    vertex_mode : bool, optional
        If enabled, row_indices are treated as vertex indices. The first argument should be the surface that the
        vertices are on. (e.g. CORTEX_LEFT 0 1 2 3...), by default False.
    border_file : bool, optional
        If enabled, the border file will be used to generate the movie. The row_indices argument should be the border
        file., by default
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

    # make sure row_indices don't have line returns
    row_indices = [r.strip() for r in row_indices]

    # if border file, load the border file and turn on vertex mode
    if border_file:
        border = Border(row_indices[0])
        row_indices = border.data
        vertex_mode = True

    # in vertex mode, convert the vertex indices to row indices
    if vertex_mode:
        surface = row_indices.pop(0)
        cifti_img = scene.get_cifti_file()
        structure = [
            (str(s[0]), cast(slice, s[1]), cast(BrainModelAxis, s[2]))
            for s in cifti_img.header.get_axis(1).iter_structures()
            if surface in str(s[0])
        ][0]
        path = np.array(list(map(int, row_indices)))
        # make sure the vertex indices are within bounds
        if not np.all((structure[1].start <= path) & (path < structure[1].stop)):
            raise ValueError("Vertex indices are out of bounds.")
        # convert vertex indices to row indices
        path = cast(list[int], np.searchsorted(structure[2].vertex, path).tolist())
    else:  # make sure path is a list of integers
        path = list(map(int, row_indices))

    # modify the math if path mods enabled
    if closed:
        path.append(path[0])
    if reverse:
        path += path[::-1]

    # check where row indices are on
    structure = scene.get_structure_from_row(path[0])

    # first compute the continuous path
    if structure == "CORTEX_LEFT" or structure == "CORTEX_RIGHT":  # surface
        continuous_path = get_continuous_path(path, scene)
    else:  # volume
        continuous_path = volume_interpolation(path, scene)
    process_frames(output, continuous_path, scene, scene_name, width, height, framerate, loops, num_cpus)
