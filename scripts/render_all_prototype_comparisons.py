import bpy
import math
import mathutils

def setup_scene(filepath):
    bpy.ops.wm.open_mainfile(filepath=filepath)
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
    
    # World background - neutral dark studio
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes['Background']
    bg_node.inputs['Color'].default_value = (0.04, 0.04, 0.05, 1.0)
    bg_node.inputs['Strength'].default_value = 0.35
    
    # Neutral Clay Material (mid-gray ~0.48 albedo, prevents clipping)
    clay_mat = bpy.data.materials.new("NeutralClay")
    clay_mat.use_nodes = True
    bsdf = clay_mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = (0.48, 0.46, 0.44, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.52
    
    # Eye Material (dark charcoal cornea with subtle sheen)
    eye_mat = bpy.data.materials.new("ClayEye")
    eye_mat.use_nodes = True
    eye_bsdf = eye_mat.node_tree.nodes.get("Principled BSDF")
    eye_bsdf.inputs['Base Color'].default_value = (0.10, 0.10, 0.12, 1.0)
    eye_bsdf.inputs['Roughness'].default_value = 0.12

    body = bpy.data.objects["GEO-body_female_realistic"]
    eye_l = bpy.data.objects["GEO-body_female_realistic.eye.L"]
    eye_r = bpy.data.objects["GEO-body_female_realistic.eye.R"]

    body.data.materials.clear()
    eye_l.data.materials.clear()
    eye_r.data.materials.clear()

    body.data.materials.append(clay_mat)
    eye_l.data.materials.append(eye_mat)
    eye_r.data.materials.append(eye_mat)

    # 3-Point Studio Lighting Rig focused on face at (0, -0.06, 1.53)
    target_pos = mathutils.Vector((0.0, -0.06, 1.53))

    # Rembrandt Key Light (45 deg right of camera, elevated)
    key_data = bpy.data.lights.new("KeyLight", type='AREA')
    key_data.energy = 85
    key_data.size = 0.6
    key_data.color = (1.0, 0.98, 0.95)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    key_obj.location = (0.65, -0.95, 1.95)
    scene.collection.objects.link(key_obj)

    # Cool Fill Light (soft bounce from left)
    fill_data = bpy.data.lights.new("FillLight", type='AREA')
    fill_data.energy = 28
    fill_data.size = 1.0
    fill_data.color = (0.85, 0.90, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    fill_obj.location = (-0.75, -0.85, 1.55)
    scene.collection.objects.link(fill_obj)

    # Rim / Kicker Light (separating skull and jaw)
    rim_data = bpy.data.lights.new("RimLight", type='AREA')
    rim_data.energy = 55
    rim_data.size = 0.5
    rim_data.color = (1.0, 1.0, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    rim_obj.location = (-0.45, 0.75, 2.05)
    scene.collection.objects.link(rim_obj)

    for light_obj in [key_obj, fill_obj, rim_obj]:
        dir = target_pos - light_obj.location
        light_obj.rotation_euler = dir.to_track_quat('-Z', 'Y').to_euler()

    # Camera (85mm portrait)
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = 85.0
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    return scene, body, eye_l, eye_r, cam_obj

def render_set(scene, cam_obj, prefix):
    target = (0.0, -0.06, 1.53)
    dist = 0.95

    def render_cam(loc, filename):
        cam_obj.location = loc
        direction = mathutils.Vector(target) - mathutils.Vector(loc)
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = filename
        bpy.ops.render.render(write_still=True)
        print(f"Rendered: {filename}")

    # 1. Front Head
    render_cam((0.0, -0.06 - dist, 1.53), f"production_v3/prototype/renders/{prefix}_head_front.png")

    # 2. Side Head (Left profile: looking from character's left side at +X)
    render_cam((dist, -0.06, 1.53), f"production_v3/prototype/renders/{prefix}_head_side.png")

    # 3. Three-Quarter Head
    rad34 = math.radians(35)
    x_34 = dist * math.sin(rad34)
    y_34 = -0.06 - dist * math.cos(rad34)
    render_cam((x_34, y_34, 1.55), f"production_v3/prototype/renders/{prefix}_head_threequarter.png")

def main():
    filepath = "production_v3/prototype/nyra_head_prototype.blend"
    scene, body, eye_l, eye_r, cam = setup_scene(filepath)
    
    # --- PASS 1: BASELINE (Set NYRA_Master_Prototype = 0.0) ---
    print("\n=== RENDERING BASELINE (CC0 ORIGINAL) ===")
    if body.data.shape_keys:
        for kb in body.data.shape_keys.key_blocks:
            kb.value = 0.0
    # Reset eyes to baseline
    eye_l.location = (0.0329, -0.1216, 1.5344)
    eye_r.location = (-0.0328, -0.1202, 1.5344)
    bpy.context.view_layer.update()
    render_set(scene, cam, "baseline_female")

    # --- PASS 2: NYRA PROTOTYPE (Set NYRA_Master_Prototype = 1.0) ---
    print("\n=== RENDERING NYRA FACIAL PROTOTYPE ===")
    if body.data.shape_keys:
        body.data.shape_keys.key_blocks["NYRA_Master_Prototype"].value = 1.0
    eye_l.location = (0.0329 + 0.0012, -0.1216 - 0.0012, 1.5344 + 0.0022)
    eye_r.location = (-0.0328 - 0.0012, -0.1202 - 0.0012, 1.5344 + 0.0022)
    bpy.context.view_layer.update()
    render_set(scene, cam, "nyra_prototype")

    print("\nAll renders complete.")

if __name__ == "__main__":
    main()
