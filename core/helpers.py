
class helpers:
    def add(v1, v2):
        """
        Adds two vectors.
        """
        return tuple(a + b for a, b in zip(v1, v2))

    def subtract(v1, v2):
        """
        Subtracts the second vector from the first.
        """
        return tuple(a - b for a, b in zip(v1, v2))
    def multiply_scalar(v, scalar):
        """
        Multiplies a vector by a scalar.
        """
        return tuple(a * scalar for a in v)

    def dot(v1, v2):
        """
        Calculates the scalar product of two vectors.
        """
        return sum(a * b for a, b in zip(v1, v2))

    def normalize(v):
        """
        Normalizes the vector (tuple)
        """
        n = sum(a * a for a in v) ** 0.5
        if n < 1e-9:
            return v
        return tuple(a / n for a in v)

    def cross(v1: tuple, v2: tuple) -> tuple:
        """
        Calculates the vector product of two vectors (tuples).
        """
        return (
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]
        )

    def reflect(ray_dir, normal):
        """
        Calculates the reflection vector (tuple).
        """
        dot_product = helpers.dot(ray_dir, normal)
        return helpers.subtract(ray_dir, helpers.multiply_scalar(normal, 2 * dot_product))

    def refract(ray_dir, normal, n1, n2):
        """
        Refraction vector (Snell). Returns None in case of total internal reflection.
        ray_dir and normal must be normalized.
        """
        cos_i = -helpers.dot(normal, ray_dir)
        if cos_i < 0:
            normal = helpers.multiply_scalar(normal, -1)
            cos_i = -helpers.dot(normal, ray_dir)
            n1, n2 = n2, n1

        eta = n1 / n2
        k = 1 - eta ** 2 * (1 - cos_i ** 2)
        if k < 0:
            return None
        return helpers.add(helpers.multiply_scalar(ray_dir, eta), helpers.multiply_scalar(normal, eta * cos_i - k ** 0.5))