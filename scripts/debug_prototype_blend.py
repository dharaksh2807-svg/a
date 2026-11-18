import bpy

bpy.ops.wm.open_mainfile(filepath="production_v3/prototype/nyra_head_prototype.blend")
obj = bpy.data.objects["GEO-body_female_realistic"]
print("Shape keys on object:")
if obj.data.shape_keys:
    for kb in obj.data.shape_keys.key_blocks:
        print(f" - {kb.name}: value={kb.value}")
else:
    print("NO SHAPE KEYS FOUND!")

for m in obj.modifiers:
    print(f"Modifier: {m.name} ({m.type}), show_viewport={m.show_viewport}, show_render={m.show_render}")

# Check vertex coordinates of basis vs master prototype
me = obj.data
basis = obj.data.shape_keys.key_blocks["Basis"]
master = obj.data.shape_keys.key_blocks["NYRA_Master_Prototype"]
diff_count = sum(1 for v1, v2 in zip(basis.data, master.data) if (v1.co - v2.co).length > 0.0001)
print(f"Number of displaced vertices in NYRA_Master_Prototype: {diff_count}")
max_disp = max((v1.co - v2.co).length for v1, v2 in zip(basis.data, master.data))
print(f"Max displacement: {max_disp * 1000:.2f} mm")
