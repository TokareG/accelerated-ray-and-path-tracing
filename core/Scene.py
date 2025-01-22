from pywavefront import Wavefront, material
from models import *
from core import *
from core.Utils import *
import os

class Scene:
    def __init__(self):
        pass

    def load_from_file(self, filepath):
        root_path = os.path.join(os.path.dirname(__file__) + "/..")
        scene = Wavefront(os.path.join(root_path, filepath), collect_faces=True)
        meshes = []
        for m in scene.mesh_list:
            mesh = Mesh(m.name)
            min_point = [float('+inf'),float('+inf'),float('+inf')]
            max_point = [float('-inf'),float('-inf'),float('-inf')]
            for material in m.materials:
                for i in range(0, len(material.vertices), 24):
                    temp = material.vertices[i:i+24]
                    v0_all = temp[0:8]
                    v1_all = temp[8:16]
                    v2_all = temp[16:24]
                    vt0, vn0, v0 = v0_all[:2], v0_all[2:5], v0_all[5:]
                    vt1, vn1, v1 = v1_all[:2], v1_all[2:5], v1_all[5:]
                    vt2, vn2, v2 = v2_all[:2], v2_all[2:5], v2_all[5:]
                    min_point = [min(v0[0], v1[0], v2[0], min_point[0]),
                                min(v0[1], v1[1], v2[1], min_point[1]),
                                min(v0[2], v1[2], v2[2], min_point[2])]
                    max_point = [max(v0[0], v1[0], v2[0], max_point[0]),
                                max(v0[1], v1[1], v2[1], max_point[1]),
                                max(v0[2], v1[2], v2[2], max_point[2])]
                    face = Triangle(v0, v1, v2, material)
                    mesh.faces.append(face)     
            mesh.set_bounding_box(min_point, max_point)   
            meshes.append(mesh)

        self.mesh_list = meshes

    def hit(self, ray: Ray):
        closest_intersection = None
        for mesh in self.mesh_list:

            for i in range(3):
                if ray.direction[i] < 1e-8:
                    if ray.origin[i] < mesh.bounding_box_min[i] or ray.origin[i] > mesh.bounding_box_max[i]:
                        continue
                else:
                    t1 = (mesh.bounding_box_min[i] - ray.origin[i]) / ray.direction[i]
                    t2 = (mesh.bounding_box_max[i] - ray.origin[i]) / ray.direction[i]
                    if t1 > t2:
                        t1, t2 = t2, t1
                    if t1 > ray.t_min:
                        ray.t_min = t1
                    if t2 < ray.t_max:
                        ray.t_max = t2
                    if ray.t_min > ray.t_max:
                        break
            intersections = []
            for face in mesh.faces:
                result = face.hit(ray)
                t, intersection_point = result if result else (False, [0,0,0])
                if t and ray.t_min < t < ray.t_max:
                    intersections.append([t, intersection_point, scalmul(255, face.material.diffuse[:3]) if face.material and face.material.diffuse else [255,255,255]])
            if intersections:
                intersections.sort(key=lambda x: x[0])
                closest__mesh_intersection = intersections[0]

                if not closest_intersection or closest__mesh_intersection[0] < closest_intersection[0]:
                    closest_intersection = closest__mesh_intersection
        return closest_intersection







# for m in obj.mesh_list:
#     mesh = Mesh(m.name)
#     min_point = [float('+inf'),float('+inf'),float('+inf')]
#     max_point = [float('-inf'),float('-inf'),float('-inf')]
#     for f in m.faces:
#         vertices = [obj.vertices[i] for i in f]
#         for vertex in vertices:
#             min_point = [min(vertex[0], min_point[0]),
#                          min(vertex[1], min_point[1]),
#                          min(vertex[2], min_point[2])]
#             max_point = [max(vertex[0], max_point[0]),
#                          max(vertex[1], max_point[1]),
#                          max(vertex[2], max_point[2])]
#         face = Triangle(vertices[0], vertices[1], vertices[2])
#         mesh.faces.append(face)     
#         mesh.set_bounding_box(min_point, max_point)   
#     #meshes.append(mesh)