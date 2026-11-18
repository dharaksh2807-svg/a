import bpy

blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"

# Load the realistic female body collection and objects
with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.collections = [c for c in data_from.collections if "Female - Realistic" in c or "Head (Sculpting)" in c or "Head (Animation)" in c]
    data_to.objects = [o for o in data_from.objects if "body_female_realistic" in o or "head_sculpt" in o or "head_anim" in o]

print("Loaded collections:", [c.name for c in data_to.collections])
print("Loaded objects:", [o.name for o in data_to.objects])

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        me = obj.data
        print(f"\nObject: {obj.name}")
        print(f" - Vertices: {len(me.vertices)}")
        print(f" - Edges: {len(me.edges)}")
        print(f" - Polygons: {len(me.polygons)}")
        non_quads = sum(1 for p in me.polygons if len(p.vertices) != 4)
        print(f" - Non-quad polygons: {non_quads}")
        print(f" - Modifiers: {[m.name + ' (' + m.type + ')' for m in obj.modifiers]}")
        print(f" - Vertex groups: {[vg.name for vg in obj.vertex_groups]}")
        print(f" - Shape keys: {obj.data.shape_keys.key_blocks.keys() if obj.data.shape_keys else 'None'}")
        print(f" - UV layers: {[uv.name for uv in me.uv_layers]}")
