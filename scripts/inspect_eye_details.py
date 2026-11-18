import bpy

bpy.ops.wm.open_mainfile(filepath="production_v3/prototype/nyra_head_prototype.blend")
eye = bpy.data.objects["GEO-body_female_realistic.eye.L"]
me = eye.data

print("Eye vertices:", len(me.vertices))
print("Eye polygons:", len(me.polygons))

# Bounding box of eye in local coords
xs = [v.co.x for v in me.vertices]
ys = [v.co.y for v in me.vertices]
zs = [v.co.z for v in me.vertices]
print(f"X: {min(xs):.4f} to {max(xs):.4f}")
print(f"Y: {min(ys):.4f} to {max(ys):.4f}")
print(f"Z: {min(zs):.4f} to {max(zs):.4f}")

# Look at UV coords
uv_layer = me.uv_layers.active.data
uvs = [(loop.uv.x, loop.uv.y) for loop in uv_layer]
print(f"UV U: {min(u[0] for u in uvs):.3f} to {max(u[0] for u in uvs):.3f}")
print(f"UV V: {min(u[1] for u in uvs):.3f} to {max(u[1] for u in uvs):.3f}")

# Front pole of eye
front_vert = min(me.vertices, key=lambda v: v.co.y)
print(f"Frontmost vertex (cornea center): co={front_vert.co}, index={front_vert.index}")
