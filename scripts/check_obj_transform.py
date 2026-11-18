import bpy
import mathutils

blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)

with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.objects = ["GEO-body_female_realistic"]

obj = data_to.objects[0]
print("Location:", obj.location)
print("Rotation:", obj.rotation_euler)
print("Scale:", obj.scale)
bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
xs = [b.x for b in bbox]
ys = [b.y for b in bbox]
zs = [b.z for b in bbox]
print(f"X: {min(xs):.3f} to {max(xs):.3f}")
print(f"Y: {min(ys):.3f} to {max(ys):.3f}")
print(f"Z: {min(zs):.3f} to {max(zs):.3f}")
