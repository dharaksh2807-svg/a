import bpy
import mathutils

blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)

with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.objects = [
        "GEO-body_female_realistic",
        "GEO-body_female_realistic.eye.L",
        "GEO-body_female_realistic.eye.R"
    ]

body = data_to.objects[0]
eye_l = data_to.objects[1]
eye_r = data_to.objects[2]

for o in [body, eye_l, eye_r]:
    bpy.context.scene.collection.objects.link(o)

# Let's shift body from (-1.3401, 0, 0) to (0, 0, 0)
offset = mathutils.Vector((-body.location.x, -body.location.y, -body.location.z))
body.location += offset

# Since eyes have parent = body, let's check their world matrix
bpy.context.view_layer.update()
print("Body world loc:", body.matrix_world.translation)
print("Eye L world loc:", eye_l.matrix_world.translation)
print("Eye R world loc:", eye_r.matrix_world.translation)
