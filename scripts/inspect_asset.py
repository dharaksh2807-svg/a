"""Inspect the currently opened asset without executing its embedded Python."""
import bpy
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
data = {'file':bpy.data.filepath,'blender':bpy.app.version_string,
        'file_version':list(bpy.data.version), 'objects':[],
        'images':[{'name':i.name,'path':i.filepath,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images],
        'texts':[{'name':t.name,'lines':len(t.lines),'use_module':t.use_module} for t in bpy.data.texts],
        'libraries':[l.filepath for l in bpy.data.libraries]}
for obj in bpy.data.objects:
    item = {'name':obj.name,'type':obj.type,'hide_render':obj.hide_render,'visible':obj.visible_get(),'dimensions':list(obj.dimensions)}
    if obj.type == 'MESH':
        obj.data.calc_loop_triangles()
        item.update(vertices=len(obj.data.vertices),triangles=len(obj.data.loop_triangles),
            materials=[m.name if m else None for m in obj.data.materials],
            modifiers=[{'name':m.name,'type':m.type,'levels':getattr(m,'levels',None),'render_levels':getattr(m,'render_levels',None)} for m in obj.modifiers],
            shape_keys=len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0)
    if obj.type == 'ARMATURE':
        item.update(bones=len(obj.data.bones),deform_bones=sum(b.use_deform for b in obj.data.bones),
            constraints=sum(len(p.constraints) for p in obj.pose.bones),
            bbone_segment_max=max((b.bbone_segments for b in obj.data.bones),default=0))
    data['objects'].append(item)
data['drivers'] = sum(len(d.animation_data.drivers) for group in (bpy.data.objects,bpy.data.meshes,bpy.data.shape_keys,bpy.data.materials) for d in group if d.animation_data)
(ROOT/'qa/evidence/rain-inspection.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
