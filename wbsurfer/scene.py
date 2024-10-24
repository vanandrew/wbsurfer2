"""Load a Scene file and methods to manipulate it."""

import xml.etree.ElementTree as ET
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal, cast

import numpy as np
from nibabel.affines import apply_affine
from nibabel.cifti2.cifti2 import Cifti2Image
from numpy import float64
from numpy.typing import NDArray


class Scene:
    """A class to represent a Scene file.

    Parameters
    ----------
    path : Path | str
        The path to the Scene file.
    name : str | None
        The name of the Scene to use in the Scene file.
    """

    base_path: Path
    tree: ET.ElementTree
    scene_name: str | None

    def __init__(self, path: Path | str, name: str | None = None):
        # store the path to the scene file
        self.scene_path = Path(path).resolve()

        # store the base_path of the scene file
        self.base_path = self.scene_path.parent

        # load the scene file
        self.tree = ET.parse(self.scene_path)

        # if scene name is provided, store it
        self.scene_name = name

        # convert all relative file paths to absolute paths
        self.convert_relative_to_absolute()

    def get_scene_subtree(self) -> ET.Element:
        """Get the Scene subtree from the Scene file."""
        # check scene name is provided, if None just return the root node
        if self.scene_name is None:
            return self.tree.getroot()
        # get the scene node with the given name
        root = self.tree.getroot()
        scenes = root.findall(".//Scene[@Type='SCENE_TYPE_FULL']")
        for scene in scenes:
            if scene is None:
                continue
            scene_name = scene.find("./Name")
            if scene_name is None:
                continue
            if scene_name.text == self.scene_name:
                return scene
        # if no scene is found, raise error
        raise ValueError(f"Scene with name '{self.scene_name}' not found.")

    def get_path_elements(self) -> list[ET.Element]:
        """Get all path elements in the Scene file."""
        #
        root = self.get_scene_subtree()
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
            if filename.text is None:
                continue
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

    def get_cifti_file(self) -> Cifti2Image:
        """Returns the first CIFTI file found in the scene."""
        # first try dtseries
        cifti_files = self.get_files(".dtseries.nii")
        # then try dconn
        if not cifti_files:
            cifti_files = self.get_files(".dconn.nii")
        # if no CIFTI files are found, return error
        if not cifti_files:
            raise ValueError("No CIFTI files found in Scene file.")
        # load first cifti_file found
        return Cifti2Image.load(str(cifti_files[0]))

    def get_vertex_and_voxel_table(self) -> tuple[NDArray[float64], NDArray[float64]]:
        """Get the vertex index from the given row index.

        Parameters
        ----------
        row : int
            The row index to get the vertex index from.
        """
        # load the CIFTI file
        cifti = self.get_cifti_file()
        # get vertex and voxel tables from 2nd axis
        vertex_table = cifti.header.get_axis(1).vertex
        voxel_table = cifti.header.get_axis(1).voxel
        return vertex_table, voxel_table

    def get_vertex_from_row(self, row: int) -> int:
        """Returns the equivalent vertex index from the given row index."""
        # get vertex table
        vertex_table, _ = self.get_vertex_and_voxel_table()
        # return the vertex index
        return vertex_table[row]

    @staticmethod
    def change_tuple_index_element(element: ET.Element, value: Iterable[Any]) -> None:
        """Change the value of an Element with an index in the name."""
        for index, v in zip(range(3), value):
            subelement = element.find(f"./Element[@Index='{index}']")
            if subelement is None:
                # make a new subelement
                subelement = element.makeelement("Element", {"Index": str(index)})
            subelement.text = str(v)

    def change_connectivity_active_row(self, row: int) -> None:
        """Change the active row for connectivity map.

        Parameters
        ----------
        row : int
            The row to make active.
        """
        # get vertex table and voxel table
        vertex_table, voxel_table = self.get_vertex_and_voxel_table()

        # set vertex and voxel index to -1
        vertex_index = -1
        voxel_index = [-1, -1, -1]

        # get the equivalent vertex index
        vertex_index = vertex_table[row]

        # check if a valid vertex, fallback to voxel if not
        if vertex_index == -1:
            voxel_index = voxel_table[row]

        # if both still incalid, raise error
        if vertex_index == -1 and (np.array(voxel_index) == -1).all():
            raise ValueError("Invalid row index.")

        # this is a surface row
        if vertex_index != -1:
            root = self.tree.getroot()
            row_index_elements = root.findall(".//Object[@Name='m_rowIndex']")
            for element in row_index_elements:
                element.text = str(row)
            surface_vertex_index_elements = root.findall(".//Object[@Name='m_surfaceVertexIndex']")
            for element in surface_vertex_index_elements:
                element.text = str(vertex_index)
            surface_node_index_elements = root.findall(".//ObjectArray[@Name='m_surfaceNodeIndices']")
            for element in surface_node_index_elements:
                subelement = element.find("./Element[@Index='0']")
                if subelement is None:
                    # make a new subelement
                    subelement = element.makeelement("Element", {"Index": "0"})
                subelement.text = str(vertex_index)
        elif not (np.array(voxel_index) == -1).all():  # this is a volume row
            affine = self.get_cifti_file().header.get_axis(1).affine
            coords = apply_affine(affine, np.array(voxel_index))
            root = self.tree.getroot()
            row_index_elements = root.findall(".//Object[@Name='m_rowIndex']")
            for element in row_index_elements:
                element.text = str(row)
            voxel_ijk_elements = root.findall(".//ObjectArray[@Name='m_voxelIJK']")
            for element in voxel_ijk_elements:
                self.change_tuple_index_element(element, voxel_index)
            volume_xyz_elements = root.findall(".//ObjectArray[@Name='m_volumeXYZ']")
            for element in volume_xyz_elements:
                self.change_tuple_index_element(element, coords)
            stereotaxic_xyz_elements = root.findall(".//ObjectArray[@Name='m_stereotaxicXYZ']")
            for element in stereotaxic_xyz_elements:
                self.change_tuple_index_element(element, coords)
            slice_coordinate_axial_elements = root.findall(".//Object[@Name='m_sliceCoordinateAxial']")
            for element in slice_coordinate_axial_elements:
                element.text = str(coords[2])
            slice_coordinate_coronal_elements = root.findall(".//Object[@Name='m_sliceCoordinateCoronal']")
            for element in slice_coordinate_coronal_elements:
                element.text = str(coords[1])
            slice_coordinate_parasagittal_elements = root.findall(".//Object[@Name='m_sliceCoordinateParasagittal']")
            for element in slice_coordinate_parasagittal_elements:
                element.text = str(coords[0])

    def get_hemisphere_from_row(self, row: int) -> Literal["CORTEX_LEFT", "CORTEX_RIGHT"]:
        """Same as get_structure_from_row, but raises error on non-hemisphere."""
        structure = self.get_structure_from_row(row)
        if structure not in ["CORTEX_LEFT", "CORTEX_RIGHT"]:
            raise ValueError("Row index is not a hemisphere.")
        return cast(Literal["CORTEX_LEFT", "CORTEX_RIGHT"], structure)

    def get_structure_from_row(self, row: int) -> str:
        """Get the hemisphere from the given row index.

        Parameters
        ----------
        row : int
            The row index to get the hemisphere from.
        """
        # load the cifti file
        cifti = self.get_cifti_file()

        # iter_structures
        match = False
        structure = None
        for structure, bound, _ in cifti.header.get_axis(1).iter_structures():
            if bound.stop is None:
                bound = slice(bound.start, cifti.shape[1], None)
            if bound.start <= row < bound.stop:
                match = True
                break

        # return error if no match
        if not match:
            raise IndexError(f"Row index out of bounds, max row is {cifti.shape[1]-1}.")

        # test if CORTEX_LEFT or CORTEX_RIGHT or neither
        return str(structure).split("CIFTI_STRUCTURE_")[1]

    def get_hemisphere_gifti_filename(self, hemi: Literal["CORTEX_LEFT", "CORTEX_RIGHT"]) -> Path:
        """Get the filename of the hemisphere surface."""
        # get root
        root = self.get_scene_subtree()

        # get BrainStructure classes
        brain_structures = root.findall(".//Object[@Class='BrainStructure']")

        # sort out which object is right/left cortex
        surface_paths: dict[str, Path] = {}
        for surf_name in ["CORTEX_LEFT", "CORTEX_RIGHT"]:
            for obj in brain_structures:
                element = obj.find("./Object[@Type='enumeratedType'][@Name='m_structure']")
                if element is None:
                    continue
                if element.text != surf_name:
                    continue
                gifti_path = obj.find("./Object[@Type='pathName'][@Name='primaryAnatomicalSurface']")
                if gifti_path is None:
                    continue
                if gifti_path.text is None:
                    continue
                surface_paths[surf_name] = Path(gifti_path.text)
                break

        # return the path
        return surface_paths[hemi]

    def save(self, path: Path) -> None:
        """Save the Scene file.

        Parameters
        ----------
        path : Path
            The path to save the Scene file.
        """
        self.tree.write(path, encoding="utf-8", xml_declaration=True)
