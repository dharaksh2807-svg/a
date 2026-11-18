import bpy

bpy.ops.wm.open_mainfile(filepath="production_v3/prototype/nyra_head_prototype.blend")
obj = bpy.data.objects["GEO-body_female_realistic"]

# Check evaluated mesh in depsgraph with shape key active
dg = bpy.context.evaluated_depsgraph_get()
eval_obj = obj.evaluated_get(dg)
eval_mesh = eval_obj.to_mesh()

print(f"Evaluated mesh verts: {len(eval_mesh.vertices)}")
# Compare a landmark vertex (e.g. nose tip index 8014)
orig_nose = obj.data.vertices[8014].co
eval_nose = eval_mesh.vertices[8014].co
print(f"Original base mesh nose tip: {orig_nose}")
print(f"Evaluated nose tip: {eval_nose}")
print(f"Difference: {(eval_nose - orig_nose).length * 1000:.2f} mm")

eval_obj.to_mesh_clear()
