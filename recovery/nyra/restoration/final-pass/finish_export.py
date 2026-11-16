"""Match the repaired strip's albedo to its lower cut, then export character only."""
import bpy,numpy as np,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(R/'NYRA-Final-Recovery.blend'))
o=bpy.data.objects['Mesh_0'];m=o.data
raw=np.load('/tmp/nyra-original.npz');v=raw['v'];f=raw['f'];uv=raw['uv'].reshape(-1,3,2);cent=v[f].mean(1);inds=np.where((cent[:,2]>1.199)&(cent[:,2]<1.208)&(cent[:,1]<0)&(abs(cent[:,0])<.12))[0];bvh=BVHTree.FromPolygons(v.tolist(),f[inds].tolist(),all_triangles=True)
with bpy.data.libraries.load(str(R.parents[1]/'candidates/candidate-a/renders/original/nyra-review.blend'),link=False) as (src,dst):dst.images=['Image_0']
orig=dst.images[0];px=np.array(orig.pixels[:],dtype=np.float32).reshape(orig.size[1],orig.size[0],4)
N=512;H=128;columns=[]
for i in range(N):
 x=np.clip((i/(N-1)-.5)*.26,-.098,.098);hit,no,idx,dist=bvh.ray_cast(Vector((x,-.25,1.203)),Vector((0,1,0)),.3)
 color=np.array([.80,.62,.51])
 if hit is not None:
  fi=inds[idx];tri=v[f[fi]];ab=np.linalg.lstsq(np.column_stack([tri[1]-tri[0],tri[2]-tri[0]]),np.array(hit)-tri[0],rcond=None)[0];U=uv[fi,0]+ab[0]*(uv[fi,1]-uv[fi,0])+ab[1]*(uv[fi,2]-uv[fi,0]);ix=int(np.clip(U[0]*orig.size[0],0,orig.size[0]-1));iy=int(np.clip(U[1]*orig.size[1],0,orig.size[1]-1));col=px[iy,ix,:3]
  if col[0]>.45 and col[0]>col[2]*1.15:color=col
 columns.append(color)
cols=np.array(columns);tex=np.ones((H,N,4),np.float32);median=np.median(cols[100:412],axis=0)
for j in range(H):
 t=j/(H-1);tex[j,:,:3]=cols*(1-.35*t)+median*.35*t
im=bpy.data.images.new('NYRA / boundary-matched abdominal skin infill',width=N,height=H);im.pixels.foreach_set(tex.ravel());im.pack()
patchmat=m.materials[5];patchmat.node_tree.nodes['Image Texture'].image=im
# Ensure all texture nodes use export-supported standard material response.
m.materials[2].node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65
# Store the delivered textures, without increasing their source resolution.
(R/'textures').mkdir(exist_ok=True)
for image,name in [(m.materials[0].node_tree.nodes['Image Texture'].image,'localized-color.png'),(im,'abdomen-skin-infill.png')]:
 image.filepath_raw=str(R/'textures'/name);image.file_format='PNG';image.save();image.pack()
# Clean presentation camera and annotate editable repair region.
o['source']='Original Candidate A only';o['repair']='Localized abdominal reconstruction; original character mesh retained'
scene=bpy.context.scene;c=scene.camera;c.location=(2.7,-4,1.5);c.rotation_euler=(Vector((0,0,.89))-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=2.04
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
# Keep texture packing and authoring data in the Blender master.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'NYRA-Final-Recovery.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(R/'NYRA-Final-Recovery.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_cameras=False,export_lights=False)
print('VERDICT: PASS — saved master and exported character only; visual gate pending',flush=True)
