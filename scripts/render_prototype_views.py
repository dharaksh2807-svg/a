import bpy
import math
import mathutils

def render_prototype():
    blend_path = "production_v3/prototype/nyra_head_prototype.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    
    scene = bpy.context.scene
    
    # Cycles + Metal setup
    scene.render.engine = 'CYCLES'
    preferences = bpy.context.preferences
    cycles_prefs = preferences.addons['cycles'].preferences
    cycles_prefs.compute_device_type = 'METAL'
    cycles_prefs.refresh_devices()
    for d in cycles_prefs.devices:
        if d.type == 'METAL':
            d.use = True
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = False
    
    # World background (matches baseline)
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs['Color'].default_value = (0.04, 0.04, 0.05, 1.0)
    bg_node.inputs['Strength'].default_value = 0.4
    
    # Neutral Clay Material
    clay_mat = bpy.data.materials.new("NeutralClay")
    clay_mat.use_nodes = True
    bsdf = clay_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.75, 0.72, 0.70, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.40
    
    # Eye Material
    eye_mat = bpy.data.materials.new("ClayEye")
    eye_mat.use_nodes = True
    eye_bsdf = eye_mat.node_tree.nodes.get("Principled BSDF")
    eye_bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.14, 1.0)
    eye_bsdf.inputs['Roughness'].default_value = 0.10

    body = bpy.data.objects["GEO-body_female_realistic"]
    eye_l = bpy.data.objects["GEO-body_female_realistic.eye.L"]
    eye_r = bpy.data.objects["GEO-body_female_realistic.eye.R"]

    body.data.materials.clear()
    eye_l.data.materials.clear()
    eye_r.data.materials.clear()

    body.data.materials.append(clay_mat)
    eye_l.data.materials.append(eye_mat)
    eye_r.data.materials.append(eye_mat)

    # 3-Point Lighting Rig focused on head at (0, -0.05, 1.53)
    target_pos = mathutils.Vector((0.0, -0.05, 1.53))

    key_data = bpy.data.lights.new("KeyLight", type='AREA')
    key_data.energy = 160
    key_data.size = 0.6
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    key_obj.location = (-0.6, -1.0, 1.9)
    scene.collection.objects.link(key_obj)

    fill_data = bpy.data.lights.new("FillLight", type='AREA')
    fill_data.energy = 60
    fill_data.size = 0.9
    fill_data.color = (0.85, 0.90, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    fill_obj.location = (0.7, -0.9, 1.5)
    scene.collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new("RimLight", type='AREA')
    rim_data.energy = 120
    rim_data.size = 0.5
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    rim_obj.location = (0.4, 0.8, 2.1)
    scene.collection.objects.link(rim_obj)

    for light_obj in [key_obj, fill_obj, rim_obj]:
        dir = target_pos - light_obj.location
        light_obj.rotation_euler = dir.to_track_quat('-Z', 'Y').to_euler()

    # Camera
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = 85.0
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    def render_view(loc, target, filename):
        cam_obj.location = loc
        direction = mathutils.Vector(target) - mathutils.Vector(loc)
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = filename
        bpy.ops.render.render(write_still=True)
        print(f"Rendered: {filename}")

    target = (0.0, -0.05, 1.53)
    dist = 0.95

    # 1. Front Head
    render_view((0.0, -0.05 - dist, 1.53), target, "production_v3/prototype/renders/nyra_prototype_head_front.png")

    # 2. Side Head (Left profile: looking from +X)
    render_view((dist, -0.05, 1.53), target, "production_v3/prototype/renders/nyra_prototype_head_side.png")

    # 3. Three-Quarter Head
    rad34 = math.radians(35)
    x_34 = dist * math.sin(rad34)
    y_34 = -0.05 - dist * math.cos(rad34)
    render_view((x_34, y_34, 1.55), target, "production_v3/prototype/renders/nyra_prototype_head_threequarter.png")

if __name__ == "__main__":
    render_prototype()
