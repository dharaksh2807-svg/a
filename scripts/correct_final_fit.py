"""Correct radial waist fitting using inward-to-outward torso rays; retain other edits."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];dg=bpy.context.evaluated_depsgraph_get()
def surface(names):
 verts=[];faces=[]
 for name in names:
  o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();base=len(verts)
  verts.extend(o.matrix_world@v.co for v in m.vertices);faces.extend(tuple(i+base for i in p.vertices) for p in m.polygons);e.to_mesh_clear()
 return BVHTree.FromPolygons(verts,faces)
waist=surface(['NYRA · anatomy','NYRA · tailored track pants'])
o=bpy.data.objects['NYRA · track waistband']
for v in o.data.vertices:
 c=Vector((0,-.015,v.co.z));d=v.co-c;d.z=0;d.normalize();h=waist.ray_cast(c,d,.24)
 if h[0]:v.co=h[0]+d*.003
 else:v.co=c+Vector((d.x*.148,d.y*.102,0))
assert max(abs(v.co.x) for v in o.data.vertices)<.22
# The hem must cover the shell edge consistently, while preserving fold volume above it.
j=bpy.data.objects['NYRA · cropped bomber shell'];hem=bpy.data.objects['NYRA · bomber rib hem']
lo=min(v.co.z for v in hem.data.vertices);hi=max(v.co.z for v in hem.data.vertices)
for v in j.data.vertices:
 if abs(v.co.x)<.23 and v.co.z<hi+.012:
  v.co.z=max(v.co.z,lo+.008)
for v in hem.data.vertices:
 t=(v.co.z-lo)/(hi-lo);v.co.z=lo+t*(hi-lo+.009)
bpy.context.view_layer.update();jacket=surface([j.name])
for v in hem.data.vertices:
 c=Vector((0,-.015,v.co.z));d=v.co-c;d.z=0;d.normalize();h=jacket.ray_cast(c,d,.23)
 if h[0]:v.co=h[0]+d*.003
for o in bpy.data.objects:
 if o.type=='MESH' and 'back reflective velocity dash' in o.name:
  for v in o.data.vertices:
   h=jacket.ray_cast(Vector((v.co.x,1,v.co.z)),Vector((0,-1,0)))
   if h[0]:v.co.y=h[0].y+.003
 if o.type=='MESH' and 'zipper pull' in o.name:
  # Keep the hardware at the lower front zipper, clear of the back panel.
  mid=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  for v in o.data.vertices:
   v.co.x+=.041-mid.x;v.co.z+=hi+.03-mid.z
   h=jacket.ray_cast(Vector((v.co.x,-1,v.co.z)),Vector((0,1,0)))
   if h[0]:v.co.y=h[0].y-.003
bpy.context.scene['phase2_finish_version']=5
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/blender/nyra/nyra-visual.blend'),compress=True)
print('VERDICT: PASS — waistband radius',max(abs(v.co.x) for v in bpy.data.objects['NYRA · track waistband'].data.vertices))
