"""Exact search for Geodesic paths"""

import numpy as np
from geodesic_chenhan import CEdge as Edge
from geodesic_chenhan import CFace as Face
from geodesic_chenhan import CICHWithFurtherPriorityQueue as ICHWithFurtherPriorityQueue
from geodesic_chenhan import CPoint3D as Point3D
from geodesic_chenhan import CRichModel as RichModel  # type: ignore
from geodesic_chenhan import EdgePoint
from numpy.typing import NDArray


class GeodesicPath:
    """A class representing a Chenhan Geodesic Path.

    Parameters
    ----------
    vertices : NDArray[np.floating]
        The vertices of the mesh.
    faces : NDArray[np.integer]
        The faces of the mesh.
    """

    def __init__(self, vertices: NDArray[np.floating], faces: NDArray[np.integer]):
        # store vertices/faces
        self.vertices = vertices
        self.faces = faces

        # create model
        self.bmodel = RichModel()

        # get vertices and faces in proper format
        self.vertices_list = []
        for v in vertices:
            self.vertices_list.append(Point3D(float(v[0]), float(v[1]), float(v[2])))
        self.faces_list = []
        for f in faces:
            self.faces_list.append(Face(int(f[0]), int(f[1]), int(f[2])))

        # load mesh into model
        self.bmodel.LoadModel(self.vertices_list, self.faces_list)
        self.bmodel.Preprocess()

        # initialize current source and emethod
        self.current_source = None
        self.emethod = None

    def update_model(self, source: int) -> None:
        """Update the model with a given source vertex index.

        Parameters
        ----------
        source : int
            The source vertex index.
        """
        if self.current_source != source:
            self.emethod = ICHWithFurtherPriorityQueue(self.bmodel, {int(source)})
            self.emethod.Execute()
            self.current_source = source

    def distances(self, source: int) -> NDArray[np.float64]:
        """Get the distances to all other vertices from the source vertex index.

        Parameters
        ----------
        source : int
            The source vertex index.

        Returns
        -------
        NDArray[np.float64]
            The distances to all other vertices from the source vertex index.
        """
        self.update_model(source)
        return np.array([d.disUptodate for d in self.emethod.GetVertexDistances()])  # type: ignore

    def path(self, source: int, target: int) -> list[EdgePoint]:
        """Get the path from the source vertex index to the target vertex index.

        Parameters
        ----------
        source : int
            The source vertex index.
        target : int
            The target vertex index.

        Returns
        -------
        list[EdgePoint]
            The path from the source vertex index to the target vertex index as EdgePoint objects.
        """
        self.update_model(source)
        # get the path from target to source
        path = self.emethod.FindSourceVertex(int(target), [])  # type: ignore
        # reverse path to go from source to target
        path.reverse()
        # return path as list of edge points
        return path

    def as_vertex_positions(self, path: list[EdgePoint]) -> NDArray[np.float64]:
        """Returns a list of edge points as vertex positions.

        Parameters
        ----------
        path : list[EdgePoint]
            The path to convert to vertex positions.

        Returns
        -------
        NDArray[np.float64]
            The vertex positions of the path.
        """
        # get the vertex positions
        vertex_positions = []
        for p in path:
            pt = p.Get3DPoint(self.bmodel)
            vertex_positions.append((pt.x, pt.y, pt.z))
        return np.array(vertex_positions)

    def as_edges(self, path: list[EdgePoint]) -> list[Edge]:
        """Returns a list of edge points as edge objects.

        Parameters
        ----------
        path : list[EdgePoint]
            The path of edge points to convert to edge objects.

        Returns
        -------
        list[Edge]
            The edges of the path.
        """
        # get edge structs
        edges = []
        for p in path:
            e = self.bmodel.Edge(p.index)
            edges.append(e)
        return edges

    def remove_dupicate_indices_from_path(self, path: list[np.int64]) -> list[np.int64]:
        """Removes duplicate indices from a path.

        Parameters
        ----------
        path : list[np.integer]
            The path to remove duplicate indices from.

        Returns
        -------
        list[np.integer]
            The path with duplicate indices removed.
        """
        # remove duplicates from path
        last_vertex = -1
        nodups_path = []
        for p in path:
            if p != last_vertex:
                nodups_path.append(p)
                last_vertex = p
        return nodups_path

    def as_nearest_index(self, path: list[EdgePoint], remove_duplicates: bool = True) -> NDArray[np.int64]:
        """Returns the nearest index of each edge point in the path.

        Parameters
        ----------
        path : list[EdgePoint]
            The path to get the nearest index of each edge point.
        remove_duplicates : bool
            Whether to remove duplicate indices.

        Returns
        -------
        NDArray[np.int64]
            The nearest index of each edge point in the path.
        """
        # get edges
        edges = self.as_edges(path)
        # get the nearest index
        nearest_index = []
        for e, p in zip(edges, path):
            if p.isVertex:
                nearest_index.append(p.index)
                continue
            proportion = p.proportion
            if proportion <= 0.5:
                nearest_index.append(e.indexOfLeftVert)
            else:
                nearest_index.append(e.indexOfRightVert)
        if remove_duplicates:
            return np.array(self.remove_dupicate_indices_from_path(nearest_index))
        return np.array(nearest_index)
