import json

from pywavefront import Wavefront, material

from Lights import Light
from Lights.Light import PointLight
from models import *
from core import *
from core.Utils import *
import os
from core.BVH import build_bvh, hit_bvh

class Scene:
    """
    Represents a 3D scene composed of multiple meshes loaded from a Wavefront OBJ file.
    The Scene class handles loading mesh data, computing bounding boxes for optimization,
    and performing ray intersections to determine visibility and color information.
    """

    def __init__(self,acceleration_structure="none") -> None:

        self.ambient_light = None
        self.mesh_list = None
        self.lights = None
        self.acceleration_structure = acceleration_structure
        self.bvh_root = None
    def load_from_file(self, filepath):
        """
        Loads a 3D scene from a Wavefront OBJ file and constructs Mesh and Triangle objects.
        """
        root_path = os.path.join(os.path.dirname(__file__) + "/..")
        scene = Wavefront(os.path.join(root_path, filepath), collect_faces=True)
        meshes = []
        all_faces = []
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

        for mesh in self.mesh_list:
            all_faces.extend(mesh.faces)
        self.bvh_root = build_bvh(all_faces, max_faces_in_leaf=4)


    def load_config(self, path):
        LIGHT_TYPE_MAP = {
            'point': PointLight,
            'default': Light
        }
        with open(path, 'r') as f:
            config = json.load(f)
        self.lights = []
        for idx, light in config['lights'].items():
            light_type = light.pop('type', "default")
            light_class = LIGHT_TYPE_MAP.get(light_type, LIGHT_TYPE_MAP['default'])
            self.lights.append(light_class(**light))
        self.ambient_light = config['ambient_light']

    def hit(self, ray: Ray):
        """
        Determines if a given ray intersects with any objects in the scene and returns
        information about the closest intersection.
        """
        if self.acceleration_structure == "bvh" and self.bvh_root:
           return hit_bvh(ray, self.bvh_root)

        closest_intersection = None
        for mesh in self.mesh_list:
            ray.t_max = float('+inf')
            ray.t_min = 0.1
            for i in range(3):
                if ray.direction[i] < 1e-8:
                    if ray.origin[i] < mesh.bounding_box_min[i] or ray.origin[i] > mesh.bounding_box_max[i]:
                        continue
                # else:
                #     t1 = (mesh.bounding_box_min[i] - ray.origin[i]) / ray.direction[i]
                #     t2 = (mesh.bounding_box_max[i] - ray.origin[i]) / ray.direction[i]
                #     if t1 > t2:
                #         t1, t2 = t2, t1
                #     if t1 > ray.t_min:
                #         ray.t_min = t1
                #     if t2 < ray.t_max:
                #         ray.t_max = t2
                #     if ray.t_min > ray.t_max:
                #         break
            intersections = []
            for face in mesh.faces:
                result = face.hit(ray)
                t, intersection_point, face = result if result else (False, [0,0,0], None)
                if t and ray.t_min <= t <= ray.t_max:
                    #color = self.phong(face, self.lights[0], intersection_point)
                    intersections.append([t, intersection_point, face])
            if intersections:
                intersections.sort(key=lambda x: x[0])
                closest__mesh_intersection = intersections[0]

                if not closest_intersection or closest__mesh_intersection[0] < closest_intersection[0]:
                    closest_intersection = closest__mesh_intersection
        return closest_intersection

