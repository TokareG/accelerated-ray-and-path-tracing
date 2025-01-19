
class ObjReader:

    @staticmethod
    def import_obj(filename):
        objects = {}
        with open(filename) as f:
            obj_name = None
            for line in f:
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                if values[0] == 'o':
                    obj_name = values[1]
                    objects[obj_name] = {
                        "vertices": [],
                        "normals": [],
                        "faces": []
                    }
                if values[0] == 'v':
                    v = tuple(map(float, values[1:4]))
                    objects[obj_name]["vertices"].append(v)
                elif values[0] == 'vn':
                    v = tuple(map(float, values[1:4]))
                    objects[obj_name]["normals"].append(v)
                elif values[0] == 'f':
                    face = []
                    for v in values[1:]:
                        w = v.split('/')
                        face.append((int(w[0]),int(w[1]) if len(w) >= 2 else 0,int(w[2]) if len(w) >= 3 else 0))
                    objects[obj_name]["faces"].append(face)
        return objects
