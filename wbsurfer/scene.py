"""Load a Scene file and methods to manipulate it."""

import xml.etree.ElementTree as ET
from pathlib import Path

from nibabel.cifti2.cifti2 import Cifti2Image
from numpy import float64
from numpy.typing import NDArray


class Scene:
    """A class to represent a Scene file.

    Parameters
    ----------
    path : Path | str
        The path to the Scene file.
    """

    base_path: Path
    tree: ET.ElementTree

    def __init__(self, path: Path | str):
        # store the path to the scene file
        scene_path = Path(path).resolve()

        # store the base_path of the scene file
        self.base_path = scene_path.parent

        # load the scene file
        self.tree = ET.parse(scene_path)

        # convert all relative file paths to absolute paths
        self.convert_relative_to_absolute()

    def get_path_elements(self) -> list[ET.Element]:
        """Get all path elements in the Scene file."""
        root = self.tree.getroot()
        return [
            *root.findall(".//Object[@Type='pathName'][@Name='dataFileName_V2']"),
            *root.findall(".//Object[@Type='pathName'][@Name='fileName']"),
            *root.findall(".//Object[@Type='pathName'][@Name='m_selectedSurfacePathName']"),
            *root.findall(".//Object[@Type='pathName'][@Name='primaryAnatomicalSurface']"),
        ]

    def convert_relative_to_absolute(self) -> None:
        """Converts all relative file paths in the Scene file to absolute paths."""
        filenames = self.get_path_elements()
        for filename in filenames:
            if filename.text is not None:
                filename.text = str((self.base_path / filename.text).resolve())

    def get_files(self, ext: str) -> list[Path]:
        """Returns all files with the given extension found in the scene file.

        Parameters
        ----------
        ext : str
            The extension of the files to return.
        """
        filenames = self.get_path_elements()
        return [Path(f.text) for f in filenames if f.text is not None and f.text.endswith(ext)]

    def get_vertex_and_voxel_table(self) -> tuple[NDArray[float64], NDArray[float64]]:
        """Get the vertex index from the given row index.

        Parameters
        ----------
        row : int
            The row index to get the vertex index from.
        """
        # load the CIFTI file
        # first try dtseries
        cifti_files = self.get_files(".dtseries.nii")
        # then try dconn
        if not cifti_files:
            cifti_files = self.get_files(".dconn.nii")
        # if no CIFTI files are found, return error
        if not cifti_files:
            raise ValueError("No CIFTI files found in Scene file.")
        # load first cifti_file found
        cifti = Cifti2Image.load(str(cifti_files[0]))
        # get vertex and voxel tables from 2nd axis
        vertex_table = cifti.header.get_axis(1).vertex
        voxel_table = cifti.header.get_axis(1).voxel
        return vertex_table, voxel_table

    def change_connectivity_active_row(self, row: int) -> None:
        """Change the active row for connectivity map.

        Parameters
        ----------
        row : int
            The row to make active.
        """
        root = self.tree.getroot()
        row_index_elements = root.findall(".//Object[@Name='m_rowIndex']")
        for element in row_index_elements:
            element.text = str(row)

    def save(self, path: Path) -> None:
        """Save the Scene file.

        Parameters
        ----------
        path : Path
            The path to save the Scene file.
        """
        self.tree.write(path, encoding="utf-8", xml_declaration=True)
