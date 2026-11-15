"""Fit waistband and retained trims against the final evaluated garments."""
import bpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1];dg=bpy.context.evaluated_depsgraph_get()
def surface(names):
 verts=[];faces=[]
 for name in names:
  o=bpy.data.objects[name];m=o.evaluated_get(dg).to_mesh();base=len(verts);verts.extend(o.matrix_world@v.co for v in m.vertices);faces.extend(tuple(i+base for i in p.vertices) for p in m.polygons);o.evaluated_get(dg).to_mesh_clear()
 return BVHTree.FromPolygons(verts,faces)
jacket=surface(['NYRA · cropped bomber shell']);pants=surface(['NYRA · tailored track pants']);waist=surface(['NYRA · anatomy','NYRA · tailored track pants'])
o=bpy.data.objects['NYRA · track waistband']
for v in o.data.vertices:
 c=Vector((0,-.015,v.co.z));d=v.co-c;d.z=0;d.normalize();h=waist.ray_cast(c+d*.5,-d)
 if h[0]:v.co=h[0]+h[1]*.002
for o in bpy.data.objects:
 if o.type=='CURVE' and any(w in o.name for w in ['zipper tape','zipper teeth','jacket pocket','pocket topstitch','pant pocket welt']):
  bvh=pants if 'pant pocket' in o.name else jacket
  for spline in o.data.splines:
   for p in spline.bezier_points:
    h=bvh.find_nearest(p.co)
    if h[0]:p.co=h[0]+h[1]*.0015
 elif o.type=='MESH' and any(w in o.name for w in ['back reflective velocity dash','zipper pull']):
  for v in o.data.vertices:
   h=jacket.find_nearest(v.co)
   if h[0]:v.co=h[0]+h[1]*.0015
bpy.context.scene['phase2_finish_version']=4
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/blender/nyra/nyra-visual.blend'),compress=True)
