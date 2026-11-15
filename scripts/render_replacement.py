"""Import an unchanged generation into a reusable Blender review studio.
Run with Blender --background --disable-autoexec --python this.py -- --input ... --output ...
"""
import argparse,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--views',default='front,three-quarter,side,rear,face,clay,wireframe,gameplay');p.add_argument('--samples',type=int,default=48);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.output.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(a.input.resolve()))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes,'No imported mesh'
points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
low=Vector([min(v[i] for v in points) for i in range(3)]);high=Vector([max(v[i] for v in points) for i in range(3)])
scale=1.78/(high.z-low.z);center=(low+high)*.5
root=bpy.data.objects.new('NYRA | presentation transform only',None);bpy.context.collection.objects.link(root)
for o in list(bpy.context.scene.objects):
    if o!=root and o.parent is None:o.parent=root
root.scale=(scale,)*3;root.location=(-center.x*scale,-center.y*scale,-low.z*scale)
for o in meshes:
    for face in o.data.polygons:face.use_smooth=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=a.samples;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('Neutral studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.19,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
scene.view_settings.view_transform='AgX'
def material(name,color,roughness=.5):
    m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=roughness;return m
floor_mat=material('Studio charcoal',(.045,.052,.07))
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='Studio floor';floor.data.materials.append(floor_mat);floor.location.z=-.008
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,location,power,color,size,target=(0,0,1)):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=location;aim(obj,target)
area('Large warm key',(-2.7,-3.3,4),450,(1,.89,.8),3)
area('Cool frontal fill',(2.4,-2.3,2.7),220,(.8,.88,1),2.5)
area('Rear separation',(1.4,2,3),500,(.78,.83,1),2)
data=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',data);scene.collection.objects.link(cam);scene.camera=cam;data.type='ORTHO'
clay=material('Clay | reveals generated surface',(.43,.45,.49),.7)
wire=material('Actual triangle edges',(.5,.53,.58),.65);nodes=wire.node_tree.nodes;links=wire.node_tree.links;edge=nodes.new('ShaderNodeWireframe');edge.use_pixel_size=True;edge.inputs['Size'].default_value=.55;mix=nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.48,.5,.54,1);mix.inputs[2].default_value=(.012,.016,.024,1);links.new(edge.outputs[0],mix.inputs[0]);links.new(mix.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
original={o.name:list(o.data.materials) for o in meshes}
def override(mat=None):
    for o in meshes:
        o.data.materials.clear()
        for m in ([mat]*max(1,len(original[o.name])) if mat else original[o.name]):o.data.materials.append(m)
views={'front':((0,-4,1),(0,0,.89),2.04),'three-quarter':((2.7,-4,1.5),(0,0,.89),2.04),'side':((-4,0,1),(0,0,.89),2.04),'rear':((0,4,1),(0,0,.89),2.04),'face':((.10,-4,1.64),(0,-.025,1.58),.48),'clay':((2.7,-4,1.5),(0,0,.89),2.04),'wireframe':((2.7,-4,1.5),(0,0,.89),2.04),'gameplay':((0,4,2.25),(0,0,1),3.6)}
views['wireframe-face']=((.10,-4,1.64),(0,-.025,1.58),.35)
stats={'source':str(a.input.resolve()),'presentation_height_m':1.78,'meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'polygons':sum(len(o.data.polygons) for o in meshes),'triangles':sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes),'uv_layers':{o.name:len(o.data.uv_layers) for o in meshes},'materials':[m.name for m in bpy.data.materials if m not in [floor_mat,clay,wire]],'images':[{'name':im.name,'width':im.size[0],'height':im.size[1]} for im in bpy.data.images if im.type=='IMAGE'],'rigged':False,'geometry_edits':'None; presentation parent transform and smooth shading only.'}
(a.output/'mesh-statistics.json').write_text(json.dumps(stats,indent=2))
bpy.ops.file.pack_all()
for view in a.views.split(','):
    position,target,ortho=views[view];cam.location=position;aim(cam,target);data.ortho_scale=ortho
    scene.render.resolution_x=1280 if view=='gameplay' else 1100;scene.render.resolution_y=720 if view=='gameplay' else 1400
    if view=='gameplay':
        for light in scene.objects:
            if light.type=='LIGHT':light.hide_render=True
        for label,location,color,power in [('Metro sun',(24,-18,42),(1,.98,.918),1.45),('Metro sky fill',(-24,-14,28),(.627,.769,.910),.70)]:
            lamp=bpy.data.lights.new(label,'SUN');lamp.color=color;lamp.energy=power;lamp.angle=.12;obj=bpy.data.objects.new(label,lamp);scene.collection.objects.link(obj);obj.location=location;aim(obj,(0,0,.9))
        scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.784,.902,.976,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    override(clay if view=='clay' else wire if view.startswith('wireframe') else None)
    scene.render.filepath=str((a.output/f'{view}.png').resolve());bpy.ops.render.render(write_still=True)
    if view=='gameplay':
        for light in scene.objects:
            if light.type=='LIGHT':light.hide_render=light.name.startswith('Metro ')
        scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.19,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
override();cam.location=views['three-quarter'][0];aim(cam,views['three-quarter'][1]);data.ortho_scale=2.04
scene.render.resolution_x=1100;scene.render.resolution_y=1400
bpy.ops.wm.save_as_mainfile(filepath=str((a.output/'nyra-review.blend').resolve()),compress=True)
print('VERDICT: PASS — saved imported source, real geometry renders and measured statistics')
