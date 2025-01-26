from core.Utils import Utils
from core.Ray import Ray
from statistics import median
from copy import deepcopy
from models.Triangle import Triangle


class KdTreeNode:
    _MAX_DEPTH = 6

    def __init__(self, obj_list: list[Triangle], depth: int, bbox: tuple[list[float], list[float]]):
        self.depth = depth
        self.meshes_list = obj_list
        self.bbox = deepcopy(bbox)  # needed, cause python tries to be smarter than its programmers

        if self._is_splitable():
            left, right = self._split_bbox_and_list()  # tuples -> (bbox, mesh_list)
            self.left_child = KdTreeNode(obj_list=left[1], depth=self.depth + 1, bbox=left[0])
            self.right_child = KdTreeNode(obj_list=right[1], depth=self.depth + 1, bbox=right[0])
            self.is_leaf = False

        else:
            self.left_child = None
            self.right_child = None
            self.is_leaf = True

    def _split_bbox_and_list(self):
        coords = [[], [], []]  # all mesh points coordinates list

        for mesh in self.meshes_list:
            coords[0] += [mesh.v0[0], mesh.v1[0], mesh.v2[0]]  # x
            coords[1] += [mesh.v0[1], mesh.v1[1], mesh.v2[1]]  # y
            coords[2] += [mesh.v0[2], mesh.v1[2], mesh.v2[2]]  # z

        bbox_lengths = [abs(length_) for length_ in Utils.sub(self.bbox[1], self.bbox[0])]
        side_idx = bbox_lengths.index(max(bbox_lengths))  # index of the longest side
        new_pos = median(coords[side_idx])  # little offset to not always include the same mesh twice

        # So when splitting a 3D bbox into two halves by splitting, we move either the upper bound point for left bbox
        # or the lower bound point for right bbox. These points are moved by updating the value of side, where the split
        # is happenning; so if we split along x-axis, we will update only x coordinates for those points.
        l_bbox = deepcopy(self.bbox)
        l_bbox[1][side_idx] = new_pos
        r_bbox = deepcopy(self.bbox)
        r_bbox[0][side_idx] = new_pos
        self.new_point = r_bbox[0]  # for ease-of-use in finding bbox hits

        # Assign meshes according to their split coordinate value. If lower than split value, move left. If higher, move
        # right. Please note, that for KD-Tree, one mesh can be added to both boundingboxes, if at least one point of
        # mesh is a member.
        l_list = []
        r_list = []
        for mesh in self.meshes_list:
            if any(point_coords <= new_pos for point_coords in [mesh.v0[side_idx], mesh.v1[side_idx], mesh.v2[side_idx]]):
                l_list.append(mesh)

            if any(point_coords >= new_pos for point_coords in [mesh.v0[side_idx], mesh.v1[side_idx], mesh.v2[side_idx]]):
                r_list.append(mesh)

        return (l_bbox, l_list), (r_bbox, r_list)

    def _is_splitable(self):
        return True if 1 < len(self.meshes_list) and self._MAX_DEPTH > self.depth else False

    def traverse_tree(self, ray: Ray):
        tmin = ray.t_min
        tmax = ray.t_max
        closest_intersection = None

        for i in range(3):
            adinv = 1.0 / (ray.direction[i] if abs(ray.direction[i]) > 1e-8 else 1e-8)
            t0 = (self.bbox[0][i] - ray.origin[i]) * adinv
            t1 = (self.bbox[1][i] - ray.origin[i]) * adinv
            t = (self.new_point[i] - ray.origin[i]) * adinv if not self.is_leaf else None

            # update min-max t-values
            if t0 < t1:
                if t0 > tmin: tmin = t0
                if t1 < tmax: tmax = t1
            else:
                if t0 < tmax: tmax = t0
                if t1 > tmin: tmin = t1

            # 0. if no hit -> break
            if tmax <= tmin:
                return None


        # 1. if at leaf, check all meshes
        if self.is_leaf:
            closest_intersection = None  # if no meshes hit, we return no hit

            for mesh in self.meshes_list:
                res = mesh.hit(ray)
                if res:
                    t, intersection_point, face = res

                    if ray.t_min <= t <= ray.t_max:
                        if not closest_intersection or t < closest_intersection[0]:
                            closest_intersection = (t, intersection_point, face)
            return closest_intersection

        # 2. check left child
        hit_left = self.left_child.traverse_tree(ray)

        # 3. check right child, but only if left unfound, assign to return variable
        closest_intersection = self.right_child.traverse_tree(ray) if not hit_left else hit_left

        return closest_intersection

    @staticmethod
    def create_meshlist_bbox(mesh_list):
        mesh_coords = [[], [], []]
        for mesh in mesh_list:
            mesh_coords[0] += [mesh.v0[0], mesh.v1[0], mesh.v2[0]]
            mesh_coords[1] += [mesh.v0[1], mesh.v1[1], mesh.v2[1]]
            mesh_coords[2] += [mesh.v0[2], mesh.v1[2], mesh.v2[2]]

        return (
            [min(mesh_coords[0]), min(mesh_coords[1]), min(mesh_coords[2])],
            [max(mesh_coords[0]), max(mesh_coords[1]), max(mesh_coords[2])]
            )
