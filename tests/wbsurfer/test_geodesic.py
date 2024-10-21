from pathlib import Path
from typing import cast

from nibabel.gifti.gifti import GiftiImage
from numpy import float32, int32
from numpy.typing import NDArray

from wbsurfer.geodesic import GeodesicPath
from wbsurfer.scene import Scene


def test_geodesic(dtseries_scene: Path):
    """Test the GeodesicPath class.

    Parameters
    ----------
    dtseries_scene : Path
        The path to the dtseries scene file.
    """
    # load the scene
    scene = Scene(dtseries_scene)

    # get vertex table
    vertex_table, _ = scene.get_vertex_and_voxel_table()

    # get vertices
    vertex_index_1 = vertex_table[16000]
    vertex_index_2 = vertex_table[16010]

    # get the gifti file
    hemi = scene.get_hemisphere_from_row(16000)
    gifti_file = scene.get_hemisphere_gifti_filename(hemi)

    # get vertices and faces
    vertices = cast(NDArray[float32], GiftiImage.load(gifti_file).darrays[0].data)
    faces = cast(NDArray[int32], GiftiImage.load(gifti_file).darrays[1].data)

    # initialize the geodesic path
    gpath = GeodesicPath(vertices, faces)

    # compute path
    path = gpath.path(vertex_index_1, vertex_index_2)
    nearest_index_path = gpath.as_nearest_index(path)
    # test if path unique
    assert len(nearest_index_path) == len(set(nearest_index_path))
