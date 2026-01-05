import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pytest

from wbsurfer.scene import Scene


def test_scene(dtseries_scene: Path):
    """Test the Scene class.

    Parameters
    ----------
    dtseries_scene : Path
        The path to the dtseries scene file.
    """
    with TemporaryDirectory() as tmpdir:
        scene = Scene(dtseries_scene)
        # vertex_table, voxel_table = scene.get_vertex_and_voxel_table()
        scene.change_connectivity_active_row(100)
        scene.save(Path(tmpdir) / "test.scene")

        # load the scene and assert
        tree = ET.parse(Path(tmpdir) / "test.scene")
        root = tree.getroot()
        filenames = [
            *root.findall(".//Object[@Type='pathName'][@Name='dataFileName_V2']"),
            *root.findall(".//Object[@Type='pathName'][@Name='fileName']"),
            *root.findall(
                ".//Object[@Type='pathName'][@Name='m_selectedSurfacePathName']"
            ),
            *root.findall(
                ".//Object[@Type='pathName'][@Name='primaryAnatomicalSurface']"
            ),
        ]
        # test all filenames are absolute paths
        for filename in filenames:
            if filename.text is not None:
                assert Path(filename.text).is_absolute()


def test_scene_init(dtseries_scene: Path):
    """Test Scene initialization."""
    scene = Scene(dtseries_scene)
    assert scene.scene_path.exists()
    assert scene.base_path.exists()
    assert scene.tree is not None


def test_scene_with_scene_name(dtseries_scene: Path):
    """Test Scene initialization with a specific scene name."""
    # The dtseries.scene file has a scene named "test"
    scene = Scene(dtseries_scene, name="test")
    assert scene.scene_name == "test"


def test_scene_get_files_dtseries(dtseries_scene: Path):
    """Test getting CIFTI files from scene."""
    scene = Scene(dtseries_scene)
    dtseries_files = scene.get_files(".dtseries.nii")
    assert len(dtseries_files) > 0
    assert all(f.suffix == ".nii" for f in dtseries_files)


def test_scene_get_files_gifti(dtseries_scene: Path):
    """Test getting GIFTI files from scene."""
    scene = Scene(dtseries_scene)
    gifti_files = scene.get_files(".surf.gii")
    assert len(gifti_files) > 0
    assert all(str(f).endswith(".surf.gii") for f in gifti_files)


def test_scene_get_cifti_file(dtseries_scene: Path):
    """Test getting the CIFTI file."""
    scene = Scene(dtseries_scene)
    cifti = scene.get_cifti_file()
    assert cifti is not None
    assert hasattr(cifti, "header")


def test_scene_get_vertex_and_voxel_table(dtseries_scene: Path):
    """Test getting vertex and voxel tables."""
    scene = Scene(dtseries_scene)
    vertex_table, voxel_table = scene.get_vertex_and_voxel_table()
    assert len(vertex_table) > 0
    assert len(voxel_table) > 0
    assert len(vertex_table) == len(voxel_table)


def test_scene_get_vertex_from_row(dtseries_scene: Path):
    """Test getting vertex from row index."""
    scene = Scene(dtseries_scene)
    vertex = scene.get_vertex_from_row(16000)
    assert isinstance(vertex, (int, np.integer, np.floating))


def test_scene_get_row_from_vertex(dtseries_scene: Path):
    """Test getting row from vertex index."""
    scene = Scene(dtseries_scene)
    # Get a valid vertex first
    vertex_table, _ = scene.get_vertex_and_voxel_table()
    # Find a surface vertex (not -1)
    surface_rows = np.where(vertex_table != -1)[0]
    if len(surface_rows) > 0:
        test_row = int(surface_rows[0])
        vertex = vertex_table[test_row]
        hemisphere = scene.get_hemisphere_from_row(test_row)
        # Get row from vertex
        row = scene.get_row_from_vertex(hemisphere, int(vertex))
        assert row == test_row


def test_scene_get_row_from_vertex_invalid(dtseries_scene: Path):
    """Test that getting row from invalid vertex raises error."""
    scene = Scene(dtseries_scene)
    # Use a very large vertex index that doesn't exist
    with pytest.raises(ValueError, match="Vertex index.*not found"):
        scene.get_row_from_vertex("CORTEX_LEFT", 999999)


def test_scene_get_valid_vertices(dtseries_scene: Path):
    """Test getting valid vertices for a hemisphere."""
    scene = Scene(dtseries_scene)
    valid_vertices = scene.get_valid_vertices("CORTEX_LEFT")
    assert isinstance(valid_vertices, set)
    assert len(valid_vertices) > 0
    # All should be non-negative integers
    assert all(isinstance(v, (int, np.integer)) for v in valid_vertices)


def test_scene_get_vertex_to_row_mapping(dtseries_scene: Path):
    """Test getting vertex to row mapping."""
    scene = Scene(dtseries_scene)
    mapping = scene.get_vertex_to_row_mapping("CORTEX_LEFT")
    assert isinstance(mapping, dict)
    assert len(mapping) > 0
    # All keys and values should be integers
    assert all(isinstance(k, int) for k in mapping.keys())
    assert all(isinstance(v, int) for v in mapping.values())


def test_scene_get_structure_from_row(dtseries_scene: Path):
    """Test getting structure from row index."""
    scene = Scene(dtseries_scene)
    structure = scene.get_structure_from_row(16000)
    assert (
        structure in ["CORTEX_LEFT", "CORTEX_RIGHT"]
        or "ACCUMBENS" in structure
        or "AMYGDALA" in structure
    )


def test_scene_get_structure_from_row_out_of_bounds(dtseries_scene: Path):
    """Test that out of bounds row raises error."""
    scene = Scene(dtseries_scene)
    cifti = scene.get_cifti_file()
    with pytest.raises(IndexError, match="Row index out of bounds"):
        scene.get_structure_from_row(cifti.shape[1] + 100)


def test_scene_get_hemisphere_from_row(dtseries_scene: Path):
    """Test getting hemisphere from row index."""
    scene = Scene(dtseries_scene)
    # Find a cortical row
    vertex_table, _ = scene.get_vertex_and_voxel_table()
    surface_rows = np.where(vertex_table != -1)[0]
    if len(surface_rows) > 0:
        hemisphere = scene.get_hemisphere_from_row(int(surface_rows[0]))
        assert hemisphere in ["CORTEX_LEFT", "CORTEX_RIGHT"]


def test_scene_get_hemisphere_from_row_non_cortex(dtseries_scene: Path):
    """Test that getting hemisphere from non-cortical row raises error."""
    scene = Scene(dtseries_scene)
    # Find a volume row (vertex == -1)
    vertex_table, _ = scene.get_vertex_and_voxel_table()
    volume_rows = np.where(vertex_table == -1)[0]
    if len(volume_rows) > 0:
        with pytest.raises(ValueError, match="Row index is not a hemisphere"):
            scene.get_hemisphere_from_row(int(volume_rows[0]))


def test_scene_get_hemisphere_gifti_filename(dtseries_scene: Path):
    """Test getting hemisphere GIFTI filename."""
    scene = Scene(dtseries_scene)
    left_gifti = scene.get_hemisphere_gifti_filename("CORTEX_LEFT")
    assert left_gifti.exists()
    assert str(left_gifti).endswith(".surf.gii")

    right_gifti = scene.get_hemisphere_gifti_filename("CORTEX_RIGHT")
    assert right_gifti.exists()
    assert str(right_gifti).endswith(".surf.gii")


def test_scene_change_connectivity_active_row_surface(dtseries_scene: Path):
    """Test changing active row for surface data."""
    scene = Scene(dtseries_scene)
    # Find a surface row
    vertex_table, _ = scene.get_vertex_and_voxel_table()
    surface_rows = np.where(vertex_table != -1)[0]
    if len(surface_rows) > 0:
        test_row = (
            int(surface_rows[100]) if len(surface_rows) > 100 else int(surface_rows[0])
        )
        scene.change_connectivity_active_row(test_row)
        # The scene should be modified, we can't easily verify without saving


def test_scene_change_connectivity_active_row_volume():
    """Test changing active row for volume data."""
    volume_scene_path = Path(__file__).parent.parent / "data" / "volume.scene"
    scene = Scene(volume_scene_path)
    # Find a volume row
    vertex_table, _ = scene.get_vertex_and_voxel_table()
    volume_rows = np.where(vertex_table == -1)[0]
    if len(volume_rows) > 0:
        test_row = (
            int(volume_rows[10]) if len(volume_rows) > 10 else int(volume_rows[0])
        )
        scene.change_connectivity_active_row(test_row)
        # The scene should be modified


def test_scene_change_connectivity_active_row_invalid(dtseries_scene: Path):
    """Test that invalid row index raises error."""
    scene = Scene(dtseries_scene)
    cifti = scene.get_cifti_file()
    # Use an out of bounds row
    with pytest.raises((ValueError, IndexError)):
        scene.change_connectivity_active_row(cifti.shape[1] + 100)


def test_scene_save(dtseries_scene: Path, tmpdir):
    """Test saving a scene file."""
    scene = Scene(dtseries_scene)
    output_path = Path(tmpdir) / "saved_scene.scene"
    scene.save(output_path)
    assert output_path.exists()

    # Load the saved scene and verify it's valid XML
    tree = ET.parse(output_path)
    assert tree.getroot() is not None
