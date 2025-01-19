from core import *
from models import *

objects = ObjReader.import_obj("path_to/cube.obj")
obj = MeshObject(faces=objects["Cube.001"]["faces"],
                 vertices=objects["Cube.001"]["vertices"],
                 normals=objects["Cube.001"]["normals"])
ray_origin = (0,-0.5,5)
ray_direction = (0.,0.,-1.)
res = obj.intersect(ray_origin, ray_direction)
print(res)