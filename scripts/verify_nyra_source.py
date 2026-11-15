"""Read-only checks of the delivered authoring file."""
import bpy,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
objects=list(bpy.data.collections['NYRA | EDITABLE VISUAL MODEL'].objects)
checks={
 'fitting_revision_6':bpy.context.scene.get('phase2_finish_version')==6,
 'waistband_within_torso':max(abs(v.co.x) for v in bpy.data.objects['NYRA · track waistband'].data.vertices)<.22,
 'no_final_armature':not any(o.type=='ARMATURE' for o in objects),
 'editable_identity_key':bool(bpy.data.objects['NYRA · face identity'].data.shape_keys.key_blocks.get('NYRA adult identity')),
 'finite_mesh_coordinates':all(math.isfinite(c) for o in objects if o.type=='MESH' for v in o.data.vertices for c in v.co),
 'all_meshes_have_uvs':all(len(o.data.uv_layers)>0 for o in objects if o.type=='MESH'),
 'all_meshes_have_materials':all(len(o.data.materials)>0 for o in objects if o.type=='MESH'),
 'all_used_images_packed':all(bool(i.packed_file) or len(i.packed_files)>0 for i in bpy.data.images if i.users and i.source in {'FILE','TILED'}),
 'no_external_blend_libraries':not bpy.data.libraries,
 'no_embedded_autorun_scripts':not any(t.use_module for t in bpy.data.texts)
}
r={'checks':checks,'pass':all(checks.values()),'blender':bpy.app.version_string,'images':[{'name':i.name,'packed':bool(i.packed_file) or len(i.packed_files)>0} for i in bpy.data.images if i.users]}
(root/'qa/phase2/source-validation.json').write_text(json.dumps(r,indent=2))
print(json.dumps(checks,indent=2));print('VERDICT: PASS' if r['pass'] else 'VERDICT: FAIL -- source check failed')
if not r['pass']:raise RuntimeError('Source checks failed')
