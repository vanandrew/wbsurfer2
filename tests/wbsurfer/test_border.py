from pathlib import Path

import pytest

from wbsurfer.border import Border


def test_border_init(tmpdir):
    """Test Border initialization with a border file.

    Parameters
    ----------
    tmpdir : Path
        Temporary directory for test files.
    """
    border_path = Path(__file__).parent.parent / "data" / "test.border"
    border = Border(border_path)
    assert border.tree is not None
    assert border.root is not None


def test_border_get_structure():
    """Test getting the structure from a border file."""
    border_path = Path(__file__).parent.parent / "data" / "test.border"
    border = Border(border_path)
    structure = border.get_structure()
    assert structure == "CORTEX_LEFT"


def test_border_get_structure_right():
    """Test getting the structure from a right hemisphere border file."""
    border_path = Path(__file__).parent.parent / "data" / "test_right.border"
    border = Border(border_path)
    structure = border.get_structure()
    assert structure == "CORTEX_RIGHT"


def test_border_get_vertices():
    """Test getting vertices from a border file."""
    border_path = Path(__file__).parent.parent / "data" / "test.border"
    border = Border(border_path)
    vertices = border.get_vertices()
    # The border file has vertices on 3 lines
    assert len(vertices) == 3
    # Check that the leftmost vertices are extracted
    assert vertices[0] == "8386"
    assert vertices[1] == "8959"
    assert vertices[2] == "16565"


def test_border_data_property():
    """Test the data property returns structure and vertices."""
    border_path = Path(__file__).parent.parent / "data" / "test.border"
    border = Border(border_path)
    data = border.data
    # Should have structure + vertices
    assert len(data) == 4
    assert data[0] == "CORTEX_LEFT"
    assert data[1] == "8386"
    assert data[2] == "8959"
    assert data[3] == "16565"


def test_border_no_vertices_node(tmpdir):
    """Test Border with missing Vertices node raises ValueError."""
    # Create a border file without Vertices node
    border_content = """<?xml version="1.0" encoding="UTF-8"?>
<BorderFile Version="3" Structure="CORTEX_LEFT" SurfaceNumberOfVertices="32492">
    <Class Name="???" Red="1" Green="1" Blue="1">
        <Border Name="test" Red="0" Green="0" Blue="0">
            <BorderPart Closed="False">
            </BorderPart>
        </Border>
    </Class>
</BorderFile>"""
    border_path = Path(tmpdir) / "invalid_border.border"
    border_path.write_text(border_content)

    border = Border(border_path)
    with pytest.raises(ValueError, match="Vertices node not found"):
        border.get_vertices()


def test_border_empty_vertices(tmpdir):
    """Test Border with empty Vertices node raises ValueError."""
    # Create a border file with empty Vertices node
    border_content = """<?xml version="1.0" encoding="UTF-8"?>
<BorderFile Version="3" Structure="CORTEX_LEFT" SurfaceNumberOfVertices="32492">
    <Class Name="???" Red="1" Green="1" Blue="1">
        <Border Name="test" Red="0" Green="0" Blue="0">
            <BorderPart Closed="False">
                <Vertices></Vertices>
            </BorderPart>
        </Border>
    </Class>
</BorderFile>"""
    border_path = Path(tmpdir) / "empty_border.border"
    border_path.write_text(border_content)

    border = Border(border_path)
    with pytest.raises(ValueError, match="Border file is empty"):
        border.get_vertices()
