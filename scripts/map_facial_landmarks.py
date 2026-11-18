import bpy
import mathutils

blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)

with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.objects = ["GEO-body_female_realistic"]

body = data_to.objects[0]
body.location = (0, 0, 0)
bpy.context.scene.collection.objects.link(body)
bpy.context.view_layer.update()

me = body.data

# Find landmark bounding boxes for Z > 1.35
face_verts = [v for v in me.vertices if v.co.z > 1.35 and v.co.y < 0.0]
print(f"Total face/head vertices with Z > 1.35 and Y < 0: {len(face_verts)}")

min_x = min(v.co.x for v in face_verts)
max_x = max(v.co.x for v in face_verts)
min_y = min(v.co.y for v in face_verts)
max_y = max(v.co.y for v in face_verts)
min_z = min(v.co.z for v in face_verts)
max_z = max(v.co.z for v in face_verts)
print(f"Face bounds: X=[{min_x:.3f}, {max_x:.3f}], Y=[{min_y:.3f}, {max_y:.3f}], Z=[{min_z:.3f}, {max_z:.3f}]")

# Key facial landmarks in the baseline mesh:
# Nose tip: lowest Y with Z between 1.48 and 1.54
nose_tip = min((v for v in face_verts if 1.48 < v.co.z < 1.54), key=lambda v: v.co.y)
print(f"Nose tip: index={nose_tip.index}, co=({nose_tip.co.x:.4f}, {nose_tip.co.y:.4f}, {nose_tip.co.z:.4f})")

# Chin apex: lowest Y with Z between 1.35 and 1.42
chin_tip = min((v for v in face_verts if 1.35 < v.co.z < 1.42), key=lambda v: v.co.y)
print(f"Chin apex: index={chin_tip.index}, co=({chin_tip.co.x:.4f}, {chin_tip.co.y:.4f}, {chin_tip.co.z:.4f})")

# Mouth center (lip junction): Y < -0.08, Z between 1.42 and 1.46
mouth_center = min((v for v in face_verts if 1.42 < v.co.z < 1.46 and abs(v.co.x) < 0.01), key=lambda v: v.co.y)
print(f"Mouth center: index={mouth_center.index}, co=({mouth_center.co.x:.4f}, {mouth_center.co.y:.4f}, {mouth_center.co.z:.4f})")

# Eye center: around Z=1.53, Y=-0.11, X=0.033
eye_region = [v for v in face_verts if 1.51 < v.co.z < 1.56 and 0.02 < v.co.x < 0.06 and v.co.y < -0.09]
print(f"Eye region vertices count: {len(eye_region)}")

# Cheekbone apex: around Z=1.50 to 1.53, X=0.05 to 0.075, Y=-0.08 to -0.04
cheek_region = [v for v in face_verts if 1.48 < v.co.z < 1.54 and 0.045 < abs(v.co.x) < 0.08 and v.co.y < -0.04]
print(f"Cheek region vertices count: {len(cheek_region)}")
