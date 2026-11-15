"""NYRA Phase 2 modeling source. Run against the original Rain blend with autoexec disabled.
Creates an editable modeling asset, not a final game rig. All dimensions are meters.
"""
import bpy,bmesh,math,json,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from math import sin,cos,pi,exp,sqrt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'source/blender/nyra/nyra-visual.blend'
scene=bpy.context.scene
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
# Capture base evaluation with no subdivision. Original file is never overwritten.
cache={}
for o in bpy.data.objects:
 if o.name.startswith('GEO-') and o.type=='MESH':
  for m in o.modifiers:
   if m.type in {'SUBSURF','MASK','VERTEX_WEIGHT_MIX'}:m.show_viewport=False
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for o in list(scene.objects):
 if o.type=='MESH' and o.name.startswith('GEO-'):
  mesh=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg)
  mesh.transform(o.matrix_world)
  cache[o.name]=mesh
# Keep image sources available but detach all external relative paths before saving elsewhere.
for image in bpy.data.images:
 if image.filepath:image.filepath=bpy.path.abspath(image.filepath)
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
for c in list(bpy.data.collections):
 if c.users==0:bpy.data.collections.remove(c)
char=bpy.data.collections.new('NYRA | EDITABLE VISUAL MODEL');scene.collection.children.link(char)
models=[]
def mesh_obj(name,verts,faces,mat=None,sub=0):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);char.objects.link(o);models.append(o)
 if mat:mesh.materials.append(mat)
 for p in mesh.polygons:p.use_smooth=True
 if sub:
  m=o.modifiers.new('Editable surface subdivision','SUBSURF');m.levels=1;m.render_levels=sub
 return o
def from_cache(key,name,mat=None,sub=1):
 o=bpy.data.objects.new(name,cache[key].copy());char.objects.link(o);models.append(o)
 if mat:o.data.materials.clear();o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 if sub:
  m=o.modifiers.new('Editable surface subdivision','SUBSURF');m.levels=1;m.render_levels=sub
 return o
def srgb(hex):
 a=[int(hex[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def material(name,color,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=srgb(color);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=srgb(color);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m,p
# Actual reusable weave height texture, generated deterministically and saved externally.
N=512;y,x=np.mgrid[0:N,0:N]/N
rng=np.random.default_rng(218)
weave=.5+.19*np.sin(x*2*pi*64)*np.sin(y*2*pi*64)+.07*np.sin((x+y)*2*pi*128)+rng.normal(0,.022,(N,N))
img=bpy.data.images.new('NYRA technical weave height',width=N,height=N,alpha=False)
a=np.ones((N,N,4),dtype=np.float32);a[:,:,:3]=np.clip(weave[:,:,None],0,1);img.pixels.foreach_set(a.ravel());img.filepath_raw=str(ROOT/'textures/nyra/technical-weave.png');img.file_format='PNG';img.save();img.colorspace_settings.name='Non-Color'
def fabric(name,color,rough=.55,scale=8,bump=.00025):
 m,p=material(name,color,rough);nodes=m.node_tree.nodes;links=m.node_tree.links
 tc=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=scale
 links.new(tc.outputs['Object'],mapping.inputs[0]);tex=nodes.new('ShaderNodeTexImage');tex.image=img;tex.extension='REPEAT';links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
 ramp=nodes.new('ShaderNodeValToRGB');base=srgb(color)
 ramp.color_ramp.elements[0].color=tuple(c*.78 for c in base[:3])+(1,);ramp.color_ramp.elements[1].color=tuple(min(c*1.10,1) for c in base[:3])+(1,)
 links.new(tex.outputs['Color'],ramp.inputs[0]);links.new(ramp.outputs[0],p.inputs['Base Color'])
 b=nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=bump;links.new(tex.outputs['Color'],b.inputs['Height']);links.new(b.outputs[0],p.inputs['Normal']);p.inputs['Sheen Weight'].default_value=.16
 return m
coral=fabric('NYRA / coral ripstop nylon','B95E48',.52,8)
ivory=fabric('NYRA / warm ivory nylon','E9DFCB',.49,8)
plum=fabric('NYRA / plum technical twill','382A40',.62,10)
knit=fabric('NYRA / plum rib knit','2B2031',.7,14,.0004)
jersey=fabric('NYRA / mulberry stretch jersey','543449',.67,12)
shoe_mesh=fabric('NYRA / ivory engineered sneaker mesh','D4CCBC',.68,10,.0005)
rubber,_=material('NYRA / cream microcellular midsole','E7DEC7',.72)
outsole,_=material('NYRA / graphite traction rubber','27242C',.83)
trim,_=material('NYRA / reflective copper trim','C59362',.3,.6)
seam,_=material('NYRA / topstitch thread','E8B79B',.65)
hair,hp=material('NYRA / espresso-black sculpted hair','19151E',.61);hp.inputs['Anisotropic'].default_value=.25;hp.inputs['Coat Weight'].default_value=0;hp.inputs['Specular IOR Level'].default_value=.12
# Hair micro-surface avoids solid plastic shading, larger strand planes are modeled.
noise=hair.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=240
b=hair.node_tree.nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.00012;b.inputs['Strength'].default_value=.1;hair.node_tree.links.new(noise.outputs['Fac'],b.inputs['Height']);hair.node_tree.links.new(b.outputs[0],hp.inputs['Normal'])
skin,sp=material('NYRA / warm skin with original painted variation','AF795A',.46)
sp.inputs['Subsurface Weight'].default_value=.075;sp.inputs['Subsurface Radius'].default_value=(1,.42,.22);sp.inputs['Subsurface Scale'].default_value=.035;sp.inputs['Specular IOR Level'].default_value=.3
nodes=skin.node_tree.nodes;links=skin.node_tree.links
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.get('TEX-rain_body_diffuse.1001.png')
mult=nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(1.05,.83,.73,1);links.new(tex.outputs['Color'],mult.inputs[1]);links.new(mult.outputs[0],sp.inputs['Base Color'])
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=550;b=nodes.new('ShaderNodeBump');b.inputs['Distance'].default_value=.00009;b.inputs['Strength'].default_value=.12;links.new(noise.outputs['Fac'],b.inputs['Height']);links.new(b.outputs[0],sp.inputs['Normal'])
lips,lp=material('NYRA / satin muted rose lip','8B4A45',.38);lp.inputs['Subsurface Weight'].default_value=.05;lp.inputs['Coat Weight'].default_value=.12
brow,_=material('NYRA / brow and lashes','20171E',.65)
# Identity adaptation works in the source coordinate system, then proportions are unified.
def facial(p,eye=False):
 p=Vector(p);ax=abs(p.x);sgn=1 if p.x>=0 else -1
 cx=sgn*.0465;cz=1.473
 if eye:
  p.x=cx+(p.x-cx)*.82;p.z=cz+(p.z-cz)*.78
 else:
  w=exp(-((ax-.047)/.041)**4-((p.z-cz)/.042)**4)*max(0,min(1,(-p.y-.04)/.05))
  p.x+=(cx-p.x)*.18*w;p.z+=(cz-p.z)*.22*w
  # Mature cheek plane, narrower nose wings, softly squared lower jaw and subtle smile.
  cheek=exp(-((ax-.077)/.032)**2-((p.z-1.432)/.029)**2)*max(0,min(1,(-p.y-.05)/.05))
  p.y-=.004*cheek
  nose=exp(-(p.x/.025)**2-((p.z-1.438)/.028)**2)*max(0,min(1,(-p.y-.11)/.04));p.x*=1-.07*nose
  jaw=exp(-((p.z-1.36)/.045)**2);p.x*=1+.045*jaw
  if p.y<-.11:
   p.z-=.011*exp(-(p.x/.055)**2-((p.z-1.35)/.026)**2)
   p.z+=.0025*exp(-((ax-.033)/.013)**2-((p.z-1.394)/.014)**2)
 return Vector((p.x*.86,-.015+(p.y+.015)*.89,1.30+(p.z-1.30)*.87))
def body_proportion(p):
 p=Vector(p)
 if p.z<.95:p.z*=1.06
 else:p.z+=.057
 return p*1.07
def lower_arm(p):
 p=Vector(p);ax=abs(p.x)
 if p.z>1.12 and ax>.12:
  w=max(0,min(1,(ax-.12)/.085));w=w*w*(3-2*w);ang=math.radians(49)*w;sgn=1 if p.x>=0 else -1
  dx=ax-.14;dz=p.z-1.25
  p.x=sgn*(.14+dx*cos(ang)+dz*sin(ang));p.z=1.25-dx*sin(ang)+dz*cos(ang)
 return p
# Curve meshes: tailored seams and attached trims remain separately editable.
def tube(name,points,radius,mat,cyclic=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=radius;cu.bevel_resolution=2
 spl=cu.splines.new('BEZIER');spl.bezier_points.add(len(points)-1)
 for b,p in zip(spl.bezier_points,points):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 spl.use_cyclic_u=cyclic
 o=bpy.data.objects.new(name,cu);char.objects.link(o);cu.materials.append(mat);models.append(o);return o

def loft(name,rings,mat,sides=32,sub=1):
 # rings are (center, axis_u, axis_v); circumferential continuous quad topology.
 verts=[];faces=[]
 for center,u,v in rings:
  for j in range(sides):
   a=2*pi*j/sides;verts.append(Vector(center)+Vector(u)*cos(a)+Vector(v)*sin(a))
 for i in range(len(rings)-1):
  for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 return mesh_obj(name,verts,faces,mat,sub)
def shell(o,thickness=.002):
 s=o.modifiers.new('Garment thickness — editable','SOLIDIFY');s.thickness=thickness;s.offset=0

body=from_cache('GEO-rain-body_nomask','NYRA · anatomy',skin,1)
head=from_cache('GEO-rain-head','NYRA · face identity',skin,1)
head.shape_key_add(name='Foundation');identity=head.shape_key_add(name='NYRA adult identity')
for v,k in zip(head.data.vertices,identity.data):k.co=facial(v.co)
identity.value=1
# Smooth vertex-painted lip tint avoids a polygon-assignment boundary on the face.
attr=head.data.color_attributes.new(name='NYRA Lip',type='FLOAT_COLOR',domain='POINT')
for v,c in zip(head.data.vertices,attr.data):
 p=v.co;w=.65*exp(-(p.x/.034)**6-((p.z-1.392)/.013)**6)*max(0,min(1,(-p.y-.135)/.018));c.color=(w,w,w,1)
attrnode=skin.node_tree.nodes.new('ShaderNodeAttribute');attrnode.attribute_name='NYRA Lip'
lipmix=skin.node_tree.nodes.new('ShaderNodeMixRGB');lipmix.inputs[2].default_value=srgb('97544E');links.new(attrnode.outputs['Fac'],lipmix.inputs[0]);links.new(mult.outputs[0],lipmix.inputs[1]);links.new(lipmix.outputs[0],sp.inputs['Base Color'])
face_objects=[head]
for key,label in [('GEO-rain-eyes','eyes'),('GEO-rain-eye_cornea','corneas'),('GEO-rain-eyelashes','upper lashes'),('GEO-rain-gums_lower','lower oral anatomy'),('GEO-rain-gums_upper','upper oral anatomy'),('GEO-rain-tongue','tongue')]:
 o=from_cache(key,'NYRA · '+label,None,1)
 if label in {'sculpted brows','upper lashes'}:
  o.data.materials.clear();o.data.materials.append(brow)
  for v in o.data.vertices:
   if label=='sculpted brows':v.co.z=1.508+(v.co.z-1.508)*.58+.003*(abs(v.co.x)/.09)
 for v in o.data.vertices:v.co=facial(v.co,eye=label in {'eyes','corneas'})
 face_objects.append(o)
# Replace eyes with a clear painted iris map and warm hazel color adjustment.
eyes=next(o for o in face_objects if o.name=='NYRA · eyes')
eyemat,ep=material('NYRA / warm hazel eyes','EEE8DC',.23);ep.inputs['Coat Weight'].default_value=.3
nt=eyemat.node_tree;et=nt.nodes.new('ShaderNodeTexImage');et.image=bpy.data.images.get('TEX-rain_eyes.png.000') or bpy.data.images.get('TEX-rain_eyes.png.002')
hue=nt.nodes.new('ShaderNodeHueSaturation');hue.inputs['Hue'].default_value=.98;hue.inputs['Saturation'].default_value=.72;nt.links.new(et.outputs['Color'],hue.inputs['Color']);nt.links.new(hue.outputs[0],ep.inputs['Base Color']);eyes.data.materials.clear();eyes.data.materials.append(eyemat)
# A new high-neck jersey shell from anatomy replaces the tank top completely.
top=from_cache('GEO-rain-body_nomask','NYRA · fitted high-neck jersey',jersey,1)
bm=bmesh.new();bm.from_mesh(top.data)
for point,normal in [((0,0,.958),(0,0,1)),((0,0,1.24),(0,0,-1)),((.146,0,0),(-1,0,0)),((-.146,0,0),(1,0,0))]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,clear_inner=True,dist=.000001)
bm.to_mesh(top.data);bm.free()
for v in top.data.vertices:v.co+=v.normal*.003
shell(top,.0015)
o=loft('NYRA · jersey mock neck',[((0,-.014,z),(rx,0,0),(0,ry,0)) for z,rx,ry in [(1.225,.075,.073),(1.24,.065,.06),(1.28,.045,.047),(1.31,.044,.045)]],jersey,48,1);shell(o,.0015)
# Remove hidden body neck to prevent coplanar shading inside the fitted collar.
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,1.255),plane_no=(0,0,-1),clear_inner=True,dist=.000001);bm.to_mesh(body.data);bm.free()
# Jacket uses continuous anatomical shoulder topology, cut/fitted as a cloth shell.
jacket=from_cache('GEO-rain-body_nomask','NYRA · cropped bomber shell',coral,1)
bm=bmesh.new();bm.from_mesh(jacket.data)
for point,normal in [((0,0,1.015),(0,0,1)),((.505,0,0),(-1,0,0)),((-.505,0,0),(1,0,0))]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=point,plane_no=normal,clear_inner=True,dist=.000001)
# Exact panel boundaries precede cloth volume shaping.
bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,1.255),plane_no=(0,0,1),dist=.000001)
# Neck opening and central zipper opening have exact clipping boundaries.
for xplane in [-.033,.033]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(xplane,0,0),plane_no=(1,0,0),dist=.000001)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.calc_center_median().x)<.03299 and f.calc_center_median().y<-.02],context='FACES')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(jacket.data);bm.free()
jacket.data.materials.append(ivory)
for p in jacket.data.polygons:
 if p.center.z>1.255:p.material_index=1
# Volume, irregular compression folds and ribbed hem fitting.
for v in jacket.data.vertices:
 p=v.co;original=p.copy();normal=v.normal.copy();ax=abs(p.x)
 if ax>.17:
  center=Vector((p.x,.006,1.247-(ax-.14)*.045));rad=Vector((0,p.y-center.y,p.z-center.z));rad.normalize()
  fold=.0035*sin((ax-.18)*95+math.atan2(rad.z,rad.y)*2.2)*exp(-((ax-.37)/.14)**2)
  p+=rad*(.020+fold)
 else:
  z=p.z;theta=math.atan2((p.y+.015)/.09,p.x/.13)
  rx=float(np.interp(z,[1.015,1.09,1.19,1.25,1.29,1.31],[.128,.147,.167,.164,.10,.047]))
  ry=float(np.interp(z,[1.015,1.09,1.19,1.25,1.29,1.31],[.093,.105,.124,.108,.06,.043]))
  oldx=p.x;p.x=rx*cos(theta);p.y=-.015+ry*sin(theta)
  if abs(oldx)<.034:p.x=oldx
  fold=.0025*sin(theta*11+z*38)*exp(-((z-1.06)/.047)**2)
  p.y+=fold*sin(theta);p.x+=fold*cos(theta)
  blend=max(0,min(1,(z-1.205)/.052));blend=blend*blend*(3-2*blend)
  p[:]=p.lerp(original+normal*.016,blend)
jacket.data.update()
jbvh=BVHTree.FromPolygons([v.co for v in jacket.data.vertices],[tuple(p.vertices) for p in jacket.data.polygons])
def jacket_surface(p,back=False,offset=.002):
 p=Vector(p);hit=jbvh.ray_cast(Vector((p.x,1 if back else -1,p.z)),Vector((0,-1 if back else 1,0)))
 return hit[0]+hit[1]*offset if hit[0] else p
shell(jacket,.0025)
# Collar, hem and cuff lofts in T-pose coordinates.
for name,zs,rx,ry,mat in [('bomber rib hem',[.997,1.0,1.023,1.027],.128,.093,knit),('stand collar',[1.285,1.29,1.328,1.333],.057,.055,coral)]:
 rings=[((0,-.014,z),(rx,0,0),(0,ry,0)) for z in zs]
 o=loft('NYRA · '+name,rings,mat,48,1);shell(o,.002)
 # Open at center front, retaining an intentional gap.
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().y<-.04 and abs(f.calc_center_median().x)<.032],context='FACES');bm.to_mesh(o.data);bm.free()
for s in [-1,1]:
 rings=[((s*x,.0,1.231),(0,r,0),(0,0,r*.9)) for x,r in [(.488,.038),(.493,.039),(.526,.033),(.529,.032)]]
 cuff=loft('NYRA · rib cuff '+str(s),rings,knit,40,1);shell(cuff,.002)
 # zipper rails follow the front silhouette; pocket mouths sit on the fitted jacket surface.
 tube('NYRA · zipper tape '+str(s),[jacket_surface(p) for p in [(s*.037,-.114,1.025),(s*.037,-.139,1.13),(s*.037,-.125,1.22),(s*.032,-.061,1.31)]],.0022,knit)
 tube('NYRA · copper zipper teeth '+str(s),[jacket_surface(p,offset=.004) for p in [(s*.034,-.116,1.026),(s*.034,-.142,1.13),(s*.034,-.128,1.22),(s*.03,-.063,1.31)]],.00085,trim)
 tube('NYRA · diagonal jacket pocket '+str(s),[jacket_surface(p) for p in [(s*.071,-.107,1.044),(s*.102,-.106,1.096)]],.002,knit)
 tube('NYRA · pocket topstitch '+str(s),[jacket_surface(p) for p in [(s*.075,-.108,1.045),(s*.106,-.107,1.097)]],.0005,seam)
# Refit jeans topology into tapered trackwear; preserve its useful knee/hip folds.
pants=from_cache('GEO-rain-jeans','NYRA · tailored track pants',plum,1)
for v in pants.data.vertices:
 p=v.co;s=1 if p.x>0 else -1;cx=s*(.075+.02*max(0,(p.z-.45)/.4));r=Vector((p.x-cx,p.y+.01,0));r.normalize();amount=.007*exp(-((p.z-.63)/.29)**2);p+=r*amount
pants.data.update()
bvh=BVHTree.FromPolygons([v.co for v in pants.data.vertices],[tuple(p.vertices) for p in pants.data.polygons])
def side_point(s,y,z,offset=.0018):
 hit=bvh.ray_cast(Vector((s*.5,y,z)),Vector((-s,0,0)))
 return hit[0]+hit[1]*offset if hit[0] else Vector((s*.105,y,z))
for s in [-1,1]:
 points=[side_point(s,-.011,z) for z in np.linspace(.18,.9,28)];tube('NYRA · track side piping '+str(s),points,.0014,coral)
 verts=[];faces=[]
 for i,z in enumerate(np.linspace(.18,.49,20)):
  section=[v.co.y for v in pants.data.vertices if abs(v.co.z-z)<.018 and v.co.x*s>0]
  mid=(min(section)+max(section))/2 if section else -.005
  width=(max(section)-min(section))*.19 if section else .009
  for j in range(7):verts.append(side_point(s,mid+(j/6-.5)*width*2,z,.0012))
 for i in range(19):
  for j in range(6):faces.append((i*7+j,i*7+j+1,(i+1)*7+j+1,(i+1)*7+j))
 patch=mesh_obj('NYRA · ivory outer calf inset '+str(s),verts,faces,ivory,0);shell(patch,.0007)
 tube('NYRA · pant pocket welt '+str(s),[(s*.105,-.113,.904),(s*.125,-.116,.85)],.0012,knit)
# Rib knit waistband, fitted to original pant height.
o=loft('NYRA · track waistband',[((0,-.014,z),(r,0,0),(0,.082,0)) for z,r in [(.923,.125),(.927,.128),(.956,.122),(.96,.12)]] ,knit,56,1);shell(o,.002)
# Head cap is adapted; original loose strand and rear ponytail are replaced.
cap=from_cache('GEO-rain-hair_main','NYRA · sculpted swept hair cap',hair,1)
for v in cap.data.vertices:
 p=v.co;p.x+=.009*exp(-((p.z-1.60)/.06)**2);v.co=facial(p)
face_objects.append(cap)
# New continuous segmented ponytail, curved clear of upper-back motif.
centers=[(0,.09,1.585),(0,.13,1.63),(.018,.174,1.60),(.035,.196,1.55),(.047,.205,1.515),(.06,.212,1.48),(.078,.211,1.435),(.086,.196,1.40),(.099,.178,1.36),(.11,.162,1.32),(.105,.155,1.29)]
radii=[.022,.035,.044,.035,.019,.032,.037,.018,.026,.017,.002]
rings=[]
for i,(c,r) in enumerate(zip(centers,radii)):
 d=(Vector(centers[min(i+1,len(centers)-1)])-Vector(centers[max(i-1,0)])).normalized();u=Vector((1,0,0));v=d.cross(u).normalized();rings.append((c,u*r,v*r*.76))
pony=loft('NYRA · continuous segmented ponytail',rings,hair,32,2)
for v in pony.data.vertices:v.co=facial(v.co)
face_objects.append(pony)
for idx in [0,4,7]:
 c,u,v=rings[idx];t=(Vector(centers[min(idx+1,10)])-Vector(centers[max(idx-1,0)])).normalized();r=[]
 for a in [-.006,-.004,.004,.006]:r.append((Vector(c)+t*a,Vector(u)*(1.4 if idx else 1.25),Vector(v)*(1.4 if idx else 1.25)))
 o=loft('NYRA · ponytail copper cuff '+str(idx),r,trim,32,1);shell(o,.001)
 for vert in o.data.vertices:vert.co=facial(vert.co)
 face_objects.append(o)
# Swept forehead clump and carved strand accents.
for i in range(0):
 shift=i*.009
 points=[(-.08+shift,-.045,1.62),(-.065+shift,-.106,1.63),(-.025+shift,-.14,1.59),(.038+shift*.45,-.143,1.55)]
 o=tube('NYRA · swept hair ridge '+str(i),[facial(p) for p in points],.0035 if i<4 else .0025,hair)
 face_objects.append(o)
# Sneakers: refined source upper/laces, entirely new layered sole and heel design.
shoes=from_cache('GEO-rain-shoes','NYRA · fitted sneaker uppers and laces',None,1)
shoes.data.materials.clear()
for m in [shoe_mesh,trim,knit,ivory,coral]:shoes.data.materials.append(m)
bm=bmesh.new();bm.from_mesh(shoes.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z<.026],context='FACES');bm.to_mesh(shoes.data);bm.free()
for v in shoes.data.vertices:
 s=1 if v.co.x>0 else -1;v.co.x=s*.076+(v.co.x-s*.076)*1.06
 if v.co.z>.029:v.co.z+=.009
shoes.data.update()
for p in shoes.data.polygons:
 c=p.center
 if p.material_index==0 and c.y>.005:p.material_index=4
sbvh=BVHTree.FromPolygons([v.co for v in shoes.data.vertices],[tuple(p.vertices) for p in shoes.data.polygons])
def shoe_surface(p,side):
 hit=sbvh.ray_cast(Vector((side*.5,p[1],p[2])),Vector((-side,0,0)))
 return hit[0]+hit[1]*.001 if hit[0] else Vector(p)
for s in [-1,1]:
 verts=[];faces=[];n=48
 for z,sc in [(.004,.91),(.007,1),(.016,1.025),(.035,1),(.04,.94)]:
  for j in range(n):
   a=2*pi*j/n;yy=-.07+.122*cos(a);width=.043*(1-.13*cos(a))
   xx=s*.076+width*sin(a)*sc;zz=z+.007*(.5+.5*cos(a))
   verts.append((xx,yy,zz))
 for i in range(4):
  for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 faces.append(tuple(reversed(range(n))));faces.append(tuple(range(4*n,5*n)))
 sole=mesh_obj('NYRA · sculpted dual-density sole '+str(s),verts,faces,rubber,1);sole.data.materials.append(outsole)
 for p in sole.data.polygons:
  if p.center.z<.015:p.material_index=1
 # heel tab, side double-dash overlays and sole stitch line.
 tube('NYRA · sneaker welt '+str(s),[(s*.076+.043*sin(a),-.07+.12*cos(a),.035+.007*(.5+.5*cos(a))) for a in np.linspace(0,2*pi,48,endpoint=False)],.0011,coral,True)
 for j in range(2):
  x=s*.121;yy=-.075+j*.025
  o=mesh_obj('NYRA · sneaker TPU slash '+str(s)+' '+str(j),[shoe_surface(p,s) for p in [(x,yy-.012,.049),(x+s*.002,yy-.005,.073),(x+s*.002,yy+.006,.073),(x,yy-.001,.049)]],[(0,1,2,3)],coral);shell(o,.001)
# Original double-dash back mark, follows jacket back. Not a borrowed brand.
for dx in [-.016,.010]:
 o=mesh_obj('NYRA · back reflective velocity dash',[jacket_surface(p,True,.003) for p in [(dx,.105,1.176),(dx+.012,.105,1.176),(dx+.032,.097,1.209),(dx+.020,.097,1.209)]],[(0,1,2,3)],ivory);shell(o,.001)
# Shoulder topstitch seams; eyelet-free small copper zipper pull.
for s in [-1,1]:
 tube('NYRA · shoulder yoke seam '+str(s),[jacket_surface(p,offset=.002) for p in [(s*.065,-.078,1.28),(s*.12,-.074,1.29),(s*.18,-.048,1.277),(s*.23,-.031,1.28)]],.0006,seam)
o=mesh_obj('NYRA · zipper pull',[jacket_surface(p,offset=.006) for p in [(.029,-.121,1.035),(.04,-.121,1.035),(.04,-.124,1.055),(.029,-.124,1.055)]],[(0,1,2,3)],trim);shell(o,.001)
# Clean tapered brow ribbons fit to the actual adult identity surface.
hbvh=BVHTree.FromPolygons([v.co for v in identity.data],[tuple(p.vertices) for p in head.data.polygons])
for side in [-1,1]:
 verts=[];faces=[]
 for i in range(25):
  t=i/24;x=side*(.018+.071*t);z=1.508+.011*sin(t*pi)-.005*t;width=.0048*(1-t)**.55+.0003
  for j in range(5):
   pos=facial((x,-.15,z+(j/4-.5)*width*2));hit=hbvh.ray_cast(Vector((pos.x,-.5,pos.z)),Vector((0,1,0)))
   verts.append(hit[0]+hit[1]*.001 if hit[0] else pos)
 for i in range(24):
  for j in range(4):faces.append((i*5+j,i*5+j+1,(i+1)*5+j+1,(i+1)*5+j))
 o=mesh_obj('NYRA · tapered brow '+str(side),verts,faces,brow,1);shell(o,.0006);face_objects.append(o)
# Source-mesh anatomy and fabric remain editable; presentation pose is a geometric A-pose.
# No production armature is generated in Phase 2.
face_set=set(face_objects)
for o in models:
 def finish(p):
  p=Vector(p)
  if o not in face_set:p=lower_arm(p)
  return body_proportion(p)
 if o.type=='MESH':
  if o.data.shape_keys:
   for key in o.data.shape_keys.key_blocks:
    for v in key.data:v.co=finish(v.co)
  else:
   for v in o.data.vertices:v.co=finish(v.co)
  o.data.update()
 elif o.type=='CURVE':
  for spline in o.data.splines:
   for b in spline.bezier_points:b.co=finish(b.co)
  o.data.bevel_depth*=1.07
 o['project']='NYRA — Urban Velocity';o['production_stage']='Phase 2 visual modeling; no final rig';o['provenance']='Original design; anatomy-derived parts adapted from Rain (CC BY 4.0)'
# UV generation only for newly authored meshes lacking UVs; inherited maps remain untouched.
for o in models:
 if o.type=='MESH' and not o.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
# Packed images make this authoring file portable, while weave PNG also remains external.
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.file.pack_all()
scene['credit']='Rain Rig (CC) Blender Foundation | studio.blender.org — CC BY 4.0. Modified anatomy and original NYRA wardrobe/hair/look development.'
scene['status']='Visual model iteration. Not game-ready; no final rigging.'
# Neutral studio setup, saved with model and used by reproducible render script.
scene.world=bpy.data.worlds.new('NYRA neutral studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.view_settings.view_transform='AgX'
scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for name,pos,power,size,col in [('Key',(2,-3,4),400,3,(1,.87,.76)),('Fill',(-2,-1,2.5),180,2,(.75,.85,1)),('Rim',(1,2,3),200,2,(1,.83,.72))]:
 data=bpy.data.lights.new('NYRA '+name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=col;o=bpy.data.objects.new(data.name,data);scene.collection.objects.link(o);o.location=pos;aim(o,(0,0,1))
cam=bpy.data.objects.new('NYRA presentation camera',bpy.data.cameras.new('NYRA presentation camera'));scene.collection.objects.link(cam);cam.location=(2,-5,2);cam.data.type='ORTHO';cam.data.ortho_scale=2.15;aim(cam,(0,0,.9));scene.camera=cam
# Matte studio floor is separate from the character collection.
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='STUDIO floor';floor.location.z=-.001;fm,_=material('STUDIO warm charcoal','38343C',.85);floor.data.materials.append(fm)
# Select character for immediate editing.
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
print('NYRA_MODEL_SAVED',OUT)
