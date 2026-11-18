import bpy

bpy.ops.wm.open_mainfile(filepath="production_v3/prototype/nyra_head_prototype.blend")

print("Objects in scene:")
for obj in bpy.data.objects:
    print(f" - {obj.name} (type={obj.type}, loc={obj.location})")
    if obj.type == 'MESH':
        print(f"   verts={len(obj.data.vertices)}, faces={len(obj.data.polygons)}")
        if obj.data.shape_keys:
            print("   Shape keys:", [kb.name for kb in obj.data.shape_keys.key_blocks])
        print("   Materials:", [m.name for m in obj.data.materials if m])
