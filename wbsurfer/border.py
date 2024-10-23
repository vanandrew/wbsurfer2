"""Module to read in border files."""

import xml.etree.ElementTree as ET
from pathlib import Path


class Border:
    """A class to represent a border file.

    Parameters
    ----------
    path : Path | str
        The path to the border file.
    """

    def __init__(self, path: Path | str):
        path = Path(path)
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()

    def get_structure(self) -> str:
        """Get the structure of the border file."""
        return self.root.attrib["Structure"]

    def get_vertices(self) -> list[str]:
        """Get the vertices of the border file."""
        vertices_node = self.root.find(".//Vertices")
        if vertices_node is None:
            raise ValueError("Vertices node not found.")
        if vertices_node.text is None:
            raise ValueError("Border file is empty.")
        # grab the left most vertex since border files are defined on a surface face instead of vertex
        return [v.split(" ")[0] for v in vertices_node.text.split("\n") if v != ""]

    @property
    def data(self) -> list[str]:
        """Return border file data"""
        return [self.get_structure(), *self.get_vertices()]
