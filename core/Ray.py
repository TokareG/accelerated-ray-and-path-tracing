from typing import List
from core.Utils import *

class Ray:
    """
    Generates a ray originating from the camera and passing through the pixel at (i, j).
    """
    def __init__(self, origin: List[float], direction: List[float]):
        self.origin = origin
        self.direction = direction
        self.t_min = 0.1
        self.t_max = float('+inf')
    
    def at(self, t: float):
        return add(self.origin, scalmul(t, self.direction))