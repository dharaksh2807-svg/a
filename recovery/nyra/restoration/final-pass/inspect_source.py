import bpy, numpy as np, json
from pathlib import Path
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R.parents[1]/'candidates/candidate-a/renders/original/nyra-review.blend'))
o=bpy.data.objects['Mesh_0'];m=o.data; w=o.matrix_world
v=np.array([(w@x.co)[:] for x in m.vertices]); faces=np.array([p.vertices[:] for p in m.polygons]); uv=np.array([x.uv[:] for x in m.uv_layers.active.data]); li=np.array([l.vertex_index for l in m.loops]);
imgs=[i for i in bpy.data.images if i.type=='IMAGE']
info={'objects':[(x.name,x.type) for x in bpy.data.objects], 'vertices':len(v),'faces':len(faces),'bounds':[v.min(0).tolist(),v.max(0).tolist()], 'images':[(i.name,list(i.size)) for i in imgs], 'materials':[]}
for mat in m.materials:
 info['materials'].append({'name':mat.name,'nodes':[(n.name,n.type) for n in mat.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links]})
base=next(l.from_node.image for l in m.materials[0].node_tree.links if l.to_socket.name=='Base Color')
px=np.array(base.pixels[:],dtype=np.float32).reshape(base.size[1],base.size[0],4)
colors=px[np.clip((uv[:,1]*base.size[1]).astype(int),0,base.size[1]-1),np.clip((uv[:,0]*base.size[0]).astype(int),0,base.size[0]-1),:3]
c=np.zeros((len(v),3));cnt=np.bincount(li,minlength=len(v));np.add.at(c,li,colors);c/=np.maximum(cnt[:,None],1)
np.savez_compressed('/tmp/nyra-original.npz',v=v,f=faces,colors=c,uv=uv)
(R/'source-inspection.json').write_text(json.dumps(info,indent=2)); print(json.dumps(info))
