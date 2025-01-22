from typing import List
from core.Utils import *
from core.Ray import *

class Mesh:
    def __init__(self, name: str) -> None:
        self.name = name
        self.faces = []

    def set_bounding_box(self, min_point: List[float], max_point: List[float]) -> None:
        self.bounding_box_min = min_point
        self.bounding_box_max = max_point