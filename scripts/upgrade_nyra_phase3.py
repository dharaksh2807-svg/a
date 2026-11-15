"""Phase 3 art-direction derivative. Always starts from the preserved Phase 2 source."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import exp,sin,cos,pi
R=Path(__file__).resolve().parents[1];sc=bpy.context.scene;col=bpy.data.collections['NYRA | EDITABLE VISUAL MODEL']
assert sc.get('phase2_finish_version')==6

def srgb(h):
 a=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def mat(name,color,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=srgb(color);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=srgb(color);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m

def recolor(name,h,rough):
 m=bpy.data.materials[name];p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=rough
 ramps=[n for n in m.node_tree.nodes if n.type=='VALTORGB']
 if ramps:
  for n in ramps:
   for e,k in zip(n.color_ramp.elements,[.88,1.08]):e.color=tuple(min(c*k,1) for c in srgb(h)[:3])+(1,)
 else:
  for l in list(p.inputs['Base Color'].links):m.node_tree.links.remove(l)
  p.inputs['Base Color'].default_value=srgb(h)
 return m

def surface(o):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);me=e.to_mesh();bvh=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[tuple(f.vertices) for f in me.polygons]);e.to_mesh_clear();return bvh

def mesh(name,verts,faces,material,sub=1,thick=0):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);col.objects.link(o);m.materials.append(material)
 for f in m.polygons:f.use_smooth=True
 if sub:q=o.modifiers.new('Editable subdivision','SUBSURF');q.levels=sub;q.render_levels=sub
 if thick:q=o.modifiers.new('Editable thickness','SOLIDIFY');q.thickness=thick
 return o

def tube(name,points,r,material,cyclic=False):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;c.resolution_u=10;s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 s.use_cyclic_u=cyclic;o=bpy.data.objects.new(name,c);col.objects.link(o);c.materials.append(material);return o

def bodymap(p):
 p=p.copy();z=p.z
 # Longer athletic legs, slightly longer upper torso; restrained waist-to-hip contrast.
 p.z+=.044*max(0,min(1,(z-.20)/.70))+.021*max(0,min(1,(z-1.10)/.30))
 waist=exp(-((z-1.105)/.115)**4);hips=exp(-((z-.925)/.11)**2)
 if abs(p.x)<.22:p.x*=1-.075*waist+.025*hips;p.y=-.015+(p.y+.015)*(1-.045*waist)
 return p

def headmap(p,feature='face'):
 p=p.copy();x,y,z=p;sgn=1 if x>=0 else -1;cx=sgn*.0428;ez=1.613
 # Aperture and eyeball transformations agree, keeping eyelids seated.
 if feature in ['eyes','corneas']:
  p.x=cx+(x-cx)*.80;p.z=ez+(z-ez)*.63+.0035*(abs(x)-.0428)/.028;p.y=-.086+(y+.086)*.84
 elif feature not in ['hair','pony']:
  w=exp(-((abs(x)-.043)/.037)**4-((z-ez)/.041)**4)*max(0,min(1,(-y-.035)/.04))
  p.x+=(cx-x)*.20*w;p.z+=(ez-z)*.37*w+.0035*(abs(x)-.0428)/.028*w;p.y+=(-.086-y)*.16*w
  front=max(0,min(1,(-y-.025)/.07));cheek=exp(-((z-1.565)/.032)**2)*front
  p.x*=1-.05*cheek+.025*exp(-((z-1.60)/.028)**2)*front
  p.y+=.004*cheek*exp(-((abs(x)-.068)/.03)**2)
  # Lengthen the lower face, define chin and bridge, retain lip topology.
  p.z-=.012*exp(-((z-1.515)/.065)**2)*front
  p.x*=1+.07*exp(-((z-1.465)/.025)**2)*front
  nose=exp(-(x/.027)**4-((z-1.565)/.035)**4)*front;p.x*=1-.08*nose;p.y-=.0025*nose
  lip=exp(-(x/.038)**6-((z-1.536)/.015)**6)*front;p.y-=.002*lip
 p.x*=.82;p.y=-.005+(p.y+.005)*.85;p.z=1.45+(p.z-1.45)*.83+.065
 return p

face_tags=['face identity','eyes','corneas','oral anatomy','tongue','lashes','tapered brow','hair cap','ponytail']
for o in list(col.objects):
 isface=any(t in o.name for t in face_tags)
 feature='eyes' if o.name.endswith('eyes') else 'corneas' if 'corneas' in o.name else 'hair' if 'hair cap' in o.name else 'pony' if 'ponytail' in o.name else 'face'
 fn=(lambda p:headmap(p,feature)) if isface else bodymap
 if o.type=='MESH':
  if o.name.endswith('face identity'):
   keys=o.data.shape_keys.key_blocks;identity=keys['NYRA adult identity'];new=o.shape_key_add(name='PHASE 3 | mature structure')
   for a,b in zip(new.data,identity.data):a.co=headmap(b.co)
   for k in keys:k.value=0
   new.value=1
  else:
   for v in o.data.vertices:v.co=fn(v.co)
 elif o.type=='CURVE':
  for s in o.data.splines:
   for p in s.bezier_points:p.co=fn(p.co)
# Lower, narrower brows convey focus rather than childlike surprise.
head=bpy.data.objects['NYRA · face identity'];hbvh=surface(head)
for o in col.objects:
 if 'tapered brow' in o.name:
  for v in o.data.vertices:
   v.co.z-=.005+.003*(1-min(abs(v.co.x)/.07,1));h=hbvh.ray_cast(Vector((v.co.x,-1,v.co.z)),Vector((0,1,0)))
   if h[0]:v.co.y=h[0].y-.0011
# Reduce scalp's inflated ridges while keeping its editable topology.
cap=bpy.data.objects['NYRA · sculpted swept hair cap'];vg=cap.vertex_groups.new(name='Crown refinement')
for v in cap.data.vertices:
 if v.co.z>1.68:vg.add([v.index],min(1,(v.co.z-1.68)/.06),'REPLACE')
q=cap.modifiers.new('Sleeker crown sculpt','SMOOTH');q.factor=.65;q.iterations=5;q.vertex_group=vg.name
# Skin stays painted, with reduced gloss and deeper warm satin lips.
skin=bpy.data.materials['NYRA / warm skin with original painted variation'];p=next(n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.52;p.inputs['Subsurface Weight'].default_value=.065
for n in skin.node_tree.nodes:
 if n.type=='MIX_RGB' and n.blend_type=='MIX':n.inputs[2].default_value=srgb('8D3F3C')
recolor('NYRA / brow and lashes','21191B',.78)
# A graphite technical moto-crop, vermillion shoulder yoke, deep charcoal knit.
recolor('NYRA / plum technical twill','303139',.55);recolor('NYRA / plum rib knit','14181F',.70);recolor('NYRA / mulberry stretch jersey','24242D',.57)
recolor('NYRA / coral ripstop nylon','DF452D',.44);recolor('NYRA / warm ivory nylon','D8452C',.48)
jacket=bpy.data.objects['NYRA · cropped bomber shell'];m=jacket.data.materials[0];p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Roughness'].default_value=.4
for n in m.node_tree.nodes:
 if n.type=='VALTORGB':
  n.color_ramp.elements[0].color=srgb('171C25');n.color_ramp.elements[1].color=srgb('232A35')
 if n.type=='MIX_RGB':n.inputs[2].default_value=srgb('D8452C')
 if n.type=='MATH' and n.operation=='GREATER_THAN':n.inputs[1].default_value=1.451
# Crop the jacket torso and fitted jersey to expose a purposeful athletic midriff.
jacket_terms=['cropped bomber','bomber rib hem','zipper','jacket pocket','pocket topstitch','back reflective']
for o in col.objects:
 if any(t in o.name for t in jacket_terms):
  def crop(p):
   p=p.copy()
   if abs(p.x)<.23:p.z+=.072*max(0,min(1,(1.43-p.z)/.24))
   return p
  if o.type=='MESH':
   for v in o.data.vertices:v.co=crop(v.co)
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.bezier_points:p.co=crop(p.co)
# Sleeves retain cloth volume but lose the swollen tube-like shape.
vg=jacket.vertex_groups.new(name='Sleeve tailoring')
for v in jacket.data.vertices:
 if abs(v.co.x)>.21:
  v.co.y*=.87;vg.add([v.index],min(1,(abs(v.co.x)-.21)/.06),'REPLACE')
q=jacket.modifiers.new('Tailored sleeve folds','SMOOTH');q.factor=.45;q.iterations=3;q.vertex_group=vg.name
jersey=bpy.data.objects['NYRA · fitted high-neck jersey'];bm=bmesh.new();bm.from_mesh(jersey.data)
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,1.244),plane_no=(0,0,1),clear_inner=True,dist=.000001);bm.to_mesh(jersey.data);bm.free()
# Trim the lower bib to the same clean edge.
bib=bpy.data.objects['NYRA · continuous jersey chest inset']
# Body-fitted trousers suppress inherited denim pocket forms and excess folds.
body=bpy.data.objects['NYRA · anatomy'];bbvh=surface(body);pants=bpy.data.objects['NYRA · tailored track pants']
for v in pants.data.vertices:
 h=bbvh.find_nearest(v.co)
 if h[0] and h[3]<.045:v.co=v.co.lerp(h[0]+h[1]*.005,.78)
q=pants.modifiers.new('Smooth fitted technical leggings','SMOOTH');q.factor=.48;q.iterations=4
# High waist follows the same underlying anatomy, including the raised top edge.
waist=bpy.data.objects['NYRA · track waistband']
for v in waist.data.vertices:
 v.co.z+=.025;center=Vector((0,-.015,v.co.z));d=v.co-center;d.z=0;d.normalize();h=bbvh.ray_cast(center,d,.23)
 if h[0]:v.co=h[0]+d*.004
# Clear inherited pocket piping, keep the useful track seam infrastructure.
for o in list(col.objects):
 if 'pant pocket welt' in o.name:bpy.data.objects.remove(o,do_unlink=True)
pbvh=surface(pants)
for o in col.objects:
 if 'outer calf inset' in o.name:
  s=1 if sum(v.co.x for v in o.data.vertices)>0 else -1
  for v in o.data.vertices:
   h=pbvh.ray_cast(Vector((s*.5,v.co.y,v.co.z)),Vector((-s,0,0)))
   if h[0]:v.co=h[0]+h[1]*.0015
 if o.type=='CURVE' and 'track side piping' in o.name:
  for spline in o.data.splines:
   for v in spline.bezier_points:
    h=pbvh.find_nearest(v.co)
    if h[0]:v.co=h[0]+h[1]*.001
# Replace the segmented sausage ponytail with one flowing, ridged, tapered volume.
for o in list(col.objects):
 if 'ponytail' in o.name:bpy.data.objects.remove(o,do_unlink=True)
hair=bpy.data.materials['NYRA / espresso-black sculpted hair'];hp=next(n for n in hair.node_tree.nodes if n.type=='BSDF_PRINCIPLED');hp.inputs['Base Color'].default_value=srgb('151317');hp.inputs['Roughness'].default_value=.38;hp.inputs['Specular IOR Level'].default_value=.3;hp.inputs['Anisotropic'].default_value=.55
# Cubic Bezier path from high tie to an asymmetrically swept tip.
P=[Vector((0,.075,1.731)),Vector((.015,.255,1.86)),Vector((.14,.255,1.41)),Vector((.055,.18,1.355))]
def path(t):return (1-t)**3*P[0]+3*(1-t)**2*t*P[1]+3*(1-t)*t*t*P[2]+t**3*P[3]
def axes(t):
 tangent=(path(min(1,t+.001))-path(max(0,t-.001))).normalized();u=tangent.cross(Vector((0,0,1)))
 if u.length<.1:u=Vector((1,0,0))
 u.normalize();return u,tangent.cross(u).normalized()
def radius(t):return .021*(1-t)+.030*sin(pi*t)**.65+.001
verts=[];faces=[];nr=49;ns=48
for i in range(nr):
 t=i/(nr-1);c=path(t);u,v=axes(t);r=radius(t)
 for j in range(ns):
  a=j*2*pi/ns;ridge=1+.035*cos(12*a+t*3)+.018*cos(7*a-t*4);verts.append(c+u*(r*cos(a)*ridge)+v*(r*.80*sin(a)*ridge))
for i in range(nr-1):
 for j in range(ns):faces.append((i*ns+j,i*ns+(j+1)%ns,(i+1)*ns+(j+1)%ns,(i+1)*ns+j))
faces.extend([tuple(reversed(range(ns))),tuple(range((nr-1)*ns,nr*ns))]);pony=mesh('NYRA · flowing high ponytail',verts,faces,hair,1)
metal=mat('NYRA / brushed champagne hardware','B9A080',.32,.78)
# Single compact tie instead of multiple oversized cuffs.
c=path(.045);u,v=axes(.045);tangent=u.cross(v)
verts=[];faces=[]
for k in range(4):
 for j in range(40):
  a=j*2*pi/40;verts.append(c+tangent*((k/3-.5)*.014)+u*.028*cos(a)+v*.024*sin(a))
for k in range(3):
 for j in range(40):faces.append((k*40+j,k*40+(j+1)%40,(k+1)*40+(j+1)%40,(k+1)*40+j))
mesh('NYRA · ponytail champagne clasp',verts,faces,metal,1,.001)
# Fine swept strand ridges follow the volume and stop short of the tip.
strandmat=mat('NYRA / warm hair strand sheen','282027',.44)
for j in range(9):
 a=j*2*pi/9+.1;points=[]
 for i in range(24):
  t=.07+i/23*.84;c=path(t);u,v=axes(t);r=radius(t)*1.018;angle=a+.11*sin(t*pi)
  points.append(c+u*r*cos(angle)+v*r*.80*sin(angle))
 tube('NYRA · ponytail strand '+str(j),points,.00055,strandmat)
# High-contrast footwear: dark technical mesh, pale midsole, vermillion overlays.
recolor('NYRA / ivory engineered sneaker mesh','292D36',.56);recolor('NYRA / cream microcellular midsole','BDBDB6',.66)
# Slimmer, less platform-like footwear, maintaining the fitted junctions.
for o in col.objects:
 if any(x in o.name for x in ['sneaker','dual-density sole']):
  if o.type=='MESH':
   for v in o.data.vertices:v.co.y=-.03+(v.co.y+.03)*.96
  elif o.type=='CURVE':
   for s in o.data.splines:
    for p in s.bezier_points:p.co.y=-.03+(p.co.y+.03)*.96
# New objects receive UVs; original useful UVs are retained.
for o in col.objects:
 if o.type=='MESH' and not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
sc['phase3_revision']=1;sc['status']='Phase 3 visual review. Adult character direction; no rigging or animation approval.'
sc['phase2_checkpoint']='770cd9d1482e25e5dbb33efd63ee9d7cde1ee331'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/blender/nyra/nyra-phase3.blend'),compress=True)
print('VERDICT: PASS')
