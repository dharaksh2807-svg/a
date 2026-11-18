import bpy

blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)

with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.objects = [
        "GEO-body_female_realistic",
        "GEO-head_animation_realistic",
        "GEO-head_sculpting_realistic"
    ]

for obj in data_to.objects:
    bpy.context.scene.collection.objects.link(obj)

for name in ["GEO-body_female_realistic", "GEO-head_animation_realistic", "GEO-head_sculpting_realistic"]:
    obj = bpy.data.objects[name]
    me = obj.data
    # count faces with vertex z > 1.3 for body or overall for head
    print(f"\n{name}:")
    print(f"Total verts: {len(me.vertices)}, Total faces: {len(me.polygons)}")
    # check face sets or vertex groups
    print(f"Face sets count in mesh attributes: {[a.name for a in me.attributes]}")
