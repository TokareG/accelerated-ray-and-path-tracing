from typing import List

class Utils:

    @staticmethod
    def cross(v1: List[float], v2: List[float]):
        return [v1[1] * v2[2] - v1[2] * v2[1],
                v1[2] * v2[0] - v1[0] * v2[2],
                v1[0] * v2[1] - v1[1] * v2[0]]
    
    @staticmethod
    def dot(v1: List[float], v2:List[float]):
        return sum(x * y for x, y in zip(v1, v2))
    
    @staticmethod
    def norm(v: List[float]):
        length = Utils.dot(v,v)**(1/2)
        assert length != 0, "Cannot normalize zero-length vector"
        return [x / length for x in v]
    
    @staticmethod
    def sub(v1: List[float], v2: List[float]):
        return [x - y for x, y in zip(v1, v2)]
    
    @staticmethod
    def add(v1: List[float], v2: List[float]):
        return [x + y for x, y in zip(v1, v2)]
    
    @staticmethod
    def matmul(v1: List[float], v2: List[float]):
        return [x * y for x, y in zip(v1, v2)]
    
    @staticmethod
    def scalmul(f: float, v: List[float]):
        return [f * x for x in v]
    
    @staticmethod
    def div_by_scalar(v: List[float],f: float):
        return [x / f for x in v]
    
    

dot = Utils.dot
cross = Utils.cross
norm = Utils.norm
sub = Utils.sub
add = Utils.add
matmul = Utils.matmul
scalmul = Utils.scalmul
div_by_scalar = Utils.div_by_scalar