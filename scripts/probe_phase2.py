import bpy,json
from mathutils import Vector
out={}
for o in bpy.data.objects:
 if o.name.startswith('GEO-') and o.type=='MESH':
  v=[o.matrix_world@x.co for x in o.data.vertices]
  out[o.name]={'min':[min(x[i] for x in v) for i in range(3)],'max':[max(x[i] for x in v) for i in range(3)],'matrix':[list(r) for r in o.matrix_world],'keys':[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []}
rig=bpy.data.objects['RIG-rain']
out['bones']=[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones if any(x in b.name.lower() for x in ['fk-upper','fk-fore','fk-hand','fk-thigh','fk-shin','neck','head']) and not b.name.startswith(('MCH','ORG','DEF'))]
for name in ['MAT-rain.body','MAT-rain.eyes','MAT-rain.hair']:
 m=bpy.data.materials[name];out[name]=[{'name':n.name,'type':n.type,'inputs':[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]} for n in m.node_tree.nodes]
print(json.dumps(out,indent=2))
