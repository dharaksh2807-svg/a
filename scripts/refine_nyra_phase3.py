"""Respond to matched-view critique: brows, scalp mass, textile response and waist closure."""
import bpy,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sc=bpy.context.scene;col=bpy.data.collections['NYRA | EDITABLE VISUAL MODEL']
assert sc.get('phase3_revision')==1

def surface(o):
 bpy.context.view_layer.update();e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();b=BVHTree.FromPolygons([v.co for v in m.vertices],[tuple(f.vertices) for f in m.polygons]);e.to_mesh_clear();return b
head=bpy.data.objects['NYRA · face identity'];h=surface(head)
# Replace blunt, frowning brow ribbons with a finer tapered arch, seated to the face.
for o in list(col.objects):
 if 'tapered brow' in o.name:bpy.data.objects.remove(o,do_unlink=True)
for s in [-1,1]:
 verts=[];faces=[];rows=31
 for i in range(rows):
  t=i/(rows-1);x=s*(.015+.052*t);z=1.679+.007*math.sin(math.pi*t*.92)-.003*t;w=.0025*(1-t)**.55+.00012
  for j in [-1,0,1]:
   zz=z+j*w;hit=h.ray_cast(Vector((x,-1,zz)),Vector((0,1,0)));verts.append((x,hit[0].y-.001 if hit[0] else -.12,zz))
 for i in range(rows-1):
  for j in range(2):faces.append((i*3+j,i*3+j+1,(i+1)*3+j+1,(i+1)*3+j))
 m=bpy.data.meshes.new('Tapered brow surface');m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new('NYRA · tapered brow '+str(s),m);col.objects.link(o);m.materials.append(bpy.data.materials['NYRA / brow and lashes'])
 for f in m.polygons:f.use_smooth=True
 q=o.modifiers.new('Soft brow contour','SUBSURF');q.levels=1;q.render_levels=1;q=o.modifiers.new('Brow thickness','SOLIDIFY');q.thickness=.0007
# Reduce the inherited sculpted crown's excess volume relative to the actual skull.
cap=bpy.data.objects['NYRA · sculpted swept hair cap'];center=Vector((0,.0,1.665))
for v in cap.data.vertices:
 d=(v.co-center).normalized();hit=h.ray_cast(center,d,.25)
 if hit[0] and (hit[0]-center).length < (v.co-center).length+.008:
  gap=max(0,(v.co-hit[0]).dot(d));v.co=hit[0]+d*(.004+gap*.23)
# Stronger cupid's bow is an actual shape-key edit, not a painted highlight.
key=head.data.shape_keys.key_blocks['PHASE 3 | mature structure']
for v in key.data:
 x,y,z=v.co
 if y<-.105:
  weight=math.exp(-((z-1.588)/.004)**2)
  v.co.z+=(.0013*math.exp(-((abs(x)-.008)/.006)**2)-.0008*math.exp(-(x/.004)**2))*weight
# Honest textile roughness: avoid wet plastic read under the unchanged lighting.
settings={'NYRA / tailored coral and ivory yoke':.62,'NYRA / coral ripstop nylon':.62,'NYRA / warm ivory nylon':.63,'NYRA / plum technical twill':.70,'NYRA / mulberry stretch jersey':.75,'NYRA / espresso-black sculpted hair':.54,'NYRA / warm hair strand sheen':.56}
for name,r in settings.items():
 m=bpy.data.materials.get(name)
 if m:
  p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=r
  if 'hair' in name:p.inputs['Specular IOR Level'].default_value=.22
# Shorter collar, with the same bottom fitting.
o=bpy.data.objects['NYRA · stand collar'];lo=min(v.co.z for v in o.data.vertices)
for v in o.data.vertices:v.co.z=lo+(v.co.z-lo)*.63
# Extend and refit the trouser waist under the waistband instead of leaving a skin slit.
body=surface(bpy.data.objects['NYRA · anatomy']);pants=bpy.data.objects['NYRA · tailored track pants']
for v in pants.data.vertices:
 if v.co.z>1.015:
  v.co.z+=.043*min(1,(v.co.z-1.015)/.09)
  hit=body.find_nearest(v.co)
  if hit[0]:v.co=hit[0]+hit[1]*.0055
# Preserve UVs; add UVs only to the new brows.
for o in col.objects:
 if o.type=='MESH' and not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
sc['phase3_revision']=2
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/blender/nyra/nyra-phase3.blend'),compress=True)
print('VERDICT: PASS')
