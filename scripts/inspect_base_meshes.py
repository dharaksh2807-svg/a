import bpy

blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
print("=== INSPECTING HUMAN BASE MESHES BUNDLE ===")

with bpy.data.libraries.load(blend_path) as (data_from, data_to):
    print("Objects in library:", len(data_from.objects))
    for obj_name in sorted(data_from.objects):
        print(" -", obj_name)
    print("Collections in library:", len(data_from.collections))
    for col_name in sorted(data_from.collections):
        print(" - Col:", col_name)
