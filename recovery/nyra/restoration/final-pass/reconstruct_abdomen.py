"""Excise the fold at exact cuts; triangulate and stitch the exterior boundary.
Run after recover.py. Original navel/belt vertices are outside the cut.
"""
import bpy,bmesh,numpy as np,json
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath='/tmp/nyra-stage1.blend');o=bpy.data.objects['Mesh_0'];m=o.data;mw=o.matrix_world.copy();inv=mw.inverted()
# Replay uses the delivered source-derived textures; no temporary master is needed.
faceim=bpy.data.images.load(str(R/'textures/localized-color.png'),check_existing=True)
mat=m.materials[1].copy();mat.name='NYRA recovery / abdominal donor skin'
mat.node_tree.nodes['Image Texture'].image=bpy.data.images.load(str(R/'textures/abdomen-skin-infill.png'),check_existing=True)
for mt in m.materials:mt.node_tree.nodes['Image Texture'].image=faceim
# Quiet donor variation; this is explicitly texture infill, not claimed detail.
im=mat.node_tree.nodes['Image Texture'].image;ar=np.array(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4);med=np.median(ar[:,150:360,:3],axis=(0,1));ar[:,:,:3]=med*.88+ar[:,:,:3]*.12;im.pixels.foreach_set(ar.ravel());im.pack()
mi=len(m.materials);m.materials.append(mat)
bm=bmesh.new();bm.from_mesh(m)
for q in bm.verts:q.co=mw@q.co
for co,no in [((0,0,1.203),(0,0,1)),((0,0,1.285),(0,0,1)),((0,-.035,0),(0,1,0))]:
 fs=[]
 for f in bm.faces:
  p=f.calc_center_median()
  if abs(p.x)<.12 and -.22<p.y<.04 and 1.19<p.z<1.30:fs.append(f)
 geom=set(fs)
 for f in fs:geom.update(f.verts);geom.update(f.edges)
 bmesh.ops.bisect_plane(bm,geom=list(geom),dist=.0000001,plane_co=co,plane_no=no)
todel=[]
for f in bm.faces:
 p=f.calc_center_median()
 if abs(p.x)<.114 and p.y<-.0350001 and 1.2030001<p.z<1.2849999:todel.append(f)
borders=set(e for f in todel for e in f.edges);bmesh.ops.delete(bm,geom=todel,context='FACES');remaining={e for e in borders if e.is_valid and e.is_boundary};parts=[]
while remaining:
 e=remaining.pop();part={e};todo=list(e.verts);vs=set(todo)
 while todo:
  q=todo.pop()
  for ee in q.link_edges:
   if ee in remaining:
    remaining.remove(ee);part.add(ee)
    for vv in ee.verts:
     if vv not in vs:vs.add(vv);todo.append(vv)
 if len(part)>200:parts.append((np.mean([q.co.y for q in vs]),part,vs))
assert len(parts)>=1,'No valid exterior repair loop'
_,edges,vs=min(parts,key=lambda item:item[0])
assert all(sum(e in edges for e in q.link_edges)==2 for q in vs),'Exterior cut is not a simple loop'
start=next(iter(vs));loop=[start];previous=None;current=start
while True:
 opts=[e.other_vert(current) for e in current.link_edges if e in edges and e.other_vert(current)!=previous]
 nxt=opts[0]
 if nxt==start:break
 loop.append(nxt);previous,current=current,nxt
assert len(loop)==len(vs)
# The fragmented side wall contains an inward notch; reconstruct its contour
# between unchanged upper and lower anatomical anchors before triangulation.
for side in [-1,1]:
 sideverts=[q for q in loop if abs(q.co.y+.035)<.00001 and q.co.x*side>0]
 if sideverts:
  qlo=min(sideverts,key=lambda q:q.co.z);qhi=max(sideverts,key=lambda q:q.co.z);xl=qlo.co.x;xh=qhi.co.x
  for q in sideverts:
   t=(q.co.z-1.203)/.082;q.co.x=xl*(1-t)+xh*t+side*.0015*np.sin(np.pi*t)
bound=np.array([q.co[:] for q in loop]);xz=bound[:,[0,2]]
area=np.sum(xz[:,0]*np.roll(xz[:,1],-1)-np.roll(xz[:,0],-1)*xz[:,1]);
if area<0:loop.reverse();bound=bound[::-1].copy();xz=xz[::-1].copy()
coords=[Vector(q) for q in xz]
for z in np.arange(1.204,1.285,.0018):
 for x in np.arange(-.106,.108,.0018):coords.append(Vector((x,z)))
out,oe,fs,ov,_,_=delaunay_2d_cdt(coords,[],[list(range(len(loop)))],1,1e-8,True)
P=np.array(out);X=P[:,0]/.1;Z=(P[:,1]-1.244)/.041
A=np.column_stack([np.ones(len(P)),X,X*X,X**3,X**4,Z,Z*Z,X*Z,X*X*Z]);bx=bound[:,0]/.1;bz=(bound[:,2]-1.244)/.041
AB=np.column_stack([np.ones(len(bound)),bx,bx*bx,bx**3,bx**4,bz,bz*bz,bx*bz,bx*bx*bz]);fit=np.linalg.lstsq(AB,bound[:,1],rcond=None)[0];Y=A@fit;fixed=np.zeros(len(P),dtype=bool);bmap={}
for i,ids in enumerate(ov):
 ids=[j for j in ids if j<len(loop)]
 if ids:fixed[i]=True;bmap[i]=ids[0];Y[i]=bound[ids[0],1]
# Harmonic residual makes an exact, smooth join to the measured cut perimeter.
res=Y-A@fit;E=np.array(oe);src=np.r_[E[:,0],E[:,1]];dst=np.r_[E[:,1],E[:,0]];deg=np.bincount(src,minlength=len(P))
for _ in range(500):
 avg=np.bincount(src,weights=res[dst],minlength=len(P))/np.maximum(deg,1);res[~fixed]=avg[~fixed]
Y=A@fit+res;new=[]
for i,(x,z) in enumerate(P):
 new.append(loop[bmap[i]] if i in bmap else bm.verts.new((x,Y[i],z)))
uvlayer=bm.loops.layers.uv.active;count=0
for ids in fs:
 if len(ids)!=3:continue
 try:f=bm.faces.new([new[j] for j in ids])
 except ValueError:continue
 f.material_index=mi;f.smooth=True
 # Front normals should point toward -Y.
 if f.normal.y>0:f.normal_flip()
 for l in f.loops:l[uvlayer].uv=((l.vert.co.x+.13)/.26,(l.vert.co.z-1.203)/.082)
 count+=1
bmesh.ops.recalc_face_normals(bm,faces=[f for f in bm.faces if f.material_index==mi])
for q in bm.verts:q.co=inv@q.co
bm.to_mesh(m);bm.free();m.update()
(R/'surface-reconstruction.json').write_text(json.dumps({'method':'Exact plane cuts, exterior-boundary constrained Delaunay patch, harmonic boundary residual, shared boundary vertices','removed_fold_faces':len(todel),'stitched_boundary_vertices':len(loop),'new_local_triangles':count,'z_bounds':[1.203,1.285],'front_cut_y':-.035,'texture':'Original Candidate A skin donor infill; no recovered fine detail claim','boundary':bound.tolist()},indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'NYRA-Final-Recovery.blend'),compress=True);print('Stitched patch complete',flush=True)
