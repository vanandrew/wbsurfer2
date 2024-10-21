from pathlib import Path
from tempfile import TemporaryDirectory

from wbsurfer.movie import generate_movie


def test_scene(dtseries_scene: Path):
    """Test the Scene class.

    Parameters
    ----------
    dtseries_scene : Path
        The path to the dtseries scene file.
    """
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        generate_movie([16000, 16010, 16020], dtseries_scene, "test", tmp_path / "output.mp4")
