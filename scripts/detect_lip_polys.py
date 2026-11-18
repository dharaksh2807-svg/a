import bpy

bpy.ops.wm.open_mainfile(filepath="production_v3/prototype/nyra_head_prototype.blend")
obj = bpy.data.objects["GEO-body_female_realistic"]
me = obj.data

print("Total vertices:", len(me.vertices))
print("Total polygons:", len(me.polygons))

# Find lip polygons: polygons where all vertices have Z between 1.43 and 1.47, and Y < -0.14, and |X| < 0.035
lip_polys = []
for p in me.polygons:
    p_verts = [me.vertices[i] for i in p.vertices]
    if all(1.428 < v.co.z < 1.478 and v.co.y < -0.138 and abs(v.co.x) < 0.032 for v in p_verts):
        lip_polys.append(p.index)

print(f"Detected lip polygons count: {len(lip_polys)}")
