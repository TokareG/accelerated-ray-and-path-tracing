from typing import List, Tuple
from core.Ray import Ray
from models.Triangle import Triangle

class UniformGrid:
    """
    Class storing information about a uniform grid:
      - bounding_box_min and bounding_box_max
      - inv_cell_size
      - resolution (nx, ny, nz)
      - cells -> {(ix, iy, iz): [triangles]}
    """
    def __init__(self,
                 bounding_box_min: List[float],
                 bounding_box_max: List[float],
                 resolution: Tuple[int,int,int],
                 cells):
        self.bounding_box_min = bounding_box_min
        self.bounding_box_max = bounding_box_max
        self.resolution = resolution
        self.cells = cells

        size_x = bounding_box_max[0] - bounding_box_min[0]
        size_y = bounding_box_max[1] - bounding_box_min[1]
        size_z = bounding_box_max[2] - bounding_box_min[2]

        nx, ny, nz = resolution
        self.cell_size = (
            size_x / nx if nx > 0 else 1e-3,
            size_y / ny if ny > 0 else 1e-3,
            size_z / nz if nz > 0 else 1e-3,
        )
        self.inv_cell_size = (
            1.0 / self.cell_size[0] if self.cell_size[0] else 1e3,
            1.0 / self.cell_size[1] if self.cell_size[1] else 1e3,
            1.0 / self.cell_size[2] if self.cell_size[2] else 1e3,
        )


def build_grid(faces: List[Triangle], desired_resolution: int = 20) -> UniformGrid:
    if not faces:
        return UniformGrid([0,0,0], [0,0,0], (1,1,1), {})

    global_min = [float('inf')] * 3
    global_max = [float('-inf')] * 3
    for tri in faces:
        tri_min, tri_max = get_triangle_bbox(tri)
        for i in range(3):
            if tri_min[i] < global_min[i]:
                global_min[i] = tri_min[i]
            if tri_max[i] > global_max[i]:
                global_max[i] = tri_max[i]

    padding = 1e-3
    global_min = [gm - padding for gm in global_min]
    global_max = [gm + padding for gm in global_max]

    size_x = global_max[0] - global_min[0]
    size_y = global_max[1] - global_min[1]
    size_z = global_max[2] - global_min[2]

    if max(size_x, size_y, size_z) < 1e-8:
        resolution = (1,1,1)
    else:
        nx = max(1, desired_resolution)
        ny = max(1, int(nx * size_y / size_x)) if size_x > 0 else 1
        nz = max(1, int(nx * size_z / size_x)) if size_x > 0 else 1

        max_dim = max(size_x, size_y, size_z)
        if size_y == max_dim:
            ny = desired_resolution
            nx = max(1, int(ny * size_x / size_y))
            nz = max(1, int(ny * size_z / size_y))
        elif size_z == max_dim:
            nz = desired_resolution
            nx = max(1, int(nz * size_x / size_z))
            ny = max(1, int(nz * size_y / size_z))

        resolution = (nx, ny, nz)

    cells = {}
    for tri in faces:
        tri_min, tri_max = get_triangle_bbox(tri)
        min_ix, min_iy, min_iz = point_to_grid_index(tri_min, global_min, global_max, resolution)
        max_ix, max_iy, max_iz = point_to_grid_index(tri_max, global_min, global_max, resolution)
        if min_ix > max_ix:
            min_ix, max_ix = max_ix, min_ix
        if min_iy > max_iy:
            min_iy, max_iy = max_iy, min_iy
        if min_iz > max_iz:
            min_iz, max_iz = max_iz, min_iz

        nx, ny, nz = resolution
        for ix in range(min_ix, max_ix + 1):
            if ix < 0 or ix >= nx:
                continue
            for iy in range(min_iy, max_iy + 1):
                if iy < 0 or iy >= ny:
                    continue
                for iz in range(min_iz, max_iz + 1):
                    if iz < 0 or iz >= nz:
                        continue
                    cells.setdefault((ix, iy, iz), []).append(tri)

    return UniformGrid(global_min, global_max, resolution, cells)


def hit_grid(ray: Ray, grid: UniformGrid):
    if not aabb_hit(ray, grid.bounding_box_min, grid.bounding_box_max):
        return None

    t_bounds = compute_entry_exit_times(ray, grid.bounding_box_min, grid.bounding_box_max,
                                        ray.t_min, ray.t_max)
    if not t_bounds:
        return None
    t_enter, t_exit = t_bounds
    p_enter = ray.at(t_enter)
    ix, iy, iz = point_to_grid_index(p_enter, grid.bounding_box_min,
                                     grid.bounding_box_max, grid.resolution)

    dirx, diry, dirz = ray.direction
    step_x = 1 if dirx >= 0 else -1
    step_y = 1 if diry >= 0 else -1
    step_z = 1 if dirz >= 0 else -1

    origin_x, origin_y, origin_z = ray.origin
    tNextX, dtX = compute_t_and_dt(origin_x, dirx, ix, step_x,
                                   grid.bounding_box_min[0],
                                   grid.cell_size[0])
    tNextY, dtY = compute_t_and_dt(origin_y, diry, iy, step_y,
                                   grid.bounding_box_min[1],
                                   grid.cell_size[1])
    tNextZ, dtZ = compute_t_and_dt(origin_z, dirz, iz, step_z,
                                   grid.bounding_box_min[2],
                                   grid.cell_size[2])

    while tNextX < t_enter:
        tNextX += dtX
    while tNextY < t_enter:
        tNextY += dtY
    while tNextZ < t_enter:
        tNextZ += dtZ

    closest_hit = None
    current_t = t_enter

    nx, ny, nz = grid.resolution
    while current_t <= t_exit:
        if 0 <= ix < nx and 0 <= iy < ny and 0 <= iz < nz:
            cell_triangles = grid.cells.get((ix, iy, iz), [])
            for tri in cell_triangles:
                res = tri.hit(ray)
                if res:
                    t_hit, pt, face = res
                    if ray.t_min <= t_hit <= ray.t_max:
                        if (closest_hit is None) or (t_hit < closest_hit[0]):
                            closest_hit = (t_hit, pt, face)

        if tNextX < tNextY and tNextX < tNextZ:
            ix += step_x
            current_t = tNextX
            tNextX += dtX
        elif tNextY < tNextZ:
            iy += step_y
            current_t = tNextY
            tNextY += dtY
        else:
            iz += step_z
            current_t = tNextZ
            tNextZ += dtZ

        if ix < 0 or ix >= nx or iy < 0 or iy >= ny or iz < 0 or iz >= nz:
            break
        if current_t > t_exit:
            break

    return closest_hit


def get_triangle_bbox(tri: Triangle):
    xs = [tri.v0[0], tri.v1[0], tri.v2[0]]
    ys = [tri.v0[1], tri.v1[1], tri.v2[1]]
    zs = [tri.v0[2], tri.v1[2], tri.v2[2]]
    return ([min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)])


def point_to_grid_index(point: List[float],
                        box_min: List[float],
                        box_max: List[float],
                        resolution: Tuple[int,int,int]) -> Tuple[int,int,int]:
    nx, ny, nz = resolution
    size_x = box_max[0] - box_min[0]
    size_y = box_max[1] - box_min[1]
    size_z = box_max[2] - box_min[2]

    dx = point[0] - box_min[0]
    dy = point[1] - box_min[1]
    dz = point[2] - box_min[2]

    fx = dx / size_x if abs(size_x) > 1e-8 else 0
    fy = dy / size_y if abs(size_y) > 1e-8 else 0
    fz = dz / size_z if abs(size_z) > 1e-8 else 0

    ix = int(fx * nx)
    iy = int(fy * ny)
    iz = int(fz * nz)
    return (ix, iy, iz)


def aabb_hit(ray: Ray, box_min: List[float], box_max: List[float]) -> bool:
    tmin = ray.t_min
    tmax = ray.t_max
    for i in range(3):
        origin_comp = ray.origin[i]
        dir_comp = ray.direction[i]
        if abs(dir_comp) < 1e-9:
            if origin_comp < box_min[i] or origin_comp > box_max[i]:
                return False
        else:
            invD = 1.0 / dir_comp
            t0 = (box_min[i] - origin_comp) * invD
            t1 = (box_max[i] - origin_comp) * invD
            if t0 > t1:
                t0, t1 = t1, t0
            if t0 > tmin:
                tmin = t0
            if t1 < tmax:
                tmax = t1
            if tmax <= tmin:
                return False
    return True


def compute_entry_exit_times(ray: Ray, box_min: List[float], box_max: List[float],
                             tmin: float, tmax: float):
    for i in range(3):
        origin = ray.origin[i]
        direction = ray.direction[i]
        if abs(direction) < 1e-9:
            if origin < box_min[i] or origin > box_max[i]:
                return None
        else:
            invD = 1.0 / direction
            t0 = (box_min[i] - origin) * invD
            t1 = (box_max[i] - origin) * invD
            if t0 > t1:
                t0, t1 = t1, t0
            if t0 > tmin:
                tmin = t0
            if t1 < tmax:
                tmax = t1
            if tmax <= tmin:
                return None
    return (tmin, tmax)


def compute_t_and_dt(origin, direction, cell_index, step, box_min_coord, cell_size):
    if abs(direction) < 1e-9:
        return (float('inf'), float('inf'))
    boundary_coord = (cell_index + (1 if step > 0 else 0)) * cell_size + box_min_coord
    tNext = (boundary_coord - origin) / direction
    dt = cell_size / abs(direction)
    return (tNext, dt)