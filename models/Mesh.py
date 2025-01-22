from typing import List
from core.Utils import *
from core.Ray import *

class Mesh:
    """
    Represents a 3D mesh composed of multiple faces (typically triangles).

    Attributes:
        name (str): The name identifier for the mesh.
        faces (List[Triangle]): A list of faces (triangles) that make up the mesh.
        bounding_box_min (List[float]): The minimum coordinates (x, y, z) of the mesh's axis-aligned bounding box.
        bounding_box_max (List[float]): The maximum coordinates (x, y, z) of the mesh's axis-aligned bounding box.
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self.faces = []

    def set_bounding_box(self, min_point: List[float], max_point: List[float]) -> None:
        self.bounding_box_min = min_point
        self.bounding_box_max = max_point