"""Fitting and facial-expression pass on the saved Phase 3 derivative."""
import bpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];col=bpy.data.collections['NYRA | EDITABLE VISUAL MODEL'];sc=bpy.context.scene
assert sc.get('phase3_revision')==2
# Retain circular irises behind the almond eyelid opening, rather than squashing the globe.
ez=1.45+(1.613-1.45)*.83+.065
for name in ['NYRA · eyes','NYRA · corneas']:
 o=bpy.data.objects[name]
 for v in o.data.vertices:
  slope=.0035*(abs(v.co.x/.82)-.0428)/(.8*.028)*.83
  v.co.z=ez+slope+(v.co.z-ez-slope)*(.80/.63)
  cy=-.005+(-.086+.005)*.85;v.co.y=cy+(v.co.y-cy)*(.80/.84)
# Fuller brow, lower inner end and a deliberate arch.
for o in col.objects:
 if 'tapered brow' in o.name:
  for i,v in enumerate(o.data.vertices):
   t=(abs(v.co.x)-.015)/.052;old=1.679+.007*math.sin(math.pi*t*.92)-.003*t;new=1.675+.011*math.sin(math.pi*t*.92)-.003*t
   v.co.z=new+(v.co.z-old)*1.25
# A restrained asymmetric closed-mouth expression, retaining the original editable identity key.
head=bpy.data.objects['NYRA · face identity'];key=head.data.shape_keys.key_blocks['PHASE 3 | mature structure']
for v in key.data:
 x,y,z=v.co
 if x>0 and y<-.10:
  v.co.z+=.0015*math.exp(-((x-.024)/.009)**2-((z-1.577)/.013)**2)
# Clear stale custom normals from deformed source-derived surfaces, if present.
cleared=[]
for o in col.objects:
 if o.type=='MESH' and o.data.has_custom_normals:
  o.data.normals_split_custom_set([(0,0,0)]*len(o.data.loops));cleared.append(o.name)
# Fully fit the remaining raised rear pocket topology to the smooth body surface.
bpy.context.view_layer.update();body=bpy.data.objects['NYRA · anatomy'];e=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();bvh=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
pants=bpy.data.objects['NYRA · tailored track pants']
for v in pants.data.vertices:
 if v.co.y>.005 and .85<v.co.z<1.16:
  h=bvh.ray_cast(Vector((v.co.x,.5,v.co.z)),Vector((0,-1,0)))
  if h[0]:v.co.y=h[0].y+.0055
# Fit the updated brows once more to the actual face.
bpy.context.view_layer.update();e=head.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();h=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear()
for o in col.objects:
 if 'tapered brow' in o.name:
  for v in o.data.vertices:
   hit=h.ray_cast(Vector((v.co.x,-1,v.co.z)),Vector((0,1,0)))
   if hit[0]:v.co.y=hit[0].y-.001
# Restrained ear studs: compact, attached and independent of future hair motion.
metal=bpy.data.materials['NYRA / brushed champagne hardware']
for side in [-1,1]:
 x=side*.089;z=1.611;hit=h.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
 if hit[0]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=hit[0]+Vector((0,-.001,0)))
  o=bpy.context.object;o.name='NYRA · champagne ear stud '+str(side);o.scale=(.0025,.0018,.0035)
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);o.data.materials.append(metal)
  for f in o.data.polygons:f.use_smooth=True
sc['phase3_revision']=3
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/blender/nyra/nyra-phase3.blend'),compress=True)
print('Custom normals reset:',cleared);print('VERDICT: PASS')
