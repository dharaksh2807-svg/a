"""Structural/export checks; does not certify artistic quality."""
import bpy,numpy as np,json,math,hashlib,struct
from pathlib import Path
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'NYRA-Final-Recovery.blend'));o=bpy.data.objects['Mesh_0'];m=o.data;pos=np.array([(o.matrix_world@q.co)[:] for q in m.vertices]);raw=np.load('/tmp/nyra-original.npz');orig=raw['v']
np.savez_compressed('/tmp/nyra-final.npz',v=pos)
k=KDTree(len(pos))
for i,p in enumerate(pos):k.insert(p,i)
k.balance()
protected=(abs(orig[:,0])<.11)&(orig[:,1]<-.065)&(orig[:,2]>1.12)&(orig[:,2]<1.200)
dist=[k.find(p)[2] for p in orig[protected]]
checks={'master_reopens':True,'finite_vertices':bool(np.isfinite(pos).all()),'navel_and_belt_original_positions_preserved':max(dist)<1e-6,'packed_used_images':all(bool(im.packed_file) or len(im.packed_files)>0 for im in bpy.data.images if im.users and im.source=='FILE'),'no_armatures':not any(q.type=='ARMATURE' for q in bpy.data.objects),'no_external_libraries':len(bpy.data.libraries)==0}
info={'checks':checks,'vertex_count':len(pos),'polygons':len(m.polygons),'protected_original_vertices':int(protected.sum()),'maximum_nearest_position_error_m':float(max(dist)),'materials':[ma.name for ma in m.materials]}
# Read GLB manifest separately and then reimport through Blender.
blob=(R/'NYRA-Final-Recovery.glb').read_bytes();length,kind=struct.unpack_from('<II',blob,12);doc=json.loads(blob[20:20+length]);checks['glb_has_no_cameras_lights_or_rig']=not doc.get('cameras') and not doc.get('skins') and not doc.get('extensions',{}).get('KHR_lights_punctual')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'NYRA-Final-Recovery.glb'))
meshes=[q for q in bpy.context.scene.objects if q.type=='MESH'];checks['glb_reimports']=len(meshes)>0;checks['glb_has_no_studio_floor']=all('floor' not in q.name.lower() for q in meshes);info['glb_meshes']=[q.name for q in meshes];info['glb_material_count']=len(doc.get('materials',[]));info['blender']=bpy.app.version_string
info['sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'NYRA-Final-Recovery.blend',R/'NYRA-Final-Recovery.glb']};info['technical_pass']=all(checks.values());info['artistic_quality']='Requires independent visual approval; technical pass is not visual approval.'
(R/'validation.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2));print('VERDICT: PASS' if all(checks.values()) else 'VERDICT: FAIL -- structural or export check failed')
assert all(checks.values())
