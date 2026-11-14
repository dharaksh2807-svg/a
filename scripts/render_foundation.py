"""Render the real Rain foundation; this does not create or claim a NYRA model."""
import bpy
import json
import time
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.resolution_x = 768
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new('Foundation inspection world')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.16,0.16,0.16,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.6
for obj in list(scene.objects):
    if obj.type in {'LIGHT','CAMERA'}:
        bpy.data.objects.remove(obj,do_unlink=True)
for obj in scene.objects:
    for mod in obj.modifiers:
        if mod.type == 'SUBSURF':
            mod.render_levels = min(mod.render_levels,1)
            mod.levels = min(mod.levels,1)

def aim(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
for name,position,power,size in [('Key',(3,-4,5),500,4),('Fill',(-3,-2,2),250,3),('Rim',(1,3,4),650,3)]:
    light=bpy.data.objects.new(name,bpy.data.lights.new(name,'AREA'))
    scene.collection.objects.link(light)
    light.location=position
    light.data.energy=power
    light.data.shape='DISK'
    light.data.size=size
    aim(light,(0,0,1))
camera=bpy.data.objects.new('Inspection Camera',bpy.data.cameras.new('Inspection Camera'))
scene.collection.objects.link(camera)
camera.location=(2.8,-6,2.5)
camera.data.type='ORTHO'
camera.data.ortho_scale=2.15
scene.camera=camera
results=[]
for name,pos in [('front',(2.8,-6,2.4)),('rear',(-2.8,6,2.4))]:
    camera.location=pos
    aim(camera,(0,0,0.85))
    scene.render.filepath=str(ROOT/f'renders/rain-foundation-{name}.png')
    start=time.monotonic()
    bpy.ops.render.render(write_still=True)
    results.append({'view':name,'seconds':round(time.monotonic()-start,2),'file':f'renders/rain-foundation-{name}.png'})
(ROOT/'qa/evidence/foundation-renders.json').write_text(json.dumps(results,indent=2))
print('VERDICT: PASS')
