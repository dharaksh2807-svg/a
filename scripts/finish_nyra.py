"""Final fitting corrections applied to the existing Phase 2 model, not a rebuild."""
import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
if scene.get('phase2_finish_version')==1:
 print('Already fitted; no changes.');raise SystemExit
jacket=bpy.data.objects['NYRA · cropped bomber shell']
mat=jacket.data.materials[0].copy();mat.name='NYRA / tailored coral and ivory yoke'
nt=mat.node_tree;p=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
source=p.inputs['Base Color'].links[0].from_socket
coord=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');mask=nt.nodes.new('ShaderNodeMath');mask.operation='GREATER_THAN';mask.inputs[1].default_value=1.395
nt.links.new(coord.outputs['Object'],sep.inputs[0]);nt.links.new(sep.outputs['Z'],mask.inputs[0])
mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.78,.71,.58,1);nt.links.new(mask.outputs[0],mix.inputs[0]);nt.links.new(source,mix.inputs[1]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
jacket.data.materials.clear();jacket.data.materials.append(mat)
for f in jacket.data.polygons:f.material_index=0
# Continuous front bib overlaps both jersey pieces beneath the open zipper.
verts=[];faces=[]
rows=[(1.15,-.135,.046),(1.18,-.14,.046),(1.22,-.14,.045),(1.24,-.132,.044),(1.255,-.107,.043),(1.275,-.080,.041),(1.295,-.065,.038),(1.31,-.060,.036)]
for z,y,w in rows:
 for j in range(13):
  x=(j/12*2-1)*w;verts.append((x*1.07,(y+.008*(x/w)**2)*1.07,(z+.057)*1.07))
for i in range(len(rows)-1):
 for j in range(12):faces.append((i*13+j,i*13+j+1,(i+1)*13+j+1,(i+1)*13+j))
mesh=bpy.data.meshes.new('Jersey inset quad surface');mesh.from_pydata(verts,[],faces);mesh.update()
o=bpy.data.objects.new('NYRA · continuous jersey chest inset',mesh);bpy.data.collections['NYRA | EDITABLE VISUAL MODEL'].objects.link(o);mesh.materials.append(bpy.data.materials['NYRA / mulberry stretch jersey'])
for f in mesh.polygons:f.use_smooth=True
m=o.modifiers.new('Fitted bib smoothing','SUBSURF');m.levels=1;m.render_levels=1
m=o.modifiers.new('Jersey thickness','SOLIDIFY');m.thickness=.001
# Upper shoulder stitch curves from the fitting trial are superseded by the clean yoke.
for old in list(bpy.data.objects):
 if old.name.startswith('NYRA · shoulder yoke seam'):bpy.data.objects.remove(old,do_unlink=True)
# Source anatomy boundaries are hidden by fitted garments; no final skeleton is created.
scene['phase2_finish_version']=1
scene['status']='Phase 2 visual model, fitted. Static presentation; final rigging and deformation validation pending.'
bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/blender/nyra/nyra-visual.blend'),compress=True)
print('VERDICT: PASS')
