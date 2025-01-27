from core.Utils import Utils
from core.Ray import Ray
from statistics import median
from copy import deepcopy
from models.Triangle import Triangle


class KdTreeNode:
    """Implement KD-Tree boosting structure for the ray tracer

    The __init__ method may be documented in either the class level
    docstring, or as a docstring on the __init__ method itself.

    Either form is acceptable, but the two should not be mixed. Choose one
    convention to document the __init__ method and be consistent with it.

    Note
    ----
    > Do not increase the _MAX_DEPTH parameter very much, as it causes the render to crash.
    > bbox is specified as seperate parameter rather than constructed at init, because it's created by parent node and
      passed down to children.

    Parameters
    ----------
    obj_list : list[Triangle]
        List containing all the triangle meshes that are considered for bounding box at that depth level.
        For root node, this list consists of all the meshes on the scene.
    depth : int
        Denotes current depth level, incremented by 1 with each child. Limited by _MAX_DEPTH. For root node, depth
        parameter should be equal to 0, but if you want to limit depth without modifying _MAX_DEPTH, you can do that
        by specifying depth parameter as higher.
    bbox : tuple[list[float], list[float]]
        Bounding box containing all the elements of obj_list. It consists of two three-element float list, each list
        specifies accordingly lower bound point and upper bound point

    Attributes
    ----------
    depth : int
        see parameter depth
    meshes_list : list[Triangle]
        see parameter obj_list
    bbox : tuple[list[float], list[float]
        see parameter bbox
    first_child : KdTreeNode
        One of children of current KdTreeNode
    second_child : KdTreeNode
        One of children of current KdTreeNode
    is_leaf : Bool
        Flag that denotes if KdTreeNode is a terminal node

    """
    _MAX_DEPTH = 16

    def __init__(self, obj_list: list[Triangle], depth: int, bbox: tuple[list[float], list[float]]):
        self.depth = depth
        self.meshes_list = obj_list
        self.bbox = deepcopy(bbox)  # needed, cause python tries to be smarter than its programmers
        self.new_point = (-1, float('inf'))

        if self._is_splitable():
            left, right = self._split_bbox_and_list()  # tuples -> (bbox, mesh_list)
            self.first_child = KdTreeNode(obj_list=left[1], depth=self.depth + 1, bbox=left[0])
            self.second_child = KdTreeNode(obj_list=right[1], depth=self.depth + 1, bbox=right[0])
            self.is_leaf = False

        else:
            self.first_child = None
            self.second_child = None
            self.is_leaf = True

    def _split_bbox_and_list(self):
        """Split bounding box into two and create two lists of meshes for them

        For splitting a following strategy is used; firstly, the biggest side is chosen. For this side, all of the point
        coordinates are considered and have median value taken. This median value is the new value for side coordinate
        of lower bound and upper bound points for newly created bounding boxes.

        Returns
        -------
        tuple[tuple[list[float], list[float], list[Triangle]], tuple[tuple[list[float], list[float], list[Triangle]],
            Two tuples, containing newly created boundingboxes and their assigned list od meshes
        """
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
        self.new_point = (side_idx, new_pos)

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
        """Allows to travel down the Kd-tree to search for intersection with meshes

        Implementation based on Indo-Wald's https://arxiv.org/abs/2211.00120

        Traversing happens by following steps:
        > 0. check if node hit at all
        > 1. if node is a leaf -> check all the meshes for hits
        > 2. analyze backside child node -> node that is further from ray origin
        > 3. analyze frontside child node
        > 4. analyze both children in order: front, back. If hit is found, we can safely terminate.

        Returns
        -------
        tuple[float, list[float], Triangle],
            (t parameter of ray equation, intersection point coordinates, hit mesh object) OR None
        """
        ray_overall_tmin = ray.t_min
        ray_overall_tmax = ray.t_max

        r = (None, None, None)

        # 0. if on hit -> break
        for i in range(3):
            adinv = 1.0 / (ray.direction[i] if abs(ray.direction[i]) > 1e-8 else 1e-8)
            t0 = (self.bbox[0][i] - ray.origin[i]) * adinv
            t1 = (self.bbox[1][i] - ray.origin[i]) * adinv

            # store for later children order analysis
            if i == self.new_point[0]:
                r = (t0, t1, (self.new_point[1] - ray.origin[i]) * adinv)

            # update min-max t-values
            if t0 < t1:
                if t0 > ray_overall_tmin: ray_overall_tmin = t0
                if t1 < ray_overall_tmax: ray_overall_tmax = t1
            else:
                if t0 < ray_overall_tmax: ray_overall_tmax = t0
                if t1 > ray_overall_tmin: ray_overall_tmin = t1

            if ray_overall_tmax <= ray_overall_tmin:
                return None

        # 'new_pos' = median(point_coords[along_specified_axis]) change parameter explained
        # so when splitting into two boundingboxes, we change one of the coordinates of corner by 'new_pos' or
        # '-new_pos' along one of three global axes. Thus, comparing t0 and t1 agains a change parameter
        #
        # t_new = t0 + r = t1 - r
        #
        # so now, using Ingo Wald's thesis we can say, which of the children is first!

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

        # unpack r parameter values of P(r)=Q+rd
        enter_point_parameter, leave_point_parameter, split_point_parameter = r

        # Next steps are:
        # 2. r_0 <= r_start <= r_end -> hit happens in backside node
        # 3. r_start <= r_end <= r_0 -> hit happens in frontside node
        # 4. r_start <= r_0 <= r_end -> hit happens in both child nodes
        #
        # if r_start >= r_end it means that hit happens from the other direction, so backside node becomes frontside and
        # so on.
        if enter_point_parameter < leave_point_parameter:

            if split_point_parameter <= enter_point_parameter:
                return self.second_child.traverse_tree(ray)

            elif split_point_parameter >= leave_point_parameter:
                return self.first_child.traverse_tree(ray)

            else:
                first_hit = self.first_child.traverse_tree(ray)
                return self.second_child.traverse_tree(ray) if not first_hit else first_hit

        else:
            if split_point_parameter <= leave_point_parameter:
                return self.first_child.traverse_tree(ray)

            elif split_point_parameter >= enter_point_parameter:
                return self.second_child.traverse_tree(ray)

            else:
                first_hit = self.second_child.traverse_tree(ray)
                return self.first_child.traverse_tree(ray) if not first_hit else first_hit

    @staticmethod
    def create_meshlist_bbox(mesh_list):
        """Create bounding box that overlap all the meshes inside input list

        Used to create bounding box for tree root, as bboxes for children nodes are provided by parent node

        Returns
        -------
        tuple[list[float], list[float]]
            lower bound and upper bound point coordinates for boundingboxes
        """
        mesh_coords = [[], [], []]
        for mesh in mesh_list:
            mesh_coords[0] += [mesh.v0[0], mesh.v1[0], mesh.v2[0]]
            mesh_coords[1] += [mesh.v0[1], mesh.v1[1], mesh.v2[1]]
            mesh_coords[2] += [mesh.v0[2], mesh.v1[2], mesh.v2[2]]

        return (
            [min(mesh_coords[0]), min(mesh_coords[1]), min(mesh_coords[2])],
            [max(mesh_coords[0]), max(mesh_coords[1]), max(mesh_coords[2])]
            )
