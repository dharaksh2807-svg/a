import bpy
import math
import mathutils
import numpy as np

def build_and_render_phase2b():
    blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 1. Load CC0 Base Mesh
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        data_to.objects = [
            "GEO-body_female_realistic",
            "GEO-body_female_realistic.eye.L",
            "GEO-body_female_realistic.eye.R"
        ]

    body = data_to.objects[0]
    eye_l = data_to.objects[1]
    eye_r = data_to.objects[2]

    for o in [body, eye_l, eye_r]:
        bpy.context.scene.collection.objects.link(o)

    # Center body at origin
    body.location = (0, 0, 0)
    body.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()

    me = body.data

    # Ensure shape keys exist
    if not body.data.shape_keys:
        body.shape_key_add(name="Basis")
    
    coords = np.array([v.co for v in me.vertices], dtype=np.float32)
    n_verts = len(coords)

    def gfalloff(p, center, radius, power=2.0):
        dist_sq = (p.x - center[0])**2 + (p.y - center[1])**2 + (p.z - center[2])**2
        r_sq = radius**2
        if dist_sq >= r_sq:
            return 0.0
        norm_dist = dist_sq / r_sq
        return math.exp(-2.0 * norm_dist) * (1.0 - norm_dist)**power

    # --- Controlled Visual Likeness Sculpt Deformation ---
    # Calibrated to match NYRA's facial planes in nyra_portrait_face.jpg
    def deform_nyra_likeness(p):
        dx, dy, dz = 0.0, 0.0, 0.0

        # 1. JAWLINE & CHIN:
        # Slim lower cheek/jaw, taper towards chin
        for sign in [-1.0, 1.0]:
            w_jaw_slim = gfalloff(p, (sign * 0.052, -0.075, 1.442), 0.045)
            if w_jaw_slim > 0:
                dx -= sign * 0.0055 * w_jaw_slim  # Slim lower jaw
                dy += 0.0025 * w_jaw_slim

            w_angle = gfalloff(p, (sign * 0.055, -0.048, 1.432), 0.035)
            if w_angle > 0:
                dx += sign * 0.0035 * w_angle
                dy -= 0.0020 * w_angle
                dz += 0.0020 * w_angle

        # Chin apex: refined, delicate, projected forward and slightly elevated
        w_chin = gfalloff(p, (0.0, -0.115, 1.420), 0.040)
        if w_chin > 0:
            dy -= 0.0065 * w_chin
            dz += 0.0040 * w_chin
            dx -= math.copysign(0.0045 * abs(p.x) / 0.02, p.x) * w_chin

        # 2. CHEEKBONES (ZYGOMATIC ARCH):
        # Prominent sculpted cheekbones
        for sign in [-1.0, 1.0]:
            w_cheek = gfalloff(p, (sign * 0.062, -0.076, 1.518), 0.048)
            if w_cheek > 0:
                dx += sign * 0.0075 * w_cheek
                dy -= 0.0055 * w_cheek
                dz += 0.0045 * w_cheek

            w_submalar = gfalloff(p, (sign * 0.048, -0.068, 1.472), 0.032)
            if w_submalar > 0:
                dx -= sign * 0.0035 * w_submalar
                dy += 0.0020 * w_submalar

        # 3. EYES & ORBITS (Almond Shape, Positive Canthal Tilt):
        for sign in [-1.0, 1.0]:
            # Lateral canthus: positive canthal tilt sweep
            w_lat = gfalloff(p, (sign * 0.052, -0.096, 1.536), 0.028)
            if w_lat > 0:
                dz += 0.0065 * w_lat
                dx += sign * 0.0045 * w_lat
                dy -= 0.0025 * w_lat

            # Upper eyelid apex
            w_upper_lid = gfalloff(p, (sign * 0.034, -0.110, 1.545), 0.026)
            if w_upper_lid > 0:
                dz += 0.0055 * w_upper_lid
                dy += 0.0035 * w_upper_lid

            # Lower eyelid contour
            w_lower_lid = gfalloff(p, (sign * 0.034, -0.112, 1.524), 0.022)
            if w_lower_lid > 0:
                dz -= 0.0020 * w_lower_lid
                dy += 0.0015 * w_lower_lid

            # Supratarsal fold
            w_crease = gfalloff(p, (sign * 0.036, -0.106, 1.554), 0.024)
            if w_crease > 0:
                dy += 0.0032 * w_crease
                dz += 0.0022 * w_crease

            # Medial canthus
            w_med = gfalloff(p, (sign * 0.016, -0.125, 1.531), 0.018)
            if w_med > 0:
                dz -= 0.0015 * w_med
                dx -= sign * 0.0012 * w_med

        # 4. NOSE (Refined bridge and tip):
        w_tip = gfalloff(p, (0.0, -0.1674, 1.5024), 0.028)
        if w_tip > 0:
            dy -= 0.0045 * w_tip
            dz += 0.0050 * w_tip
            dx -= math.copysign(0.0035 * abs(p.x) / 0.012, p.x) * w_tip

        for sign in [-1.0, 1.0]:
            w_ala = gfalloff(p, (sign * 0.017, -0.150, 1.488), 0.024)
            if w_ala > 0:
                dx -= sign * 0.0042 * w_ala
                dz += 0.0020 * w_ala

        w_bridge = gfalloff(p, (0.0, -0.145, 1.522), 0.030)
        if w_bridge > 0:
            dx -= math.copysign(0.0028 * abs(p.x) / 0.010, p.x) * w_bridge

        # 5. LIPS & PHILTRUM:
        for sign in [-1.0, 1.0]:
            w_peak = gfalloff(p, (sign * 0.0075, -0.154, 1.465), 0.018)
            if w_peak > 0:
                dz += 0.0042 * w_peak
                dy -= 0.0038 * w_peak
                dx += sign * 0.0015 * w_peak

        w_phil = gfalloff(p, (0.0, -0.150, 1.474), 0.015)
        if w_phil > 0:
            dy += 0.0030 * w_phil

        w_low = gfalloff(p, (0.0, -0.153, 1.444), 0.026)
        if w_low > 0:
            dy -= 0.0058 * w_low
            dz -= 0.0020 * w_low
            w_cleft = gfalloff(p, (0.0, -0.153, 1.442), 0.010)
            dy += 0.0022 * w_cleft

        for sign in [-1.0, 1.0]:
            w_corner = gfalloff(p, (sign * 0.025, -0.138, 1.455), 0.020)
            if w_corner > 0:
                dz += 0.0030 * w_corner
                dy += 0.0015 * w_corner

        if dx != 0 or dy != 0 or dz != 0:
            return (dx, dy, dz)
        return None

    sk = body.shape_key_add(name="NYRA_Phase2B_Likeness")
    new_coords = coords.copy()
    for i in range(n_verts):
        p = mathutils.Vector(coords[i])
        if p.z > 1.30 and p.y < 0.08:
            offset = deform_nyra_likeness(p)
            if offset:
                new_coords[i] += np.array(offset, dtype=np.float32)
    sk.data.foreach_set("co", new_coords.ravel())
    sk.value = 1.0

    if body.data.shape_keys:
        for k in body.data.shape_keys.key_blocks:
            if k.name != "NYRA_Phase2B_Likeness" and k.name != "Basis":
                k.value = 0.0

    # 2. EYEBALL PLACEMENT (Calibrated relative to head origin)
    eye_l.parent = None
    eye_r.parent = None
    eye_l.location = (0.0335, -0.1235, 1.5365)
    eye_r.location = (-0.0335, -0.1235, 1.5365)
    eye_l.rotation_euler = (0, 0, 0)
    eye_r.rotation_euler = (0, 0, 0)

    # 3. MATERIALS SETUP
    body.data.materials.clear()
    eye_l.data.materials.clear()
    eye_r.data.materials.clear()

    # A) Calibrated Skin Material
    skin_mat = bpy.data.materials.new("M_NYRA_Skin_Proxy")
    skin_mat.use_nodes = True
    s_nodes = skin_mat.node_tree.nodes
    skin_bsdf = s_nodes.get("Principled BSDF")
    skin_bsdf.inputs['Base Color'].default_value = (0.76, 0.52, 0.40, 1.0) # Warm golden-olive
    skin_bsdf.inputs['Subsurface Weight'].default_value = 0.08            # Subtle soft scatter
    skin_bsdf.inputs['Subsurface Radius'].default_value = (0.0025, 0.0015, 0.0008) # 2.5mm scatter
    skin_bsdf.inputs['Roughness'].default_value = 0.48
    skin_bsdf.inputs['Specular IOR Level'].default_value = 0.45

    # B) Accurate Lip Material
    lip_mat = bpy.data.materials.new("M_NYRA_Lips_Proxy")
    lip_mat.use_nodes = True
    lip_bsdf = lip_mat.node_tree.nodes.get("Principled BSDF")
    lip_bsdf.inputs['Base Color'].default_value = (0.68, 0.28, 0.32, 1.0) # Natural rose mauve
    lip_bsdf.inputs['Subsurface Weight'].default_value = 0.12
    lip_bsdf.inputs['Subsurface Radius'].default_value = (0.0030, 0.0015, 0.0010)
    lip_bsdf.inputs['Roughness'].default_value = 0.28 # Satin gloss
    lip_bsdf.inputs['Specular IOR Level'].default_value = 0.60

    # C) Dark Espresso Hair Material (for scalp and hair curves)
    hair_dark_mat = bpy.data.materials.new("M_NYRA_Hair_Dark")
    hair_dark_mat.use_nodes = True
    hd_bsdf = hair_dark_mat.node_tree.nodes.get("Principled BSDF")
    hd_bsdf.inputs['Base Color'].default_value = (0.07, 0.05, 0.04, 1.0) # Espresso dark brown
    hd_bsdf.inputs['Roughness'].default_value = 0.38
    hd_bsdf.inputs['Specular IOR Level'].default_value = 0.65

    # Assign material slots to body
    body.data.materials.append(skin_mat)      # Slot 0: Skin
    body.data.materials.append(lip_mat)       # Slot 1: Lips
    body.data.materials.append(hair_dark_mat)  # Slot 2: Scalp Hair

    # Assign polygons:
    # - Scalp: Z > 1.555 and Y > -0.065
    # - Lips: vermilion border (1.438 < z < 1.467, y < -0.145, |x| < 0.024)
    for p in me.polygons:
        p_verts = [me.vertices[i] for i in p.vertices]
        if all(1.438 < v.co.z < 1.467 and v.co.y < -0.145 and abs(v.co.x) < 0.024 for v in p_verts):
            p.material_index = 1 # Lips
        elif all(v.co.z > 1.555 and v.co.y > -0.065 for v in p_verts):
            p.material_index = 2 # Scalp hair cap
        else:
            p.material_index = 0 # Skin

    # D) Calibrated Concentric Hazel Eye Material
    eye_mat = bpy.data.materials.new("M_NYRA_Eye_Hazel")
    eye_mat.use_nodes = True
    e_nodes = eye_mat.node_tree.nodes
    e_links = eye_mat.node_tree.links
    e_nodes.clear()

    out_node = e_nodes.new('ShaderNodeOutputMaterial')
    bsdf_node = e_nodes.new('ShaderNodeBsdfPrincipled')
    texcoord = e_nodes.new('ShaderNodeTexCoord')
    mapping = e_nodes.new('ShaderNodeMapping')
    
    # Calculate radius r = sqrt(x^2 + z^2) in local space
    sep_xyz = e_nodes.new('ShaderNodeSeparateXYZ')
    math_x2 = e_nodes.new('ShaderNodeMath')
    math_x2.operation = 'POWER'
    math_x2.inputs[1].default_value = 2.0
    
    math_z2 = e_nodes.new('ShaderNodeMath')
    math_z2.operation = 'POWER'
    math_z2.inputs[1].default_value = 2.0

    math_sum = e_nodes.new('ShaderNodeMath')
    math_sum.operation = 'ADD'

    math_r = e_nodes.new('ShaderNodeMath')
    math_r.operation = 'SQRT'

    # Normalize radius by dividing by iris outer radius (~0.0062m)
    math_norm = e_nodes.new('ShaderNodeMath')
    math_norm.operation = 'DIVIDE'
    math_norm.inputs[1].default_value = 0.0062 # Iris outer edge = 1.0

    color_ramp = e_nodes.new('ShaderNodeValToRGB')
    elements = color_ramp.color_ramp.elements
    # 0.0 - 0.35: Pupil (Deep black)
    elements[0].position = 0.0
    elements[0].color = (0.008, 0.008, 0.008, 1.0)
    
    el1 = elements.new(0.36)
    el1.color = (0.008, 0.008, 0.008, 1.0) # Sharp pupil edge
    
    el2 = elements.new(0.42)
    el2.color = (0.60, 0.36, 0.10, 1.0) # Warm golden amber iris
    
    el3 = elements.new(0.75)
    el3.color = (0.42, 0.28, 0.08, 1.0) # Hazel ring
    
    el4 = elements.new(0.92)
    el4.color = (0.08, 0.05, 0.03, 1.0) # Dark espresso limbal ring
    
    elements[1].position = 1.02
    elements[1].color = (0.92, 0.92, 0.94, 1.0) # Sclera

    e_links.new(texcoord.outputs['Object'], sep_xyz.inputs['Vector'])
    e_links.new(sep_xyz.outputs['X'], math_x2.inputs[0])
    e_links.new(sep_xyz.outputs['Z'], math_z2.inputs[0])
    e_links.new(math_x2.outputs['Value'], math_sum.inputs[0])
    e_links.new(math_z2.outputs['Value'], math_sum.inputs[1])
    e_links.new(math_sum.outputs['Value'], math_r.inputs[0])
    e_links.new(math_r.outputs['Value'], math_norm.inputs[0])
    e_links.new(math_norm.outputs['Value'], color_ramp.inputs['Fac'])
    e_links.new(color_ramp.outputs['Color'], bsdf_node.inputs['Base Color'])

    bsdf_node.inputs['Roughness'].default_value = 0.03 # Wet cornea mirror gloss
    bsdf_node.inputs['Specular IOR Level'].default_value = 0.85
    e_links.new(bsdf_node.outputs['BSDF'], out_node.inputs['Surface'])

    eye_l.data.materials.append(eye_mat)
    eye_r.data.materials.append(eye_mat)

    # 4. EYEBROWS (Accurately positioned on skin surface)
    brow_mat = bpy.data.materials.new("M_NYRA_Brows_Proxy")
    brow_mat.use_nodes = True
    b_bsdf = brow_mat.node_tree.nodes.get("Principled BSDF")
    b_bsdf.inputs['Base Color'].default_value = (0.08, 0.06, 0.04, 1.0) # Espresso dark
    b_bsdf.inputs['Roughness'].default_value = 0.60

    def create_eyebrow(name, sign):
        c_data = bpy.data.curves.new(name, type='CURVE')
        c_data.dimensions = '3D'
        c_data.bevel_depth = 0.0025
        c_data.bevel_resolution = 3
        c_data.fill_mode = 'FULL'
        
        spline = c_data.splines.new('BEZIER')
        spline.bezier_points.add(2)
        
        pts = [
            (sign * 0.015, -0.143, 1.558), # Brow head
            (sign * 0.034, -0.136, 1.572), # Arch apex
            (sign * 0.052, -0.128, 1.554)  # Brow tail
        ]
        radii = [0.9, 1.2, 0.3]
        for i, (p, r) in enumerate(zip(pts, radii)):
            bp = spline.bezier_points[i]
            bp.co = p
            bp.radius = r
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
            
        obj = bpy.data.objects.new(name, c_data)
        obj.data.materials.append(brow_mat)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    create_eyebrow("GEO-NYRA_Eyebrow.L", 1.0)
    create_eyebrow("GEO-NYRA_Eyebrow.R", -1.0)

    # 5. EYELASHES & WINGED EYELINER (Accurately positioned on upper lid lash line)
    lash_mat = bpy.data.materials.new("M_NYRA_Lashes_Proxy")
    lash_mat.use_nodes = True
    l_bsdf = lash_mat.node_tree.nodes.get("Principled BSDF")
    l_bsdf.inputs['Base Color'].default_value = (0.015, 0.015, 0.015, 1.0)
    l_bsdf.inputs['Roughness'].default_value = 0.35

    def create_eyelash(name, sign):
        c_data = bpy.data.curves.new(name, type='CURVE')
        c_data.dimensions = '3D'
        c_data.bevel_depth = 0.0016
        c_data.bevel_resolution = 3
        c_data.fill_mode = 'FULL'
        
        spline = c_data.splines.new('BEZIER')
        spline.bezier_points.add(3)
        
        pts = [
            (sign * 0.015, -0.136, 1.539), # Medial canthus
            (sign * 0.034, -0.137, 1.550), # Mid upper lid
            (sign * 0.046, -0.131, 1.540), # Lateral canthus
            (sign * 0.054, -0.126, 1.544)  # Winged cat-eye flick
        ]
        radii = [0.5, 1.2, 1.3, 0.2]
        for i, (p, r) in enumerate(zip(pts, radii)):
            bp = spline.bezier_points[i]
            bp.co = p
            bp.radius = r
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
            
        obj = bpy.data.objects.new(name, c_data)
        obj.data.materials.append(lash_mat)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    create_eyelash("GEO-NYRA_Eyelash.L", 1.0)
    create_eyelash("GEO-NYRA_Eyelash.R", -1.0)

    # 6. HAIR PROXY (High Ponytail + Face-framing Fringe + Signature Purple Accent)
    hair_purple_mat = bpy.data.materials.new("M_NYRA_Hair_PurpleAccent")
    hair_purple_mat.use_nodes = True
    hp_bsdf = hair_purple_mat.node_tree.nodes.get("Principled BSDF")
    hp_bsdf.inputs['Base Color'].default_value = (0.58, 0.08, 0.88, 1.0) # Saturated electric violet
    hp_bsdf.inputs['Roughness'].default_value = 0.35
    hp_bsdf.inputs['Specular IOR Level'].default_value = 0.70

    tie_mat = bpy.data.materials.new("M_NYRA_HairTie_Violet")
    tie_mat.use_nodes = True
    ht_bsdf = tie_mat.node_tree.nodes.get("Principled BSDF")
    ht_bsdf.inputs['Base Color'].default_value = (0.42, 0.06, 0.75, 1.0)
    ht_bsdf.inputs['Roughness'].default_value = 0.50

    # A) Hair Tie Ring at crown
    tie_curve = bpy.data.curves.new("GEO-HairTie", type='CURVE')
    tie_curve.dimensions = '3D'
    tie_curve.bevel_depth = 0.007
    tie_curve.bevel_resolution = 4
    tie_curve.fill_mode = 'FULL'
    tie_spline = tie_curve.splines.new('BEZIER')
    tie_spline.bezier_points.add(3)
    tie_spline.use_cyclic_u = True
    tie_center = (0.0, 0.025, 1.635)
    r_tie = 0.026
    for i in range(4):
        ang = i * (math.pi / 2.0)
        bp = tie_spline.bezier_points[i]
        bp.co = (tie_center[0] + r_tie * math.cos(ang), tie_center[1] + r_tie * math.sin(ang) * 0.75, tie_center[2] + (i%2)*0.003)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    tie_obj = bpy.data.objects.new("GEO-NYRA_HairTie", tie_curve)
    tie_obj.data.materials.append(tie_mat)
    bpy.context.scene.collection.objects.link(tie_obj)

    def create_hair_strand(name, pts, radii, mat, bevel=0.014):
        c_data = bpy.data.curves.new(name, type='CURVE')
        c_data.dimensions = '3D'
        c_data.bevel_depth = bevel
        c_data.bevel_resolution = 4
        c_data.fill_mode = 'FULL'
        spline = c_data.splines.new('BEZIER')
        spline.bezier_points.add(len(pts) - 1)
        for i, (p, r) in enumerate(zip(pts, radii)):
            bp = spline.bezier_points[i]
            bp.co = p
            bp.radius = r
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
        obj = bpy.data.objects.new(name, c_data)
        obj.data.materials.append(mat)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    # Ponytail center plume
    create_hair_strand("GEO-NYRA_Pony_Center", [
        (0.0, 0.025, 1.640),
        (0.0, 0.055, 1.705),
        (-0.015, 0.115, 1.635),
        (-0.025, 0.145, 1.515),
        (-0.010, 0.155, 1.385)
    ], [1.0, 1.8, 2.0, 1.5, 0.5], hair_dark_mat, bevel=0.018)

    # Lateral dark wings
    create_hair_strand("GEO-NYRA_Pony_LeftDark", [
        (0.022, 0.025, 1.640),
        (0.040, 0.065, 1.695),
        (0.050, 0.110, 1.615),
        (0.040, 0.135, 1.490),
        (0.025, 0.140, 1.375)
    ], [0.8, 1.4, 1.6, 1.2, 0.3], hair_dark_mat, bevel=0.014)

    create_hair_strand("GEO-NYRA_Pony_RightDark", [
        (-0.022, 0.025, 1.640),
        (-0.040, 0.065, 1.695),
        (-0.050, 0.110, 1.615),
        (-0.040, 0.135, 1.490),
        (-0.025, 0.140, 1.375)
    ], [0.8, 1.4, 1.6, 1.2, 0.3], hair_dark_mat, bevel=0.014)

    # VIBRANT PURPLE STREAK (Character's left side / viewer right)
    create_hair_strand("GEO-NYRA_Pony_PurpleStreak", [
        (0.032, 0.032, 1.650),
        (0.055, 0.075, 1.710),
        (0.072, 0.120, 1.625),
        (0.075, 0.145, 1.505),
        (0.058, 0.150, 1.390)
    ], [0.7, 1.3, 1.4, 1.0, 0.25], hair_purple_mat, bevel=0.012)

    # Face-framing curtain fringe tendrils (sweeping down from forehead past cheeks)
    # Left fringe
    create_hair_strand("GEO-NYRA_Fringe_Left", [
        (0.012, -0.138, 1.585), # Hairline parting
        (0.028, -0.142, 1.545), # Temple
        (0.045, -0.130, 1.485), # Sweep past cheekbone
        (0.042, -0.112, 1.435), # Jawline curve
        (0.035, -0.095, 1.390)  # Neck tip
    ], [0.8, 1.2, 1.1, 0.8, 0.2], hair_dark_mat, bevel=0.006)

    # Right fringe
    create_hair_strand("GEO-NYRA_Fringe_Right", [
        (-0.012, -0.138, 1.585),
        (-0.028, -0.142, 1.545),
        (-0.045, -0.130, 1.485),
        (-0.042, -0.112, 1.435),
        (-0.035, -0.095, 1.390)
    ], [0.8, 1.2, 1.1, 0.8, 0.2], hair_dark_mat, bevel=0.006)

    # 7. SILVER HOOP EARRINGS
    silver_mat = bpy.data.materials.new("M_NYRA_Silver")
    silver_mat.use_nodes = True
    s_bsdf = silver_mat.node_tree.nodes.get("Principled BSDF")
    s_bsdf.inputs['Base Color'].default_value = (0.92, 0.93, 0.95, 1.0)
    s_bsdf.inputs['Metallic'].default_value = 0.98
    s_bsdf.inputs['Roughness'].default_value = 0.15

    def create_hoop_earring(name, sign):
        c_data = bpy.data.curves.new(name, type='CURVE')
        c_data.dimensions = '3D'
        c_data.bevel_depth = 0.0022
        c_data.bevel_resolution = 4
        c_data.fill_mode = 'FULL'
        spline = c_data.splines.new('BEZIER')
        spline.bezier_points.add(3)
        spline.use_cyclic_u = True
        center = (sign * 0.076, -0.012, 1.482)
        r_ear = 0.017
        for i in range(4):
            ang = i * (math.pi / 2.0)
            bp = spline.bezier_points[i]
            bp.co = (center[0], center[1] + r_ear * math.cos(ang), center[2] + r_ear * math.sin(ang))
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
        obj = bpy.data.objects.new(name, c_data)
        obj.data.materials.append(silver_mat)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    create_hoop_earring("GEO-NYRA_Earring.L", 1.0)
    create_hoop_earring("GEO-NYRA_Earring.R", -1.0)

    # 8. TOP STRAPS
    strap_mat = bpy.data.materials.new("M_NYRA_TopStraps")
    strap_mat.use_nodes = True
    st_bsdf = strap_mat.node_tree.nodes.get("Principled BSDF")
    st_bsdf.inputs['Base Color'].default_value = (0.10, 0.09, 0.11, 1.0)
    st_bsdf.inputs['Roughness'].default_value = 0.70

    def create_strap(name, sign):
        c_data = bpy.data.curves.new(name, type='CURVE')
        c_data.dimensions = '3D'
        c_data.bevel_depth = 0.006
        c_data.bevel_resolution = 3
        c_data.fill_mode = 'FULL'
        spline = c_data.splines.new('BEZIER')
        spline.bezier_points.add(2)
        pts = [
            (sign * 0.072, -0.015, 1.395),
            (sign * 0.065, -0.065, 1.340),
            (sign * 0.045, -0.115, 1.280)
        ]
        for i, p in enumerate(pts):
            bp = spline.bezier_points[i]
            bp.co = p
            bp.radius = 1.0
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
        obj = bpy.data.objects.new(name, c_data)
        obj.data.materials.append(strap_mat)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    create_strap("GEO-NYRA_Strap.L", 1.0)
    create_strap("GEO-NYRA_Strap.R", -1.0)

    # Save editable prototype master file
    save_path = "production_v3/prototype/nyra_head_prototype_v2.blend"
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"Saved editable Phase 2B prototype blend to: {save_path}")

    # 9. RENDER SETUP
    scene = bpy.context.scene
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

    # Studio neutral dark-gray environment to prevent ambient washing out
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.02, 0.02, 0.02, 1.0)
        bg_node.inputs['Strength'].default_value = 0.05

    # Clean Neutral Backdrop Plane (placed 1.4m behind the character)
    backdrop_data = bpy.data.meshes.new("BackdropMesh")
    backdrop_obj = bpy.data.objects.new("Backdrop", backdrop_data)
    # 4 vertices plane
    verts = [(-2.5, 1.4, 0.5), (2.5, 1.4, 0.5), (2.5, 1.4, 2.5), (-2.5, 1.4, 2.5)]
    faces = [(0, 1, 2, 3)]
    backdrop_data.from_pydata(verts, [], faces)
    backdrop_mat = bpy.data.materials.new("M_Backdrop")
    backdrop_mat.use_nodes = True
    bd_bsdf = backdrop_mat.node_tree.nodes.get("Principled BSDF")
    bd_bsdf.inputs['Base Color'].default_value = (0.84, 0.84, 0.86, 1.0) # Matches reference neutral light gray
    bd_bsdf.inputs['Roughness'].default_value = 0.90
    backdrop_obj.data.materials.append(backdrop_mat)
    scene.collection.objects.link(backdrop_obj)

    # Backdrop Light
    bd_light_data = bpy.data.lights.new("BackdropLight", type='AREA')
    bd_light_data.energy = 140
    bd_light_data.size = 2.0
    bd_light_data.color = (0.95, 0.96, 1.0)
    bd_light_obj = bpy.data.objects.new("BackdropLight", bd_light_data)
    bd_light_obj.location = (0.0, 0.2, 1.6)
    bd_light_obj.rotation_euler = (math.radians(-90), 0, 0)
    scene.collection.objects.link(bd_light_obj)

    # 3-Point Portrait Subject Lighting Rig focused on head at (0, -0.05, 1.51)
    target_pos = mathutils.Vector((0.0, -0.05, 1.51))

    # Key light: Soft portrait key (front-left, slightly elevated)
    key_data = bpy.data.lights.new("KeyLight", type='AREA')
    key_data.energy = 55
    key_data.size = 0.7
    key_data.color = (1.0, 0.97, 0.94)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    key_obj.location = (-0.50, -1.20, 1.80)
    scene.collection.objects.link(key_obj)

    # Fill light: Gentle soft fill (front-right)
    fill_data = bpy.data.lights.new("FillLight", type='AREA')
    fill_data.energy = 25
    fill_data.size = 0.9
    fill_data.color = (0.92, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    fill_obj.location = (0.60, -1.10, 1.55)
    scene.collection.objects.link(fill_obj)

    # Rim / Hair light: Highlights ponytail, silhouette, and purple hair streak
    rim_data = bpy.data.lights.new("RimLight", type='AREA')
    rim_data.energy = 60
    rim_data.size = 0.5
    rim_data.color = (1.0, 0.98, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    rim_obj.location = (0.35, 0.70, 1.95)
    scene.collection.objects.link(rim_obj)

    for light_obj in [key_obj, fill_obj, rim_obj]:
        direction = target_pos - light_obj.location
        light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

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
    build_and_render_phase2b()
