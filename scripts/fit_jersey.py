import bpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];dg=bpy.context.evaluated_depsgraph_get()
verts=[];faces=[]
for name in ['NYRA · anatomy','NYRA · face identity']:
 o=bpy.data.objects[name];m=o.evaluated_get(dg).to_mesh();base=len(verts);verts.extend(o.matrix_world@v.co for v in m.vertices);faces.extend(tuple(i+base for i in p.vertices) for p in m.polygons);o.evaluated_get(dg).to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces)
o=bpy.data.objects['NYRA · continuous jersey chest inset']
for v in o.data.vertices:
 hit=bvh.ray_cast(Vector((v.co.x,-1,v.co.z)),Vector((0,1,0)))
 if hit[0]:
  offset=.0015 if v.co.z<1.375 else .004
  v.co=hit[0]+hit[1]*offset
 else:
  t=max(0,min(1,(v.co.z-1.395)/.04));v.co.y=-.105*(1-t)-.071*t
bpy.context.scene['phase2_finish_version']=3
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/blender/nyra/nyra-visual.blend'),compress=True)
