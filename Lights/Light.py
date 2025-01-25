

class LightSource:
    def __init__(self, position, intensity, color=[1, 1, 1]):
        self.position = position
        self.intensity = intensity
        self.color = color

class PointLight(LightSource):
    def __init__(self, position, intensity):
        super().__init__(position, intensity, color=[1, 1, 1])
