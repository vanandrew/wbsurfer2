import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

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
            *root.findall(".//Object[@Type='pathName'][@Name='m_selectedSurfacePathName']"),
            *root.findall(".//Object[@Type='pathName'][@Name='primaryAnatomicalSurface']"),
        ]
        # test all filenames are absolute paths
        for filename in filenames:
            if filename.text is not None:
                assert Path(filename.text).is_absolute()
