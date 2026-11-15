import bpy,json
from pathlib import Path
r={};dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.collections['NYRA | EDITABLE VISUAL MODEL'].objects:
 e=o.evaluated_get(dg);m=e.to_mesh();pts=[v.co for v in m.vertices]
 r[o.name]={'bounds':[[round(f(p[i] for p in pts),5) for i in range(3)] for f in [min,max]],'verts':len(m.vertices),'modifiers':[x.type for x in o.modifiers]};e.to_mesh_clear()
head=bpy.data.objects['NYRA · face identity'];r['face_keys']=[k.name for k in head.data.shape_keys.key_blocks]
Path('qa/phase3/basis-inspection.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
