import numpy as np
from numpy.typing import NDArray
from rich.progress import track

from wbsurfer.scene import Scene


def bresenham3d(v0: NDArray[np.int_], v1: NDArray[np.int_]) -> NDArray[np.int_]:
    """
    Bresenham's algorithm for a 3-D line

    https://www.geeksforgeeks.org/bresenhams-algorithm-for-3-d-line-drawing/

    Parameters
    ----------
    v0 : NDArray[np.int_]
        The start vertex of the line.
    v1 : NDArray[np.int_]
        The end vertex of the line.

    Returns
    -------
    NDArray[np.int_]
        The line array.
    """
    # initialize axis differences

    dx = np.abs(v1[0] - v0[0])
    dy = np.abs(v1[1] - v0[1])
    dz = np.abs(v1[2] - v0[2])
    xs = 1 if (v1[0] > v0[0]) else -1
    ys = 1 if (v1[1] > v0[1]) else -1
    zs = 1 if (v1[2] > v0[2]) else -1

    # determine the driving axis
    if dx >= dy and dx >= dz:
        d0 = dx
        d1 = dy
        d2 = dz
        s0 = xs
        s1 = ys
        s2 = zs
        a0 = 0
        a1 = 1
        a2 = 2
    elif dy >= dx and dy >= dz:
        d0 = dy
        d1 = dx
        d2 = dz
        s0 = ys
        s1 = xs
        s2 = zs
        a0 = 1
        a1 = 0
        a2 = 2
    elif dz >= dx and dz >= dy:
        d0 = dz
        d1 = dx
        d2 = dy
        s0 = zs
        s1 = xs
        s2 = ys
        a0 = 2
        a1 = 0
        a2 = 1

    # create line array
    line = np.zeros((d0 + 1, 3), dtype=np.int64)
    line[0] = v0

    # get points
    p1 = 2 * d1 - d0
    p2 = 2 * d2 - d0
    for i in range(d0):
        c = line[i].copy()
        c[a0] += s0
        if p1 >= 0:
            c[a1] += s1
            p1 -= 2 * d0
        if p2 >= 0:
            c[a2] += s2
            p2 -= 2 * d0
        p1 += 2 * d1
        p2 += 2 * d2
        line[i + 1] = c

    # return list
    return line


def volume_interpolation(path: list[int], scene: Scene) -> list[int]:
    """Interpolates a path in a volume.

    Parameters
    ----------
    path : list[str]
        The path to interpolate the volume of.
    scene : Scene
        The scene object.

    Returns
    -------
    list[str]
        The interpolated path of the volume.
    """
    # make list to store interpolated path
    interpolated_path = []

    # loop through pairs of points on the path
    for point_1, point_2 in track(zip(path[:-1], path[1:]), description="Interpolating path...", total=len(path) - 1):
        # first ensure they are in the same structure
        structure_1 = scene.get_structure_from_row(point_1)
        structure_2 = scene.get_structure_from_row(point_2)
        if structure_1 != structure_2:
            raise ValueError("Path crosses structures")
        # get the voxel table
        _, voxel_table = scene.get_vertex_and_voxel_table()
        # get the coordinates of the points
        coord_1 = voxel_table[point_1]
        coord_2 = voxel_table[point_2]
        coords = bresenham3d(coord_1, coord_2)
        # find row indices from coords
        interpolated = [
            int(np.where((voxel_table == c).all(axis=1))[0][0]) for c in coords if (voxel_table == c).all(axis=1).any()
        ]
        # get the interpolated path
        interpolated_path.extend(interpolated[:-1])
    # append final point
    interpolated_path.append(path[-1])
    # return interpolated path
    return interpolated_path
