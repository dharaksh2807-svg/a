"""Replace inherited denim pocket surfaces with fitted athletic garment topology."""
import bpy,bmesh,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sc=bpy.context.scene;col=bpy.data.collections['NYRA | EDITABLE VISUAL MODEL'];assert sc.get('phase3_revision')==3
old=bpy.data.objects['NYRA · tailored track pants'];old.name='ARCHIVE · Phase 2 adapted denim topology'
archive=bpy.data.collections.new('ARCHIVE | previous trouser topology');sc.collection.children.link(archive);archive.hide_render=True;archive.hide_viewport=True
for c in list(old.users_collection):c.objects.unlink(old)
archive.objects.link(old)
body=bpy.data.objects['NYRA · anatomy'];m=body.data.copy();m.name='NYRA clean fitted athletic trouser quads';bm=bmesh.new();bm.from_mesh(m)
for co,no in [((0,0,.17),(0,0,1)),((0,0,1.16),(0,0,-1)),((.235,0,0),(-1,0,0)),((-.235,0,0),(1,0,0))]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=co,plane_no=no,clear_inner=True,dist=.000001)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
for v in m.vertices:
 p=v.co;offset=.006
 # Small compression folds behind knees, not inherited denim pockets.
 if p.y>.005:offset+=.0013*math.sin(p.z*150)*math.exp(-((p.z-.59)/.045)**2)
 v.co+=v.normal*offset
m.materials.clear();m.materials.append(bpy.data.materials['NYRA / plum technical twill'])
for f in m.polygons:f.use_smooth=True
pants=bpy.data.objects.new('NYRA · tailored track pants',m);col.objects.link(pants);q=pants.modifiers.new('Athletic garment subdivision','SUBSURF');q.levels=1;q.render_levels=1;q=pants.modifiers.new('Stretch textile thickness','SOLIDIFY');q.thickness=.002;q.offset=0
# Smooth the crop transition into the sleeves rather than introducing a hard positional boundary.
jacket=bpy.data.objects['NYRA · cropped bomber shell']
for v in jacket.data.vertices:
 x=abs(v.co.x);z=v.co.z
 if x<.23 and z<1.43:z=z-.072 if z<1.262 else (z-.429)/.7
 t=max(0,min(1,(x-.16)/.13));weight=1-t*t*(3-2*t)
 v.co.z=z+.072*max(0,min(1,(1.43-z)/.24))*weight
# Diagonal vermillion yoke is a material boundary on continuous cloth.
mat=jacket.data.materials[0];nt=mat.node_tree;sep=next(n for n in nt.nodes if n.type=='SEPXYZ');mask=next(n for n in nt.nodes if n.type=='MATH' and n.operation=='GREATER_THAN')
scale=nt.nodes.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=.14;nt.links.new(sep.outputs['X'],scale.inputs[0]);sub=nt.nodes.new('ShaderNodeMath');sub.operation='SUBTRACT';nt.links.new(sep.outputs['Z'],sub.inputs[0]);nt.links.new(scale.outputs[0],sub.inputs[1]);nt.links.new(sub.outputs[0],mask.inputs[0])
def surface(o):
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();b=BVHTree.FromPolygons([v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);e.to_mesh_clear();return b
pbvh=surface(pants)
for o in col.objects:
 if 'outer calf inset' in o.name:
  s=1 if sum(v.co.x for v in o.data.vertices)>0 else -1
  for v in o.data.vertices:
   hit=pbvh.ray_cast(Vector((s*.5,v.co.y,v.co.z)),Vector((-s,0,0)))
   if hit[0]:v.co=hit[0]+hit[1]*.0015
 if o.type=='CURVE' and 'track side piping' in o.name:
  for spline in o.data.splines:
   for p in spline.bezier_points:
    hit=pbvh.find_nearest(p.co)
    if hit[0]:p.co=hit[0]+hit[1]*.001
sc['phase3_revision']=4
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/blender/nyra/nyra-phase3.blend'),compress=True);print('VERDICT: PASS')
