import bpy

bpy.ops.wm.open_mainfile(filepath="production_v3/prototype/nyra_head_prototype.blend")

for name in ["GEO-body_female_realistic.eye.L", "GEO-body_female_realistic.eye.R"]:
    eye = bpy.data.objects[name]
    print(f"\n{name}:")
    print(" - world location:", eye.matrix_world.translation)
    print(" - parent:", eye.parent)
    print(" - dimensions:", eye.dimensions)
    me = eye.data
    print(" - UV layers:", [uv.name for uv in me.uv_layers])

# Also check head_animation eye parts from upstream bundle
blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.objects = [
        "GEO-head_animation_realistic.sclera.L",
        "GEO-head_animation_realistic.iris.L"
    ]

for obj in data_to.objects:
    print(f"\nUpstream {obj.name}:")
    print(" - dimensions:", obj.dimensions)
    print(" - UV layers:", [uv.name for uv in obj.data.uv_layers])
