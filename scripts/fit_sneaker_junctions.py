"""Fit existing soles to the upper envelope and reseat side overlays."""
import bpy,math
from mathutils import Vector
from mathutils.geometry import convex_hull_2d
from mathutils.bvhtree import BVHTree
from pathlib import Path
root=Path(__file__).resolve().parents[1];dg=bpy.context.evaluated_depsgraph_get()
upper=bpy.data.objects['NYRA · fitted sneaker uppers and laces'];e=upper.evaluated_get(dg);m=e.to_mesh()
pts=[v.co.copy() for v in m.vertices];bvh=BVHTree.FromPolygons(pts,[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
for s in [-1,1]:
 points=[Vector((p.x,p.y)) for p in pts if p.x*s>0 and p.z<.095]
 hull=[points[i] for i in convex_hull_2d(points)];cx=s*.08132;cy=-.075
 def radius(dx,dy):
  hits=[]
  for i,a in enumerate(hull):
   b=hull[(i+1)%len(hull)];ex=b.x-a.x;ey=b.y-a.y;den=dx*ey-dy*ex
   if abs(den)<1e-9:continue
   ax=a.x-cx;ay=a.y-cy;t=(ax*ey-ay*ex)/den;u=(ax*dy-ay*dx)/den
   if t>0 and 0<=u<=1:hits.append(t)
  return max(hits) if hits else .05
 o=bpy.data.objects['NYRA · sculpted dual-density sole '+str(s)]
 for i,v in enumerate(o.data.vertices):
  ring=i//48;dx=v.co.x-cx;dy=v.co.y-cy;length=math.hypot(dx,dy);dx/=length;dy/=length
  r=radius(dx,dy)+.0015;scale=[.96,1,1.018,1.012,.995][ring]
  heel=max(0,min(1,(cy+dy*r+.14)/.18))
  v.co=(cx+dx*r*scale,cy+dy*r*scale,[.0045,.008,.017,.042+.008*heel,.048+.008*heel][ring])
 for f in o.data.polygons:
  f.material_index=1 if sum(o.data.vertices[i].co.z for i in f.vertices)/len(f.vertices)<.0171 else 0
 # Keep the welt as a single clean line immediately below the upper.
 welt=bpy.data.objects['NYRA · sneaker welt '+str(s)]
 for spline in welt.data.splines:
  for p in spline.bezier_points:
   dx=p.co.x-cx;dy=p.co.y-cy;length=math.hypot(dx,dy);dx/=length;dy/=length;r=radius(dx,dy)+.0017
   heel=max(0,min(1,(cy+dy*r+.14)/.18));p.co=(cx+dx*r,cy+dy*r,.046+.008*heel)
 for j in range(2):
  o=bpy.data.objects['NYRA · sneaker TPU slash '+str(s)+' '+str(j)]
  yc=-.075+j*.025
  for v,(y,z) in zip(o.data.vertices,[(yc-.009,.068),(yc-.003,.097),(yc+.005,.097),(yc-.001,.068)]):
   hit=bvh.ray_cast(Vector((s*.5,y,z)),Vector((-s,0,0)))
   if hit[0]:v.co=hit[0]+Vector((s*.0015,0,0))
bpy.context.scene['phase2_finish_version']=6
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/blender/nyra/nyra-visual.blend'),compress=True)
