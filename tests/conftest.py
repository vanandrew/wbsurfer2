from pathlib import Path

from pytest import fixture

THISDIR = Path(__file__).resolve().parent


@fixture
def dtseries_scene():
    return THISDIR / "data" / "dtseries.scene"
