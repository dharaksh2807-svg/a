"""Localized recovery of original Candidate A; no generated replacement body."""
import bpy,bmesh,numpy as np,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R.parents[1]/'candidates/candidate-a/renders/original/nyra-review.blend'))
o=bpy.data.objects['Mesh_0'];m=o.data;mw=o.matrix_world.copy(); inv=mw.inverted()
raw=np.load('/tmp/nyra-original.npz');orig=raw['v'];colors=raw['colors'];v=orig.copy();x,y,z=v.T
# Fit the intact skin anchors, not the protruding ridge or the belt.
# Skin transition: lower anchor 1.205-1.218; upper 1.268-1.279.
# Symmetric even-X cubic-Z field constrained by source anatomy on both sides.
skin=(colors[:,0]>.35)&(colors[:,0]>colors[:,2]*1.22)&(colors[:,1]>.19)
a=(abs(x)<.112)&(y<-.07)&skin&(((z>1.205)&(z<1.218))|((z>1.268)&(z<1.279)))
def design(x,z):
 t=(z-1.24)/.04
 return np.column_stack([np.ones(len(x)),x*x,t,t*t,t*t*t,x*x*t])
coef=np.linalg.lstsq(design(x[a],z[a]),y[a],rcond=None)[0]
target=design(x,z)@coef
# Entire folded wall moves both forwards and backwards; full strength across shelf.
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
w=smooth((z-1.203)/.017)*smooth((1.284-z)/.014)*smooth((.126-abs(x))/.018)*smooth((-y-.065)/.015)
# Ignore jacket/sleeves, include skin under the bra. Periphery blends to original.
v[:,1]=y+w*(target-y)
changes={'abdomen_vertices':int((w>0).sum()),'fit_coefficients':coef.tolist(),'anchor_vertices':int(a.sum()),'abdomen_roi':{'z':[1.203,1.284],'abs_x_max':.126,'front_y_max':-.065}}
for vert,co in zip(m.vertices,v):vert.co=inv@Vector(co)
# Weld coincident UV seam vertices without touching per-loop UVs. Recomputed
# continuous normals remove false triangular shading while retaining geometry.
bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bm.to_mesh(m);bm.free()
if m.has_custom_normals:
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 try:bpy.ops.mesh.customdata_custom_splitnormals_clear()
 except Exception:pass
for p in m.polygons:p.use_smooth=True
m.update();n=len(m.vertices);pos=np.array([(mw@q.co)[:] for q in m.vertices]);original_welded=pos.copy();x,y,z=pos.T
edges=np.empty(len(m.edges)*2,dtype=np.int32);m.edges.foreach_get('vertices',edges);edges=edges.reshape(-1,2);src=np.r_[edges[:,0],edges[:,1]];dst=np.r_[edges[:,1],edges[:,0]];degree=np.bincount(src,minlength=n)
# Low amplitude relaxation; no body replacement, no rescale of proportions.
hair=(z>1.69)|((z>1.46)&(abs(x)>.071))|((z>1.48)&(y>.025))
face=(z>1.533)&(z<1.66)&(abs(x)<.062)&(y<-.083)
shoe=z<.19
cloth=(z>.23)&(z<1.1)&(abs(x)<.21)
weights=np.zeros(n);weights[cloth]=.12;weights[shoe]=.25;weights[hair]=.30;weights[face]=.2
# Protect abdomen, navel, belt, hands. Targeted smoothing acts only on named zones.
for it in range(4):
 sums=np.zeros_like(pos);np.add.at(sums,src,pos[dst]);avg=sums/np.maximum(degree[:,None],1)
 delta=(avg-pos)*weights[:,None];length=np.linalg.norm(delta,axis=1);delta*=np.minimum(1,.0012/np.maximum(length,1e-12))[:,None];pos+=delta
# Correct over-inflated lips with smooth local field, keeping original vermilion UV.
x,y,z=pos.T
lip=np.exp(-((x-.003)/.036)**6-((z-1.567)/.019)**6)*(y<-.10)
pos[:,0]+=-.07*(x-.003)*lip;pos[:,2]+=-.11*(z-1.567)*lip
# Flatten lowest outsole points into a consistent contact band.
sole=smooth((.024-z)/.014);pos[:,2]=z*(1-.6*sole)
for vert,co in zip(m.vertices,pos):vert.co=inv@Vector(co)
m.update();changes['welded_vertices']=n;changes['relaxed_vertices']=int((weights>0).sum())
# Original atlas retained. Separate roughness for hair/skin/fabric follows the
# source's own color and anatomical regions; no synthetic detail claimed.
base=m.materials[0];li=np.array([l.vertex_index for l in m.loops]);uv=np.array([d.uv[:] for d in m.uv_layers.active.data]);im=base.node_tree.nodes['Image Texture'].image;px=np.array(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4)
c=px[np.clip((uv[:,1]*im.size[1]).astype(int),0,im.size[1]-1),np.clip((uv[:,0]*im.size[0]).astype(int),0,im.size[0]-1),:3];cv=np.zeros((n,3));np.add.at(cv,li,c);cv/=np.maximum(np.bincount(li,minlength=n)[:,None],1)
skin=(cv[:,0]>.35)&(cv[:,0]>cv[:,2]*1.22)&(cv[:,1]>.19)
classes={'skin':(.48,0.0),'hair':(.58,0.0),'fabric':(.76,0.0),'rubber':(.68,0.0)}
for name,(rough,metal) in classes.items():
 mat=base.copy();mat.name='NYRA recovery / '+name;bs=mat.node_tree.nodes.get('Principled BSDF')
 for socket in ['Roughness','Metallic']:
  for link in list(bs.inputs[socket].links):mat.node_tree.links.remove(link)
 bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
 if name=='skin':bs.inputs['Subsurface Weight'].default_value=.035;bs.inputs['Subsurface Radius'].default_value=(.8,.35,.2)
 m.materials.append(mat)
# Polygon material labels, conservative face centers.
for p in m.polygons:
 ids=list(p.vertices);center=pos[ids].mean(0);col=cv[ids].mean(0);cx,cy,cz=center
 if skin[ids].mean()>.65:p.material_index=1
 elif (cz>1.68 or (cz>1.41 and (abs(cx)>.064 or cy>.015))) and col.mean()<.45:p.material_index=2
 elif cz<.065:p.material_index=4
 else:p.material_index=3
changes['notes']=['No new body or hairstyle generated','Original UV atlas remains packed','Localized surface field bridges entire shelf','Welded coincident vertices for continuous shading']
(R/'edit-evidence.json').write_text(json.dumps(changes,indent=2));np.savez_compressed('/tmp/nyra-after.npz',v=pos)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(Path('/tmp/nyra-stage1.blend')),compress=True)
print('Saved localized recovery for visual inspection',flush=True)
