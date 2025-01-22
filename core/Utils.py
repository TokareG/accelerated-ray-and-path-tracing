from typing import List

class Utils:
    """
    A utility class providing static methods for common vector operations used in 3D computations.

    """

    @staticmethod
    def cross(v1: List[float], v2: List[float]):
        """
        Computes the cross product of two 3D vectors.
        The cross product of vectors v1 and v2 results in a third vector that is perpendicular to both
        v1 and v2, following the right-hand rule.
        """
        return [v1[1] * v2[2] - v1[2] * v2[1],
                v1[2] * v2[0] - v1[0] * v2[2],
                v1[0] * v2[1] - v1[1] * v2[0]]
    
    @staticmethod
    def dot(v1: List[float], v2:List[float]):
        """
        Computes the dot product of two vectors.
        The dot product is a scalar value representing the magnitude of the projection of one vector
        onto another. It is calculated as the sum of the products of corresponding components.
        """
        return sum(x * y for x, y in zip(v1, v2))

    @staticmethod
    def norm(v: List[float]):
        """
        Normalizes a vector to have a unit length.
        Normalization scales the vector so that its length is 1, preserving its direction. This is
        essential for operations where direction matters but magnitude does not, such as in lighting calculations.
        """
        length = Utils.dot(v,v)**(1/2)
        assert length != 0, "Cannot normalize zero-length vector"
        return [x / length for x in v]
    
    @staticmethod
    def sub(v1: List[float], v2: List[float]):
        """
        Subtracts one vector from another.
        Performs element-wise subtraction of v2 from v1.
        """
        return [x - y for x, y in zip(v1, v2)]
    
    @staticmethod
    def add(v1: List[float], v2: List[float]):
        """
        Adds two vectors together.
        Performs element-wise addition of v1 and v2.
        """
        return [x + y for x, y in zip(v1, v2)]
    
    @staticmethod
    def matmul(v1: List[float], v2: List[float]):
        """
        Performs element-wise multiplication (Hadamard product) of two vectors.
        This operation multiplies corresponding components of the vectors together.
        """
        return [x * y for x, y in zip(v1, v2)]
    
    @staticmethod
    def scalmul(f: float, v: List[float]):
        """
        Multiplies a vector by a scalar.
        Scales each component of the vector by the given scalar value.
        """
        return [f * x for x in v]

    @staticmethod
    def div_by_scalar(v: List[float],f: float):
        """
        Divides a vector by a scalar.
        Scales each component of the vector by the reciprocal of the given scalar value.
        """
        return [x / f for x in v]
    
    

dot = Utils.dot
cross = Utils.cross
norm = Utils.norm
sub = Utils.sub
add = Utils.add
matmul = Utils.matmul
scalmul = Utils.scalmul
div_by_scalar = Utils.div_by_scalar