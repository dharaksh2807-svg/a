import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1];o=bpy.data.objects['NYRA · cropped bomber shell']
g=o.vertex_groups.get('Tailored shoulder relaxation') or o.vertex_groups.new(name='Tailored shoulder relaxation')
for v in o.data.vertices:
 w=max(0,min(1,(v.co.z-1.25)/.09))*max(0,min(1,(.28-abs(v.co.x))/.06))
 if w:g.add([v.index],w,'REPLACE')
m=o.modifiers.get('Tailored shoulder relaxation') or o.modifiers.new('Tailored shoulder relaxation','SMOOTH');m.factor=.8;m.iterations=22;m.vertex_group=g.name
bpy.context.view_layer.objects.active=o
bpy.ops.object.modifier_move_up(modifier=m.name)
bpy.ops.object.modifier_move_up(modifier=m.name)
bpy.context.scene['phase2_finish_version']=2
bpy.ops.wm.save_as_mainfile(filepath=str(root/'source/blender/nyra/nyra-visual.blend'),compress=True)
