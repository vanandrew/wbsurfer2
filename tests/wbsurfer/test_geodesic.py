from pathlib import Path
from typing import cast

import numpy as np
from nibabel.gifti.gifti import GiftiImage
from numpy import float32, int32
from numpy.typing import NDArray

from wbsurfer.geodesic import (
    GeodesicPath,
    check_and_mask_medial_wall,
    get_continuous_path,
    remove_dupicate_indices_from_path,
)
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


def test_remove_duplicate_indices_from_path():
    """Test removing duplicate indices from a path."""
    # Path with duplicates
    path = [
        np.int64(1),
        np.int64(1),
        np.int64(2),
        np.int64(3),
        np.int64(3),
        np.int64(4),
    ]
    result = remove_dupicate_indices_from_path(path)
    assert result == [1, 2, 3, 4]


def test_remove_duplicate_indices_no_duplicates():
    """Test removing duplicates when there are none."""
    path = [np.int64(1), np.int64(2), np.int64(3), np.int64(4)]
    result = remove_dupicate_indices_from_path(path)
    assert result == [1, 2, 3, 4]


def test_remove_duplicate_indices_all_same():
    """Test removing duplicates when all indices are the same."""
    path = [np.int64(5), np.int64(5), np.int64(5), np.int64(5)]
    result = remove_dupicate_indices_from_path(path)
    assert result == [5]


def test_geodesic_distances(dtseries_scene: Path):
    """Test computing distances from a source vertex."""
    # load the scene
    scene = Scene(dtseries_scene)

    # get vertex table
    vertex_table, _ = scene.get_vertex_and_voxel_table()

    # get a vertex
    vertex_index = vertex_table[16000]

    # get the gifti file
    hemi = scene.get_hemisphere_from_row(16000)
    gifti_file = scene.get_hemisphere_gifti_filename(hemi)

    # get vertices and faces
    vertices = cast(NDArray[float32], GiftiImage.load(gifti_file).darrays[0].data)
    faces = cast(NDArray[int32], GiftiImage.load(gifti_file).darrays[1].data)

    # initialize the geodesic path
    gpath = GeodesicPath(vertices, faces)

    # compute distances
    distances = gpath.distances(vertex_index)

    # Check that distances is an array with the same length as vertices
    assert len(distances) == len(vertices)
    # Distance to self should be 0
    assert distances[vertex_index] == 0
    # All distances should be non-negative
    assert np.all(distances >= 0)


def test_geodesic_as_vertex_positions(dtseries_scene: Path):
    """Test getting vertex positions from a path."""
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
    positions = gpath.as_vertex_positions(path)

    # Should have 3D coordinates
    assert positions.shape[1] == 3
    # Should have same number of points as path
    assert len(positions) == len(path)


def test_geodesic_as_edges(dtseries_scene: Path):
    """Test getting edges from a path."""
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
    edges = gpath.as_edges(path)

    # Should have same number of edges as path
    assert len(edges) == len(path)


def test_geodesic_as_nearest_index_no_duplicates(dtseries_scene: Path):
    """Test getting nearest indices without removing duplicates."""
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
    nearest_with_dups = gpath.as_nearest_index(path, remove_duplicates=False)
    nearest_no_dups = gpath.as_nearest_index(path, remove_duplicates=True)

    # The version with duplicates removed should be shorter or equal
    assert len(nearest_no_dups) <= len(nearest_with_dups)


def test_check_and_mask_medial_wall(dtseries_scene: Path):
    """Test checking and masking the medial wall."""
    # load the scene
    scene = Scene(dtseries_scene)

    # get the gifti file for left hemisphere
    gifti_file = scene.get_hemisphere_gifti_filename("CORTEX_LEFT")

    # get vertices and faces
    vertices = cast(NDArray[float32], GiftiImage.load(gifti_file).darrays[0].data)
    faces = cast(NDArray[int32], GiftiImage.load(gifti_file).darrays[1].data)

    # check and mask
    new_vertices, new_faces = check_and_mask_medial_wall(
        vertices, faces, scene, "CORTEX_LEFT"
    )

    # Vertices should be unchanged
    assert np.array_equal(vertices, new_vertices)
    # Faces might be filtered if there's a medial wall
    assert len(new_faces) <= len(faces)


def test_get_continuous_path(dtseries_scene: Path):
    """Test getting a continuous path from row indices."""
    # load the scene
    scene = Scene(dtseries_scene)

    # Create a simple path with a few row indices
    path = [16000, 16010, 16020]

    # Get continuous path
    continuous = get_continuous_path(path, scene, suppress_progress=True)

    # Should be a list of integers
    assert isinstance(continuous, list)
    assert all(isinstance(i, int) for i in continuous)
    # Should have at least as many points as the input
    assert len(continuous) >= len(path)
    # Should start and end with the same values
    assert continuous[0] == path[0]
    assert continuous[-1] == path[-1]

    # All indices should be valid row indices
    vertex_table, _ = scene.get_vertex_and_voxel_table()
    assert all(0 <= i < len(vertex_table) for i in continuous)

    # All indices should belong to the same hemisphere
    hemi = scene.get_hemisphere_from_row(path[0])
    for idx in continuous:
        assert scene.get_hemisphere_from_row(idx) == hemi


def test_get_continuous_path_with_offset(dtseries_scene: Path):
    """Test that continuous path correctly handles hemisphere offsets."""
    # load the scene
    scene = Scene(dtseries_scene)

    # Get vertex table and hemisphere information
    vertex_table, _ = scene.get_vertex_and_voxel_table()

    # Find surface rows for left hemisphere
    left_start, left_stop = scene.get_hemisphere_row_offset("CORTEX_LEFT")
    left_rows = [i for i in range(left_start, min(left_start + 30, left_stop))]

    # Create a path in the left hemisphere
    path = left_rows[::10]  # Sample every 10th row

    # Get continuous path
    continuous = get_continuous_path(path, scene, suppress_progress=True)

    # Verify all returned indices are within the left hemisphere range
    assert all(left_start <= i < left_stop for i in continuous)

    # Verify the vertices in the continuous path are valid
    for row_idx in continuous:
        vertex = vertex_table[row_idx]
        assert vertex >= 0, f"Row {row_idx} should have a valid vertex"

    # Verify mapping back from vertex to row works correctly
    for row_idx in continuous:
        vertex = vertex_table[row_idx]
        # The vertex should map back to the correct row
        recovered_row = scene.get_row_from_vertex("CORTEX_LEFT", int(vertex))
        assert recovered_row == row_idx
