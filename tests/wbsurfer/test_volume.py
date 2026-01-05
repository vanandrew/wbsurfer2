from pathlib import Path

import numpy as np
import pytest

from wbsurfer.scene import Scene
from wbsurfer.volume import bresenham3d, volume_interpolation


def test_bresenham3d_simple():
    """Test Bresenham's 3D algorithm with a simple line."""
    v0 = np.array([0, 0, 0], dtype=np.int64)
    v1 = np.array([5, 0, 0], dtype=np.int64)
    line = bresenham3d(v0, v1)
    # Should create a straight line along x-axis
    assert len(line) == 6  # 0, 1, 2, 3, 4, 5
    assert np.array_equal(line[0], [0, 0, 0])
    assert np.array_equal(line[-1], [5, 0, 0])


def test_bresenham3d_diagonal():
    """Test Bresenham's 3D algorithm with a diagonal line."""
    v0 = np.array([0, 0, 0], dtype=np.int64)
    v1 = np.array([3, 3, 3], dtype=np.int64)
    line = bresenham3d(v0, v1)
    # Should create a diagonal line
    assert len(line) == 4  # 0, 1, 2, 3
    assert np.array_equal(line[0], [0, 0, 0])
    assert np.array_equal(line[-1], [3, 3, 3])


def test_bresenham3d_negative_direction():
    """Test Bresenham's 3D algorithm with negative direction."""
    v0 = np.array([5, 5, 5], dtype=np.int64)
    v1 = np.array([0, 0, 0], dtype=np.int64)
    line = bresenham3d(v0, v1)
    # Should create a line from (5,5,5) to (0,0,0)
    assert len(line) == 6
    assert np.array_equal(line[0], [5, 5, 5])
    assert np.array_equal(line[-1], [0, 0, 0])


def test_bresenham3d_y_dominant():
    """Test Bresenham's 3D algorithm where y-axis is dominant."""
    v0 = np.array([0, 0, 0], dtype=np.int64)
    v1 = np.array([1, 5, 1], dtype=np.int64)
    line = bresenham3d(v0, v1)
    # Y should be the dominant axis
    assert len(line) == 6
    assert np.array_equal(line[0], [0, 0, 0])
    assert np.array_equal(line[-1], [1, 5, 1])


def test_bresenham3d_z_dominant():
    """Test Bresenham's 3D algorithm where z-axis is dominant."""
    v0 = np.array([0, 0, 0], dtype=np.int64)
    v1 = np.array([1, 1, 5], dtype=np.int64)
    line = bresenham3d(v0, v1)
    # Z should be the dominant axis
    assert len(line) == 6
    assert np.array_equal(line[0], [0, 0, 0])
    assert np.array_equal(line[-1], [1, 1, 5])


def test_bresenham3d_single_point():
    """Test Bresenham's 3D algorithm with same start and end point."""
    v0 = np.array([3, 3, 3], dtype=np.int64)
    v1 = np.array([3, 3, 3], dtype=np.int64)
    line = bresenham3d(v0, v1)
    # Should return single point
    assert len(line) == 1
    assert np.array_equal(line[0], [3, 3, 3])


def test_volume_interpolation(tmpdir):
    """Test volume interpolation with a scene."""
    # Load a volume scene
    volume_scene_path = Path(__file__).parent.parent / "data" / "volume.scene"
    scene = Scene(volume_scene_path)

    # Get some valid volume row indices
    vertex_table, voxel_table = scene.get_vertex_and_voxel_table()
    cifti = scene.get_cifti_file()

    # Find volume indices from the same structure
    # Iterate through structures to find a volume structure with multiple voxels
    for structure, bound, _ in cifti.header.get_axis(1).iter_structures():
        if bound.stop is None:
            bound = slice(bound.start, cifti.shape[1], None)
        # Check if this is a volume structure (vertices are -1)
        structure_vertex_table = vertex_table[bound]
        if np.all(structure_vertex_table == -1):
            # This is a volume structure
            structure_rows = np.arange(bound.start, bound.stop)
            if len(structure_rows) >= 2:
                # Use first and a nearby index from the same structure
                path = [
                    int(structure_rows[0]),
                    int(structure_rows[min(5, len(structure_rows) - 1)]),
                ]
                result = volume_interpolation(path, scene, suppress_progress=True)

                # Result should be a list of integers
                assert isinstance(result, list)
                assert all(isinstance(i, int) for i in result)
                # Should start and end with the original indices
                assert result[0] == path[0]
                assert result[-1] == path[-1]
                # Should have at least as many points as the input
                assert len(result) >= len(path)
                return  # Test passed, exit

    # If no suitable volume structure found, skip test
    pytest.skip("No suitable volume structure found in test data")


def test_volume_interpolation_cross_structures():
    """Test that volume_interpolation raises error when path crosses structures."""
    volume_scene_path = Path(__file__).parent.parent / "data" / "volume.scene"
    scene = Scene(volume_scene_path)

    # Get vertex and voxel tables
    vertex_table, voxel_table = scene.get_vertex_and_voxel_table()

    # Find indices from different structures
    # First, find a volume index
    volume_indices = np.where(vertex_table == -1)[0]
    # Then find a surface index (not -1)
    surface_indices = np.where(vertex_table != -1)[0]

    if len(volume_indices) > 0 and len(surface_indices) > 0:
        # Try to interpolate between different structures
        path = [int(volume_indices[0]), int(surface_indices[0])]
        with pytest.raises(ValueError, match="Path crosses structures"):
            volume_interpolation(path, scene, suppress_progress=True)
