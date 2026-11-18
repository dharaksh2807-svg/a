import bpy

blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)

with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.objects = [
        "GEO-body_female_realistic",
        "GEO-body_female_realistic.eye.L",
        "GEO-body_female_realistic.eye.R"
    ]

for o in data_to.objects:
    print(o.name, "loc:", o.location, "parent:", o.parent)
