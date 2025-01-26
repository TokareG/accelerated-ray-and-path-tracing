from core.Ray import Ray
from models import Triangle
from core.Utils import sub



def aabb_hit(ray: Ray, bounding_box_min: list[float], bounding_box_max: list[float]) -> bool:
    """
    Determines whether a given ray intersects with an AABB.

    Parameters:
        ray (Ray): The ray to test for intersection.
        bounding_box_min (list of float): The minimum (x, y, z) coordinates of the bounding box.
        bounding_box_max (list of float): The maximum (x, y, z) coordinates of the bounding box.

    Returns:
        bool: True if the ray intersects the bounding box, False otherwise.
    """
    tmin = ray.t_min
    tmax = ray.t_max
    for i in range(3):
        adinv = 1.0 / (ray.direction[i] if abs(ray.direction[i]) > 1e-8 else 1e-8)
        t0 = (bounding_box_min[i] - ray.origin[i]) * adinv
        t1 = (bounding_box_max[i] - ray.origin[i]) * adinv
        if t0<t1:
            if(t0>tmin): tmin=t0
            if(t1<tmax): tmax=t1
        else:
            if(t0<tmax): tmax=t0
            if(t1>tmin): tmin=t1
        if tmax <= tmin:
            return False
    return True


def get_triangle_bbox(tri: Triangle):
    """
    Calculates the AABB for a given triangle.

    Parameters:
        tri (Triangle): The triangle for which to compute the bounding box.

    Returns:
        tuple: A tuple containing two lists:
            - bounding_box_min (list of float): The minimum (x, y, z) coordinates of the bounding box.
            - bounding_box_max (list of float): The maximum (x, y, z) coordinates of the bounding box.
    """
    xs = [tri.v0[0], tri.v1[0], tri.v2[0]]
    ys = [tri.v0[1], tri.v1[1], tri.v2[1]]
    zs = [tri.v0[2], tri.v1[2], tri.v2[2]]
    return (
        [min(xs), min(ys), min(zs)],
        [max(xs), max(ys), max(zs)]
    )



class BvhNode:
    """
    Represents a node within a Bounding Volume Hierarchy (BVH) tree, used to optimize ray-tracing operations.

    Attributes:
        faces (list of Triangle): The list of triangles contained in this node.
        left (BvhNode or None): The left child node.
        right (BvhNode or None): The right child node.
        is_leaf (bool): Indicates whether the node is a leaf node.
        bounding_box_min (list of float): The minimum (x, y, z) coordinates of the node's bounding box.
        bounding_box_max (list of float): The maximum (x, y, z) coordinates of the node's bounding box.
    """
    def __init__(self, faces: list[Triangle]):
        self.faces = faces
        self.left = None
        self.right = None
        self.is_leaf = False

        min_pt = [float('inf'), float('inf'), float('inf')]
        max_pt = [float('-inf'), float('-inf'), float('-inf')]
        for f in faces:
            tri_min, tri_max = get_triangle_bbox(f)
            for i in range(3):
                min_pt[i] = min(min_pt[i], tri_min[i])
                max_pt[i] = max(max_pt[i], tri_max[i])
        self.bounding_box_min = min_pt
        self.bounding_box_max = max_pt



def build_bvh(faces: list[Triangle], max_faces_in_leaf) -> BvhNode:
    """
    Constructs a Bounding Volume Hierarchy (BVH) tree from a list of triangles to accelerate ray intersection tests.

    Parameters:
        faces (list of Triangle): The list of triangles to include in the BVH.
        max_faces_in_leaf (int, optional): The maximum number of triangles allowed in a leaf node. Defaults to 4.

    Returns:
        BvhNode: The root node of the constructed BVH tree.
    """
    node = BvhNode(faces)

    if len(faces) <= max_faces_in_leaf:
        node.is_leaf = True
        return node

    bbox_size = sub(node.bounding_box_max, node.bounding_box_min)
    axis = bbox_size.index(max(bbox_size))
    faces.sort(key=lambda f: ((f.v0[axis] + f.v1[axis] + f.v2[axis]) / 3.0))
    mid = len(faces) // 2
    left_faces = faces[:mid]
    right_faces = faces[mid:]
    node.left = build_bvh(left_faces, max_faces_in_leaf)
    node.right = build_bvh(right_faces, max_faces_in_leaf)
    return node


def hit_bvh(ray: Ray, node: BvhNode):
    """
    Finds the closest intersection between a ray and the triangles contained within a BVH tree.

    Parameters:
        ray (Ray): The ray to test for intersections.
        node (BvhNode): The current node in the BVH tree being tested.

    Returns:
        tuple or None: If an intersection is found, returns a tuple (t, intersection_point, face) where:
            - t (float): The parameter value along the ray where the intersection occurs.
            - intersection_point (list of float): The (x, y, z) coordinates of the intersection point.
            - face (Triangle): The triangle that was intersected.
        If no intersection is found, returns None.
    """

    if not aabb_hit(ray, node.bounding_box_min, node.bounding_box_max):
        return None

    if node.is_leaf:
        closest_intersection = None
        for f in node.faces:
            res = f.hit(ray)
            if res:
                t, intersection_point, face = res
                if (ray.t_min <= t <= ray.t_max):
                    if not closest_intersection or t < closest_intersection[0]:
                        closest_intersection = (t, intersection_point, face)
        return closest_intersection


    hit_left = hit_bvh(ray, node.left) if node.left else None
    hit_right = hit_bvh(ray, node.right) if node.right else None

    if hit_left and hit_right:
        return hit_left if hit_left[0] < hit_right[0] else hit_right
    return hit_left if hit_left else hit_right


class MeshBvhNode:

    def __init__(self, meshes):
        self.meshes = meshes
        self.left = None
        self.right = None
        self.is_leaf = False

        min_pt = [float('inf'), float('inf'), float('inf')]
        max_pt = [float('-inf'), float('-inf'), float('-inf')]
        for mesh in meshes:
            for i in range(3):
                min_pt[i] = min(min_pt[i], mesh.bounding_box_min[i])
                max_pt[i] = max(max_pt[i], mesh.bounding_box_max[i])
        self.bounding_box_min = min_pt
        self.bounding_box_max = max_pt

def build_bvh_meshes(meshes, max_in_leaf=1) -> MeshBvhNode:
    node = MeshBvhNode(meshes)
    if len(meshes) <= max_in_leaf:
        node.is_leaf = True
        return node
    bbox_size = sub(node.bounding_box_max, node.bounding_box_min)
    axis = bbox_size.index(max(bbox_size))
    def mesh_centroid(mesh):
        cmin, cmax = mesh.bounding_box_min, mesh.bounding_box_max
        return (cmin[axis] + cmax[axis]) * 0.5

    meshes.sort(key=mesh_centroid)

    mid = len(meshes) // 2
    left_meshes  = meshes[:mid]
    right_meshes = meshes[mid:]

    node.left  = build_bvh_meshes(left_meshes,  max_in_leaf)
    node.right = build_bvh_meshes(right_meshes, max_in_leaf)
    return node

def hit_bvh_meshes(ray: Ray, node: MeshBvhNode):

    if not aabb_hit(ray, node.bounding_box_min, node.bounding_box_max):
        return None

    if node.is_leaf:

        closest_hit = None
        for mesh in node.meshes:
            if not aabb_hit(ray, mesh.bounding_box_min, mesh.bounding_box_max):
                continue

            for face in mesh.faces:
                res = face.hit(ray)
                if res:
                    t, intersection_point, face_obj = res
                    if ray.t_min <= t <= ray.t_max:
                        if (closest_hit is None) or (t < closest_hit[0]):
                            closest_hit = (t, intersection_point, face_obj)
        return closest_hit

    hit_left  = hit_bvh_meshes(ray, node.left)  if node.left  else None
    hit_right = hit_bvh_meshes(ray, node.right) if node.right else None

    if hit_left and hit_right:
        return hit_left if hit_left[0] < hit_right[0] else hit_right
    return hit_left if hit_left else hit_right