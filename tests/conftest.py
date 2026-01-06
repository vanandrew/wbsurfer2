import logging
from pathlib import Path

from pytest import fixture

THISDIR = Path(__file__).resolve().parent


@fixture
def dtseries_scene():
    return THISDIR / "data" / "dtseries.scene"


@fixture(autouse=True)
def reset_logging():
    """Reset logging configuration before and after each test to ensure isolation."""
    yield

    # Clean up after the test - close and remove any handlers added during the test
    # but preserve pytest's handlers
    root_logger = logging.getLogger()
    pytest_handlers = [
        h for h in root_logger.handlers if "pytest" in type(h).__module__
    ]

    for handler in root_logger.handlers[:]:
        if handler not in pytest_handlers:
            handler.close()
            root_logger.removeHandler(handler)
