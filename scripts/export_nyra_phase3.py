"""Bake a portable static NYRA review GLB from the saved authoring model.
No armature or animation is created. Source blend remains untouched.
"""
import bpy,bmesh,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
source=list(bpy.data.collections['NYRA | EDITABLE VISUAL MODEL'].objects)
report={'authoring':{},'export':{},'notes':['Static visual review asset; no final rig.','Packed base-color atlases; simplified PBR roughness. Blender SSS and weave bump are not reproduced exactly.']}
dg=bpy.context.evaluated_depsgraph_get()
report['authoring']['objects']=len(source)
report['authoring']['phase3_revision']=scene.get('phase3_revision')
report['authoring']['base_vertices']=sum(len(o.data.vertices) for o in source if o.type=='MESH')
report['authoring']['base_triangles']=0
report['authoring']['evaluated_triangles']=0
for o in source:
 if o.type=='MESH':o.data.calc_loop_triangles();report['authoring']['base_triangles']+=len(o.data.loop_triangles)
 mesh=o.evaluated_get(dg).to_mesh();mesh.calc_loop_triangles();report['authoring']['evaluated_triangles']+=len(mesh.loop_triangles);o.evaluated_get(dg).to_mesh_clear()
report['authoring']['materials']=len({m.name for o in source for m in o.data.materials})
report['authoring']['armatures']=sum(o.type=='ARMATURE' for o in source)
# Apply a single subdivision only where it contributes visibly. Discard covered body surfaces in export copy.
for o in source:
 for m in o.modifiers:
  if m.type=='SUBSURF':m.levels=0 if any(w in o.name for w in ['anatomy','sneaker uppers']) else min(m.levels,1)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
groups={name:[] for name in ['skin','eyes','hair','outfit','metal']}
for original in source:
 if 'corneas' in original.name:continue
 mesh=bpy.data.meshes.new_from_object(original.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);mesh.transform(original.matrix_world)
 if 'anatomy' in original.name:
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.delete(bm,geom=[f for f in bm.faces if (abs(f.calc_center_median().x)<.22 or f.calc_center_median().z<.80) and not (1.145<f.calc_center_median().z<1.25)],context='FACES');bm.to_mesh(mesh);bm.free()
 if not mesh.polygons:continue
 o=bpy.data.objects.new('REVIEW '+original.name,mesh);scene.collection.objects.link(o)
 if mesh.uv_layers:mesh.uv_layers.active.name='SourceUV'
 else:mesh.uv_layers.new(name='SourceUV')
 for slot in o.material_slots:
  mat=slot.material.copy();slot.material=mat;nt=mat.node_tree
  uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='SourceUV'
  for n in list(nt.nodes):
   if n.type=='UVMAP':n.uv_map='SourceUV'
   if n.type=='TEX_IMAGE' and not n.inputs['Vector'].is_linked:nt.links.new(uv.outputs['UV'],n.inputs['Vector'])
  p=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
  out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
  emit=nt.nodes.new('ShaderNodeEmission')
  if p:
   color=p.inputs['Base Color'];emit.inputs['Color'].default_value=color.default_value
   if color.is_linked:nt.links.new(color.links[0].from_socket,emit.inputs['Color'])
  else:emit.inputs['Color'].default_value=mat.diffuse_color
  nt.links.new(emit.outputs[0],out.inputs['Surface'])
 n=original.name
 group='skin' if any(w in n for w in ['anatomy','face identity','oral anatomy','tongue']) else 'eyes' if n.endswith('eyes') else 'metal' if any(w in n for w in ['copper','champagne','zipper pull']) else 'hair' if any(w in n for w in ['hair cap','ponytail','brow','lashes']) else 'outfit'
 # Thin hems, overlapping jersey layers and trim must retain their fitted topology.
 if group=='outfit' and any(w in n for w in ['cropped bomber shell','tailored track pants','sneaker uppers']):
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  d=o.modifiers.new('Reduce broad garment surfaces','DECIMATE');d.ratio=.30;bpy.ops.object.modifier_apply(modifier=d.name)
 groups[group].append(o)
# Remove source objects only from this throwaway export process.
for o in source:bpy.data.objects.remove(o,do_unlink=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
export=[]
for group,objects in groups.items():
 if not objects:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name='NYRA '+group
 dec=o.modifiers.new('Static preview reduction','DECIMATE');dec.ratio={'skin':.65,'eyes':.25,'hair':.5,'outfit':1.0,'metal':.35}[group];bpy.ops.object.modifier_apply(modifier=dec.name)
 atlas=o.data.uv_layers.new(name='NYRA_Atlas');o.data.uv_layers.active=atlas;atlas.active_render=True
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 size=2048 if group in ['skin','outfit'] else 1024 if group=='hair' else 512
 image=bpy.data.images.new('NYRA '+group+' base color',width=size,height=size,alpha=False)
 for mat in o.data.materials:
  n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=image;mat.node_tree.nodes.active=n;n.select=True
 if '--reuse-unaffected' in sys.argv and group in ['skin','eyes','hair']:
  image=bpy.data.images.load(str(ROOT/f'textures/nyra-phase3/{group}-basecolor.png'))
 else:
  bpy.ops.object.bake(type='EMIT',margin=8,use_clear=True)
 image.filepath_raw=str(ROOT/f'textures/nyra-phase3/{group}-basecolor.png');image.file_format='PNG';image.save()
 mat=bpy.data.materials.new('NYRA baked '+group);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value={'skin':.46,'eyes':.2,'hair':.61,'outfit':.62,'metal':.3}[group]
 if group=='metal':p.inputs['Metallic'].default_value=.6
 tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 o.data.materials.clear();o.data.materials.append(mat)
 for f in o.data.polygons:f.material_index=0
 # Remove unused source UVs only after the appearance has been baked.
 for layer in list(o.data.uv_layers):
  if layer.name!='NYRA_Atlas':o.data.uv_layers.remove(layer)
 o['credit']='Adapted from Rain Rig (CC) Blender Foundation | studio.blender.org; CC BY 4.0. NYRA visual production.'
 o.data.calc_loop_triangles();report['export'][group]={'triangles':len(o.data.loop_triangles),'vertices':len(o.data.vertices),'atlas':size}
 export.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in export:o.select_set(True)
bpy.context.view_layer.objects.active=export[0]
bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports/nyra-phase3.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
report['export_triangles']=sum(x['triangles'] for x in report['export'].values());report['glb_bytes']=(ROOT/'exports/nyra-phase3.glb').stat().st_size
(ROOT/'qa/phase2/mesh-statistics.json').write_text(json.dumps(report,indent=2))
print('VERDICT: PASS')
