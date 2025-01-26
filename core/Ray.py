from typing import List
from core.Utils import *

class Ray:
    """
    Generates a ray originating from the camera and passing through the pixel at (i, j).
    """
    def __init__(self, origin: List[float], direction: List[float], t_min: float = 0.001, t_max: float = float('+inf')):
        self.origin = origin
        self.direction = direction
        self.t_min = t_min
        self.t_max = t_max
    
    def at(self, t: float):
        return add(self.origin, scale(t, self.direction))