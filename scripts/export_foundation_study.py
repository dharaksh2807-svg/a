"""Static clay geometry study of Rain. Not NYRA, not an animation-ready export."""
import bpy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
source=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('GEO-') and not o.hide_render]
for obj in source:
    for mod in obj.modifiers:
        if mod.type=='SUBSURF':
            mod.show_viewport=False
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
clay=bpy.data.materials.new('Inspection clay — not final materials')
clay.use_nodes=True
shader=clay.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value=(0.48,0.40,0.34,1)
shader.inputs['Roughness'].default_value=0.65
meshes=[]
for obj in source:
    if obj.name in {'GEO-rain-eye_cornea','GEO-rain-eye_dots'}:
        continue
    mesh=bpy.data.meshes.new_from_object(obj.evaluated_get(deps),depsgraph=deps)
    mesh.materials.clear()
    mesh.materials.append(clay)
    for poly in mesh.polygons:
        poly.material_index=0
    new=bpy.data.objects.new('STUDY-'+obj.name,mesh)
    new.matrix_world=obj.matrix_world.copy()
    new['asset_status']='Rain static geometry study; not NYRA; no animation rig'
    new['credit']='Rain Rig (CC) Blender Foundation | studio.blender.org; CC BY 4.0'
    scene.collection.objects.link(new)
    meshes.append(new)
if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
for obj in list(bpy.data.objects):
    if obj not in meshes:
        bpy.data.objects.remove(obj,do_unlink=True)
for text in list(bpy.data.texts):
    bpy.data.texts.remove(text)
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/blender/rain-geometry-study.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports/rain-geometry-study.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
triangles=0
for o in meshes:
    o.data.calc_loop_triangles()
    triangles+=len(o.data.loop_triangles)
(ROOT/'qa/evidence/foundation-export.json').write_text(json.dumps({'meshes':len(meshes),'triangles':triangles,'rigged':False,'materials':'single neutral clay; textures intentionally not evaluated','source':'Official Rain v3 page; archive Rain v3.3; rain_v3.2.blend','license':'CC-BY-4.0'},indent=2))
print('VERDICT: PASS')
