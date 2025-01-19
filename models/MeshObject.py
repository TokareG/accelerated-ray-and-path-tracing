from core.helpers import *

class MeshObject:
    def __init__(self,
                 faces: list[list[tuple[int, int, int]]],
                 normals: list[tuple[float, float, float]],
                 vertices: list[tuple[float, float, float]]):
        self.faces = faces
        self.normals = normals
        self.vertices = vertices
        self.bounding_box = {
            "min_corner": [float("inf"),
                           float("inf"),
                           float("inf")],
            "max_corner": [float("-inf"),
                           float("-inf"),
                           float("-inf")],
        }
        for vertex in vertices:
            for i in range(3):
                self.bounding_box["min_corner"][i] = min(self.bounding_box["min_corner"][i], vertex[i])
            for i in range(3):
                self.bounding_box["max_corner"][i] = max(self.bounding_box["max_corner"][i], vertex[i])

    def intersect(self, ray_origin, ray_dir):
        t_min = float('-inf')
        t_max = float('inf')

        for i in range(3):
            if abs(ray_dir[i]) < 1e-9:
                if ray_origin[i] < self.bounding_box["min_corner"][i] or ray_origin[i] > self.bounding_box["max_corner"][i]:
                    return None
            else:
                t1 = (self.bounding_box["min_corner"][i] - ray_origin[i]) / ray_dir[i]
                t2 = (self.bounding_box["max_corner"][i] - ray_origin[i]) / ray_dir[i]
                tmin_i = min(t1, t2)
                tmax_i = max(t1, t2)
                t_min = max(t_min, tmin_i)
                t_max = min(t_max, tmax_i)
                if t_max < t_min:
                    return None

        for face in self.faces:

            #normal = self.normals[face[0][2]-1]

            v0 = self.vertices[face[0][0]-1]
            v1 = self.vertices[face[1][0]-1]
            v2 = self.vertices[face[2][0]-1]

            u = helpers.subtract(v1, v0)
            v = helpers.subtract(v2, v0)
            normal = helpers.cross(u, v)
            w = [n / helpers.dot(normal, normal) for n in normal]
            denom = helpers.dot(normal, ray_dir)

            if abs(denom) < 1e-9:
                continue
            # test_list = [-1 * d for d in ray_dir]
            # norm = list(self.normals[face[0][2]-1])
            # if norm != test_list:
            #     print(test_list)
            #     continue
            t = helpers.dot(helpers.subtract(v0, ray_origin), normal) / denom
            intersecion = helpers.add(ray_origin, (t*rd for rd in ray_dir))
            hitpoint = helpers.subtract(intersecion, v0)
            alpha = helpers.dot(w, helpers.cross(hitpoint, v)) #możliwa zamiana u i v
            beta = helpers.dot(w, helpers.cross(u, hitpoint))
            if alpha < 0 or beta < 0:
                continue
            if alpha + beta > 1:
                continue
            if alpha >=0 and alpha <= 1 and beta >= 0 and beta <= 1:
                return (t, alpha, beta)
            return None
