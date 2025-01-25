import json
import os
import sys
import time

from core.Utils import *

"""
TODO:
- Separate light classes
- Define ambient light
- Define point light
- Define spot light ?
- Define directional light
- Add light sources to scene
- Read camera config
"""
start = time.process_time()
class LightSource:
    def __init__(self, position, intensity=250):
        self.position = position
        self.intensity = intensity
        self.color = [1, 1, 1]

class LightSourceSquare(LightSource):
    def __init__(self, position, intensity, width, height):
        super().__init__(position, intensity)
        self.width = width
        self.height = height

class LightSourceCircle(LightSource):
    def __init__(self, position, intensity, radius):
        super().__init__(position, intensity)
        self.radius = radius

with open('scene_config.json') as f:
    config = json.load(f)

lights = []

for idx, light in config['lights'].items():
    if light['type'] == 'square':
        light.pop('type')
        light_source = LightSourceSquare(**light)
    elif light['type'] == 'circle':
        light.pop('type')
        light_source = LightSourceCircle(**light)
    else:
        light_source = LightSource(**light[1:])
        print(light_source.position)
    lights.append(light_source)

for light in lights:
    print(json.dumps(light.__dict__))

def phong(scene, face, light):
    Ns, ka, kd, ks, Ni, d, illum = (face.material.shininess,
                                    face.material.ambient,
                                    face.material.diffuse,
                                    face.material.specular,
                                    face.material.optical_density,
                                    face.material.transparency,
                                    face.material.illumination_model)
    L = norm(sub(light.position, face.position))
    R = norm(sub(scale(2 * dot(face.normal, L), face.normal), L))
    V = norm(sub(scene.camera.position, face.position))
    color = scale(scene.ambient_light, ka) + scale(light.intensity, matmul(light.color, add(scale(max(0, dot(L, face.normal)), kd), scale(max(0, dot(R, V)) ** Ns, ks))))