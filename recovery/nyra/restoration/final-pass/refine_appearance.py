"""Reference-guided localized atlas repair; retain original geometry and UVs."""
import bpy,numpy as np,json,math,sys
from pathlib import Path
R=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(R/'NYRA-Final-Recovery.blend'))
o=bpy.data.objects['Mesh_0'];m=o.data;w=o.matrix_world;v=np.array([(w@q.co)[:] for q in m.vertices]);base=m.materials[0].node_tree.nodes['Image Texture'].image

with bpy.data.libraries.load(str(R.parents[1]/'candidates/candidate-a/renders/original/nyra-review.blend'),link=False) as (src,dst):dst.images=['Image_0']
base=dst.images[0]
W,H=base.size;px=np.array(base.pixels[:],dtype=np.float32).reshape(H,W,4);source=px.copy()
ref=bpy.data.images.load(str(R.parents[1]/'inputs/nyra-face.png'));rw,rh=ref.size;rp=np.array(ref.pixels[:],dtype=np.float32).reshape(rh,rw,4)
uv=np.array([d.uv[:] for d in m.uv_layers.active.data]);painted=0;affected=np.zeros((H,W),dtype=bool)
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
for p in m.polygons:
 ids=list(p.vertices);pos=v[ids];c=pos.mean(0)
 isface=(1.529<c[2]<1.684 and abs(c[0]-.004)<.074 and c[1]<-.073)
 ishair=False  # Reference hair projection rejected after visual inspection.
 issole=c[2]<.067
 isband=(1.286<c[2]<1.322 and abs(c[0])<.095 and c[1]<-.09)
 if not (isface or ishair or issole or isband):continue
 U=uv[list(p.loop_indices)]*np.array([W,H]);a,b,d=U[:3];den=(b[1]-d[1])*(a[0]-d[0])+(d[0]-b[0])*(a[1]-d[1])
 if abs(den)<1e-8:continue
 mn=np.maximum(np.floor(U.min(0)).astype(int),0);mx=np.minimum(np.ceil(U.max(0)).astype(int),[W-1,H-1])
 if np.any(mx<mn):continue
 xx,yy=np.meshgrid(np.arange(mn[0],mx[0]+1),np.arange(mn[1],mx[1]+1));xx=xx.ravel();yy=yy.ravel();X=xx+.5;Y=yy+.5
 aa=((b[1]-d[1])*(X-d[0])+(d[0]-b[0])*(Y-d[1]))/den;bb=((d[1]-a[1])*(X-d[0])+(a[0]-d[0])*(Y-d[1]))/den;cc=1-aa-bb;keep=(aa>=-.015)&(bb>=-.015)&(cc>=-.015)
 xx=xx[keep];yy=yy[keep];P=aa[keep,None]*pos[0]+bb[keep,None]*pos[1]+cc[keep,None]*pos[2]
 if not len(P):continue
 x,y,z=P.T;old=source[yy,xx,:3];skin=(old[:,0]>.40)&(old[:,0]>old[:,2]*1.15)&(old[:,1]>.20)
 eyes=(z>1.612)&(z<1.645)&(x>-.033)&(x<.047)&(y>-.112)&(y<-.077)
 lips=(z>1.543)&(z<1.583)&(abs(x-.003)<.043)&(y<-.075)
 weight=smooth((.071-abs(x-.004))/.016)*smooth((z-1.529)/.016)*smooth((1.682-z)/.018)*(skin|eyes|lips)
 weight*=np.where(eyes|lips,1.0,.72)
 if not isface:weight*=0
 # Landmarks fitted to existing Candidate A nose, lip and orbital positions.
 u=640+(x-.005)*2700
 yp=np.interp(z,[1.529,1.551,1.565,1.588,1.623,1.638,1.670,1.69],[820,762,718,635,518,470,360,300]);vv=rh-1-yp
 u=np.clip(u,0,rw-2);vv=np.clip(vv,0,rh-2);ix=u.astype(int);iy=vv.astype(int);fx=(u-ix)[:,None];fy=(vv-iy)[:,None]
 color=(rp[iy,ix,:3]*(1-fx)+rp[iy,ix+1,:3]*fx)*(1-fy)+(rp[iy+1,ix,:3]*(1-fx)+rp[iy+1,ix+1,:3]*fx)*fy
 # Reference is a beauty-lit illustration; blend its detail into original color.
 color=np.clip(color*np.array([1.02,1.01,1.015]),0,1)
 if ishair:
  hu=np.clip(640+(x-.005)*2850,0,rw-1).astype(int);hy=np.clip(rh-1-np.interp(z,[1.42,1.625,1.69,1.78],[1160,518,260,0]),0,rh-1).astype(int);hc=rp[hy,hu,:3];ha=rp[hy,hu,3]
  hw=((ha>.95)&(hc.mean(1)<.32)&(old.mean(1)<.45)).astype(float)*.72
  color=hc;weight=hw
 if issole:
  # Original purple-and-white palette, repaired outsole color bands.
  rubber=np.where((z<.016)[:,None],np.array([.19,.105,.23]),np.array([.76,.735,.77]));shade=np.clip(old.mean(1)/.55,.83,1.1)
  color=rubber*shade[:,None];weight=smooth((.067-z)/.012)*.94
 if isband:
  leak=(old[:,0]>old[:,2]*1.15)&(old[:,0]>.45);color=np.tile(np.array([.22,.075,.26]),(len(P),1));weight=leak.astype(float)*smooth((z-1.286)/.006)*smooth((1.322-z)/.006)
 px[yy,xx,:3]=old*(1-weight[:,None])+color*weight[:,None];affected[yy[weight>.01],xx[weight>.01]]=True;painted+=1
# Write distinct packed atlas; untouched texels are bit-identical in float data.
im=bpy.data.images.new('NYRA / localized reference facial paint',width=W,height=H,alpha=True);im.pixels.foreach_set(px.ravel());im.pack()
for mat in list(m.materials)[:5]:
 mat.node_tree.nodes['Image Texture'].image=im
# Shape a shallow continuous outsole channel on the original sneakers.
inv=w.inverted();changed=0
for vert in m.vertices:
 co=w@vert.co
 if co.z<.075 and '--texture-only' not in sys.argv:
  groove=.003*math.exp(-((co.z-.035)/.005)**2);cx=.148 if co.x>0 else -.148;dx=co.x-cx;dy=co.y+.045;length=math.hypot(dx,dy)
  if length>.02:co.x-=groove*dx/length;co.y-=groove*dy/length;vert.co=inv@co;changed+=1
m.update()
(R/'appearance-evidence.json').write_text(json.dumps({'facial_reference':'recovery/nyra/inputs/nyra-face.png','authority_note':'Existing derived facial guide; approved-concept.png remains design authority. No new reference generated.','atlas_texels_edited':int(affected.sum()),'atlas_triangles_processed':painted,'shoe_vertices_edited_in_this_invocation':changed,'limitations':['Facial paint is a projection onto original geometry, not new eye anatomy','No claim of recovered native high-frequency skin or hair detail']},indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'NYRA-Final-Recovery.blend'),compress=True)
print('Localized appearance pass complete',flush=True)
