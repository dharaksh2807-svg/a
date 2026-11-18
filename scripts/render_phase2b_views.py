import bpy
import math
import mathutils

def render_phase2b():
    blend_path = "production_v3/prototype/nyra_head_prototype_v2.blend"
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
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = False
    
    # World background: Soft neutral light studio gray matching reference portrait
    world = bpy.data.worlds.new("Phase2BStudioWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.86, 0.86, 0.88, 1.0)
        bg_node.inputs['Strength'].default_value = 0.55
    
    # 3-Point Portrait Lighting Rig focused on head at (0, -0.05, 1.51)
    target_pos = mathutils.Vector((0.0, -0.05, 1.51))

    # Key light: Soft portrait key (front-left, slightly elevated)
    key_data = bpy.data.lights.new("KeyLight", type='AREA')
    key_data.energy = 85
    key_data.size = 0.8
    key_data.color = (1.0, 0.98, 0.96)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    key_obj.location = (-0.55, -1.25, 1.85)
    scene.collection.objects.link(key_obj)

    # Fill light: Gentle soft fill (front-right)
    fill_data = bpy.data.lights.new("FillLight", type='AREA')
    fill_data.energy = 45
    fill_data.size = 1.0
    fill_data.color = (0.95, 0.97, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    fill_obj.location = (0.65, -1.15, 1.55)
    scene.collection.objects.link(fill_obj)

    # Rim / Hair light: Highlights ponytail, silhouette, and purple hair streak
    rim_data = bpy.data.lights.new("RimLight", type='AREA')
    rim_data.energy = 75
    rim_data.size = 0.6
    rim_data.color = (1.0, 0.98, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    rim_obj.location = (0.35, 0.75, 1.95)
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

    dist = 1.12
    target = (0.0, -0.05, 1.51)

    # 1. Front Face View
    render_view((0.0, -0.05 - dist, 1.51), target, "production_v3/prototype/renders/nyra_phase2b_front.png")

    # 2. Three-Quarter Face View (32 degrees)
    rad34 = math.radians(32)
    x_34 = dist * math.sin(rad34)
    y_34 = -0.05 - dist * math.cos(rad34)
    render_view((x_34, y_34, 1.52), target, "production_v3/prototype/renders/nyra_phase2b_threequarter.png")

    # 3. Side Profile View (Left profile: looking from +X)
    render_view((dist, -0.05, 1.51), target, "production_v3/prototype/renders/nyra_phase2b_side.png")

if __name__ == "__main__":
    render_phase2b()
