import json
import os
import sys
import time
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

with open('config.json') as f:
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

print(f"Execution time: {time.process_time() - start}")