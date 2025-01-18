import numpy as np
class Material:
    """
    Simple material:
    - Kd: base diffusion color [R,G,B] in 0..1
    - Ni : index of refraction
    - d : opacity (1.0 = fully opaque)
    - reflection: reflectance (0..1)
    """
    def __init__(self, name="Default"):
        self.name = name
        self.Kd = np.array([0.8, 0.8, 0.8], dtype=float)
        self.Ni = 1.0
        self.d  = 1.0
        self.reflection = 0.0

    @property
    def color_rgb(self):
        """
        Returns color (R,G,B) on a scale of 0..255 as a tuple int.
        """
        return tuple(int(255*c) for c in self.Kd)

    def __repr__(self):
        return (f"Material(name={self.name}, Kd={self.Kd}, Ni={self.Ni}, "
                f"d={self.d}, reflection={self.reflection})")

