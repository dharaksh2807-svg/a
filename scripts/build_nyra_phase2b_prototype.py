import bpy
import math
import mathutils
import numpy as np

def build_nyra_phase2b_prototype():
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
    # Directly tuned to match NYRA's facial planes in nyra_portrait_face.jpg
    def deform_nyra_likeness(p):
        dx, dy, dz = 0.0, 0.0, 0.0

        # 1. JAWLINE & CHIN:
        # In NYRA, the face is sleek and tapered, not square/puffy.
        # We slim the masseter/lower cheek area and define the elegant pointed chin.
        for sign in [-1.0, 1.0]:
            # Lower cheek & jaw slim
            w_jaw_slim = gfalloff(p, (sign * 0.052, -0.075, 1.442), 0.045)
            if w_jaw_slim > 0:
                dx -= sign * 0.0055 * w_jaw_slim  # Slim lower jaw by 5.5mm
                dy += 0.0025 * w_jaw_slim

            # Defined mandibular angle under ear
            w_angle = gfalloff(p, (sign * 0.055, -0.048, 1.432), 0.035)
            if w_angle > 0:
                dx += sign * 0.0035 * w_angle
                dy -= 0.0020 * w_angle
                dz += 0.0020 * w_angle

        # Chin apex: refined, delicate, slightly pointed and elevated
        w_chin = gfalloff(p, (0.0, -0.115, 1.420), 0.040)
        if w_chin > 0:
            dy -= 0.0065 * w_chin                # Project chin forward 6.5mm
            dz += 0.0040 * w_chin                # Elevate chin 4mm
            # Taper lateral chin
            dx -= math.copysign(0.0045 * abs(p.x) / 0.02, p.x) * w_chin

        # 2. CHEEKBONES (ZYGOMATIC ARCH):
        # High, prominent sculpted cheekbones framing the face
        for sign in [-1.0, 1.0]:
            w_cheek = gfalloff(p, (sign * 0.062, -0.076, 1.518), 0.048)
            if w_cheek > 0:
                dx += sign * 0.0075 * w_cheek    # Lateral cheekbone projection
                dy -= 0.0055 * w_cheek           # Anterior projection
                dz += 0.0045 * w_cheek           # High elevation

            # Submalar contour below cheekbone
            w_submalar = gfalloff(p, (sign * 0.048, -0.068, 1.472), 0.032)
            if w_submalar > 0:
                dx -= sign * 0.0035 * w_submalar # Athletic hollow
                dy += 0.0020 * w_submalar

        # 3. EYES & ORBITS (Almond Shape, Positive Canthal Tilt, Open Aperture):
        for sign in [-1.0, 1.0]:
            # Lateral canthus (outer corner): strong positive canthal tilt sweep
            w_lat = gfalloff(p, (sign * 0.052, -0.096, 1.536), 0.028)
            if w_lat > 0:
                dz += 0.0065 * w_lat             # Lift outer corner by 6.5mm
                dx += sign * 0.0045 * w_lat      # Widen almond aperture
                dy -= 0.0025 * w_lat

            # Upper eyelid apex: significantly open the aperture so the eye is large and expressive!
            w_upper_lid = gfalloff(p, (sign * 0.034, -0.110, 1.545), 0.026)
            if w_upper_lid > 0:
                dz += 0.0055 * w_upper_lid       # Open upper lid by 5.5mm
                dy += 0.0035 * w_upper_lid

            # Lower eyelid contour: smooth almond cradle
            w_lower_lid = gfalloff(p, (sign * 0.034, -0.112, 1.524), 0.022)
            if w_lower_lid > 0:
                dz -= 0.0020 * w_lower_lid       # Slightly open lower lid
                dy += 0.0015 * w_lower_lid

            # Supratarsal fold (double eyelid crease)
            w_crease = gfalloff(p, (sign * 0.036, -0.106, 1.554), 0.024)
            if w_crease > 0:
                dy += 0.0032 * w_crease          # Deepen crease
                dz += 0.0022 * w_crease

            # Medial canthus (tear duct): anchor
            w_med = gfalloff(p, (sign * 0.016, -0.125, 1.531), 0.018)
            if w_med > 0:
                dz -= 0.0015 * w_med
                dx -= sign * 0.0012 * w_med

        # 4. NOSE (Narrow bridge, refined upturned tip, narrow alar base):
        # Nasal tip:
        w_tip = gfalloff(p, (0.0, -0.1674, 1.5024), 0.028)
        if w_tip > 0:
            dy -= 0.0045 * w_tip                 # Forward tip projection
            dz += 0.0050 * w_tip                 # Upward tip tilt (supratip break)
            dx -= math.copysign(0.0035 * abs(p.x) / 0.012, p.x) * w_tip # Slim tip width

        # Alar wings (nostrils):
        for sign in [-1.0, 1.0]:
            w_ala = gfalloff(p, (sign * 0.017, -0.150, 1.488), 0.024)
            if w_ala > 0:
                dx -= sign * 0.0042 * w_ala      # Narrow alar base by 4.2mm
                dz += 0.0020 * w_ala

        # Nasal bridge (dorsum):
        w_bridge = gfalloff(p, (0.0, -0.145, 1.522), 0.030)
        if w_bridge > 0:
            dx -= math.copysign(0.0028 * abs(p.x) / 0.010, p.x) * w_bridge # Slim bridge

        # 5. LIPS & PHILTRUM:
        # Upper lip Cupid's bow peaks:
        for sign in [-1.0, 1.0]:
            w_peak = gfalloff(p, (sign * 0.0075, -0.154, 1.465), 0.018)
            if w_peak > 0:
                dz += 0.0042 * w_peak            # Sharp Cupid peaks
                dy -= 0.0038 * w_peak            # Forward projection
                dx += sign * 0.0015 * w_peak

        # Philtrum groove depression:
        w_phil = gfalloff(p, (0.0, -0.150, 1.474), 0.015)
        if w_phil > 0:
            dy += 0.0030 * w_phil                # Deepen groove

        # Lower lip fullness & cushion:
        w_low = gfalloff(p, (0.0, -0.153, 1.444), 0.026)
        if w_low > 0:
            dy -= 0.0058 * w_low                 # Plump lower lip forward 5.8mm
            dz -= 0.0020 * w_low
            # Bilobed cleft
            w_cleft = gfalloff(p, (0.0, -0.153, 1.442), 0.010)
            dy += 0.0022 * w_cleft

        # Commissures (corners of mouth): relaxed, self-possessed micro-lift
        for sign in [-1.0, 1.0]:
            w_corner = gfalloff(p, (sign * 0.025, -0.138, 1.455), 0.020)
            if w_corner > 0:
                dz += 0.0030 * w_corner          # Micro-lift
                dy += 0.0015 * w_corner

        if dx != 0 or dy != 0 or dz != 0:
            return (dx, dy, dz)
        return None

    # Apply likeness shape key
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

    # Ensure other shape keys are disabled
    if body.data.shape_keys:
        for k in body.data.shape_keys.key_blocks:
            if k.name != "NYRA_Phase2B_Likeness" and k.name != "Basis":
                k.value = 0.0

    # Eyeballs follow the almond orbit
    eye_l.location.x += 0.0018
    eye_l.location.z += 0.0030
    eye_l.location.y -= 0.0015

    eye_r.location.x -= 0.0018
    eye_r.location.z += 0.0030
    eye_r.location.y -= 0.0015

    # 2. Materials Setup
    body.data.materials.clear()
    eye_l.data.materials.clear()
    eye_r.data.materials.clear()

    # --- Skin Material ---
    skin_mat = bpy.data.materials.new("M_NYRA_Skin_Proxy")
    skin_mat.use_nodes = True
    skin_nodes = skin_mat.node_tree.nodes
    skin_links = skin_mat.node_tree.links
    skin_bsdf = skin_nodes.get("Principled BSDF")
    
    # Warm golden-olive skin with realistic subsurface scattering
    skin_bsdf.inputs['Base Color'].default_value = (0.83, 0.58, 0.46, 1.0)
    skin_bsdf.inputs['Subsurface Weight'].default_value = 0.22
    skin_bsdf.inputs['Subsurface Radius'].default_value = (0.45, 0.25, 0.15)
    skin_bsdf.inputs['Roughness'].default_value = 0.44
    skin_bsdf.inputs['Specular IOR Level'].default_value = 0.5

    # --- Lip Material ---
    lip_mat = bpy.data.materials.new("M_NYRA_Lips_Proxy")
    lip_mat.use_nodes = True
    lip_nodes = lip_mat.node_tree.nodes
    lip_bsdf = lip_nodes.get("Principled BSDF")
    lip_bsdf.inputs['Base Color'].default_value = (0.72, 0.32, 0.36, 1.0) # Rose mauve lip tone
    lip_bsdf.inputs['Subsurface Weight'].default_value = 0.35
    lip_bsdf.inputs['Subsurface Radius'].default_value = (0.50, 0.20, 0.20)
    lip_bsdf.inputs['Roughness'].default_value = 0.24 # Soft satin gloss
    lip_bsdf.inputs['Specular IOR Level'].default_value = 0.65

    # Assign materials to body slots
    body.data.materials.append(skin_mat) # Slot 0: Skin
    body.data.materials.append(lip_mat)  # Slot 1: Lips

    # Assign lip material to detected lip polygons
    for p in me.polygons:
        p_verts = [me.vertices[i] for i in p.vertices]
        if all(1.428 < v.co.z < 1.478 and v.co.y < -0.138 and abs(v.co.x) < 0.032 for v in p_verts):
            p.material_index = 1
        else:
            p.material_index = 0

    # --- Eye Material (Iris + Pupil + Cornea Wetness) ---
    eye_mat = bpy.data.materials.new("M_NYRA_Eye_Hazel")
    eye_mat.use_nodes = True
    e_nodes = eye_mat.node_tree.nodes
    e_links = eye_mat.node_tree.links
    e_nodes.clear()

    out_node = e_nodes.new('ShaderNodeOutputMaterial')
    bsdf_node = e_nodes.new('ShaderNodeBsdfPrincipled')
    geom_node = e_nodes.new('ShaderNodeNewGeometry')
    texcoord = e_nodes.new('ShaderNodeTexCoord')
    mapping = e_nodes.new('ShaderNodeMapping')
    gradient = e_nodes.new('ShaderNodeTexGradient')
    gradient.gradient_type = 'SPHERICAL'
    color_ramp = e_nodes.new('ShaderNodeValToRGB')

    # Eye Color Ramp:
    # 0.0 - 0.22: Pupil (Obsidian Black)
    # 0.22 - 0.48: Inner Iris (Warm Golden Hazel Amber)
    # 0.48 - 0.62: Outer Iris (Olive Hazel)
    # 0.62 - 0.68: Limbal Ring (Dark Espresso)
    # 0.68 - 1.0: Sclera (Clean White with subtle warm shading)
    elements = color_ramp.color_ramp.elements
    elements[0].position = 0.0
    elements[0].color = (0.01, 0.01, 0.01, 1.0) # Pupil
    
    el1 = elements.new(0.24)
    el1.color = (0.01, 0.01, 0.01, 1.0) # Pupil edge
    
    el2 = elements.new(0.28)
    el2.color = (0.62, 0.38, 0.12, 1.0) # Golden amber iris
    
    el3 = elements.new(0.50)
    el3.color = (0.42, 0.28, 0.10, 1.0) # Hazel ring
    
    el4 = elements.new(0.60)
    el4.color = (0.08, 0.05, 0.03, 1.0) # Dark limbal ring
    
    elements[1].position = 0.66
    elements[1].color = (0.92, 0.92, 0.93, 1.0) # Sclera

    # Mapping centered on front pole of eye
    mapping.inputs['Location'].default_value = (0.0, 0.5, 0.0)
    mapping.inputs['Scale'].default_value = (3.2, 3.2, 3.2)

    e_links.new(texcoord.outputs['Object'], mapping.inputs['Vector'])
    e_links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    e_links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])
    e_links.new(color_ramp.outputs['Color'], bsdf_node.inputs['Base Color'])
    
    bsdf_node.inputs['Roughness'].default_value = 0.03 # Highly polished mirror wetness
    bsdf_node.inputs['Specular IOR Level'].default_value = 0.8
    e_links.new(bsdf_node.outputs['BSDF'], out_node.inputs['Surface'])

    eye_l.data.materials.append(eye_mat)
    eye_r.data.materials.append(eye_mat)

    # 3. Create Eyebrows (Arched, Espresso Dark Brown)
    brow_mat = bpy.data.materials.new("M_NYRA_Brows_Proxy")
    brow_mat.use_nodes = True
    b_bsdf = brow_mat.node_tree.nodes.get("Principled BSDF")
    b_bsdf.inputs['Base Color'].default_value = (0.12, 0.08, 0.06, 1.0)
    b_bsdf.inputs['Roughness'].default_value = 0.65

    def create_eyebrow(name, sign):
        curve_data = bpy.data.curves.new(name, type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.0028
        curve_data.bevel_resolution = 3
        curve_data.fill_mode = 'FULL'
        
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(2) # 3 points total
        
        pts = [
            (sign * 0.016, -0.126, 1.558), # Head
            (sign * 0.038, -0.106, 1.568), # Arch apex
            (sign * 0.056, -0.088, 1.550)  # Tail
        ]
        radii = [1.0, 1.2, 0.3]
        for i, (p, r) in enumerate(zip(pts, radii)):
            bp = spline.bezier_points[i]
            bp.co = p
            bp.radius = r
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
            
        obj = bpy.data.objects.new(name, curve_data)
        obj.data.materials.append(brow_mat)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    create_eyebrow("GEO-NYRA_Eyebrow.L", 1.0)
    create_eyebrow("GEO-NYRA_Eyebrow.R", -1.0)

    # 4. Create Eyelashes & Eyeliner Line (Winged almond cat-eye flick)
    lash_mat = bpy.data.materials.new("M_NYRA_Lashes_Proxy")
    lash_mat.use_nodes = True
    l_bsdf = lash_mat.node_tree.nodes.get("Principled BSDF")
    l_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    l_bsdf.inputs['Roughness'].default_value = 0.35

    def create_eyelash(name, sign):
        curve_data = bpy.data.curves.new(name, type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 0.0018
        curve_data.bevel_resolution = 3
        curve_data.fill_mode = 'FULL'
        
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(3) # 4 points
        
        pts = [
            (sign * 0.018, -0.124, 1.534), # Medial canthus
            (sign * 0.032, -0.115, 1.548), # Mid upper lid
            (sign * 0.050, -0.098, 1.542), # Lateral canthus
            (sign * 0.058, -0.092, 1.546)  # Winged flick!
        ]
        radii = [0.4, 1.2, 1.4, 0.2]
        for i, (p, r) in enumerate(zip(pts, radii)):
            bp = spline.bezier_points[i]
            bp.co = p
            bp.radius = r
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
            
        obj = bpy.data.objects.new(name, curve_data)
        obj.data.materials.append(lash_mat)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    create_eyelash("GEO-NYRA_Eyelash.L", 1.0)
    create_eyelash("GEO-NYRA_Eyelash.R", -1.0)

    # 5. Create Hair Proxy (High Ponytail + Fringe Tendrils + Purple Accent)
    hair_dark_mat = bpy.data.materials.new("M_NYRA_Hair_Dark")
    hair_dark_mat.use_nodes = True
    hd_bsdf = hair_dark_mat.node_tree.nodes.get("Principled BSDF")
    hd_bsdf.inputs['Base Color'].default_value = (0.09, 0.07, 0.06, 1.0) # Deep espresso brown
    hd_bsdf.inputs['Roughness'].default_value = 0.40
    hd_bsdf.inputs['Specular IOR Level'].default_value = 0.65

    hair_purple_mat = bpy.data.materials.new("M_NYRA_Hair_PurpleAccent")
    hair_purple_mat.use_nodes = True
    hp_bsdf = hair_purple_mat.node_tree.nodes.get("Principled BSDF")
    hp_bsdf.inputs['Base Color'].default_value = (0.58, 0.10, 0.88, 1.0) # Electric violet/magenta
    hp_bsdf.inputs['Roughness'].default_value = 0.35
    hp_bsdf.inputs['Specular IOR Level'].default_value = 0.75

    tie_mat = bpy.data.materials.new("M_NYRA_HairTie_Violet")
    tie_mat.use_nodes = True
    ht_bsdf = tie_mat.node_tree.nodes.get("Principled BSDF")
    ht_bsdf.inputs['Base Color'].default_value = (0.45, 0.08, 0.78, 1.0) # Saturated purple tie
    ht_bsdf.inputs['Roughness'].default_value = 0.55

    # A) Hair Tie / Band at crown
    tie_curve = bpy.data.curves.new("GEO-HairTie", type='CURVE')
    tie_curve.dimensions = '3D'
    tie_curve.bevel_depth = 0.009
    tie_curve.bevel_resolution = 4
    tie_curve.fill_mode = 'FULL'
    tie_spline = tie_curve.splines.new('BEZIER')
    tie_spline.bezier_points.add(3)
    tie_spline.use_cyclic_u = True
    tie_center = (0.0, 0.035, 1.632)
    r_tie = 0.032
    for i in range(4):
        ang = i * (math.pi / 2.0)
        bp = tie_spline.bezier_points[i]
        bp.co = (tie_center[0] + r_tie * math.cos(ang), tie_center[1] + r_tie * math.sin(ang) * 0.7, tie_center[2] + (i%2)*0.003)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    tie_obj = bpy.data.objects.new("GEO-NYRA_HairTie", tie_curve)
    tie_obj.data.materials.append(tie_mat)
    bpy.context.scene.collection.objects.link(tie_obj)

    # B) Ponytail Cascading Strands (Dark Base + Purple Streak)
    def create_hair_strand(name, pts, radii, mat, bevel=0.016):
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

    # Main ponytail central volume
    pony_center_pts = [
        (0.0, 0.035, 1.635),
        (0.0, 0.065, 1.705),
        (-0.015, 0.125, 1.640),
        (-0.025, 0.155, 1.520),
        (-0.010, 0.165, 1.380)
    ]
    pony_center_r = [1.2, 2.2, 2.4, 1.8, 0.6]
    create_hair_strand("GEO-NYRA_Pony_Center", pony_center_pts, pony_center_r, hair_dark_mat, bevel=0.024)

    # Ponytail lateral dark wings
    pony_left_pts = [
        (0.025, 0.035, 1.635),
        (0.045, 0.075, 1.695),
        (0.055, 0.120, 1.615),
        (0.045, 0.145, 1.490),
        (0.030, 0.150, 1.370)
    ]
    create_hair_strand("GEO-NYRA_Pony_LeftDark", pony_left_pts, [1.0, 1.8, 2.0, 1.4, 0.4], hair_dark_mat, bevel=0.018)

    pony_right_pts = [
        (-0.025, 0.035, 1.635),
        (-0.045, 0.075, 1.695),
        (-0.055, 0.120, 1.615),
        (-0.045, 0.145, 1.490),
        (-0.030, 0.150, 1.370)
    ]
    create_hair_strand("GEO-NYRA_Pony_RightDark", pony_right_pts, [1.0, 1.8, 2.0, 1.4, 0.4], hair_dark_mat, bevel=0.018)

    # SIGNATURE VIBRANT PURPLE STREAK (Character's left side / camera right)
    pony_purple_pts = [
        (0.038, 0.042, 1.645),
        (0.065, 0.088, 1.715),
        (0.085, 0.135, 1.630),
        (0.090, 0.160, 1.510),
        (0.070, 0.165, 1.390)
    ]
    create_hair_strand("GEO-NYRA_Pony_PurpleStreak", pony_purple_pts, [0.8, 1.4, 1.6, 1.2, 0.3], hair_purple_mat, bevel=0.014)

    # C) Front Face-Framing Fringe Tendrils
    # Left fringe (parting to jaw)
    fringe_l_pts = [
        (0.012, -0.095, 1.585),  # Parting
        (0.032, -0.108, 1.535),  # Past temple
        (0.046, -0.098, 1.475),  # Past cheekbone
        (0.042, -0.082, 1.425),  # Jaw taper
        (0.036, -0.068, 1.385)   # Tip at neck
    ]
    create_hair_strand("GEO-NYRA_Fringe_Left", fringe_l_pts, [0.8, 1.2, 1.1, 0.8, 0.2], hair_dark_mat, bevel=0.007)

    # Right fringe
    fringe_r_pts = [
        (-0.012, -0.095, 1.585),
        (-0.032, -0.108, 1.535),
        (-0.046, -0.098, 1.475),
        (-0.042, -0.082, 1.425),
        (-0.036, -0.068, 1.385)
    ]
    create_hair_strand("GEO-NYRA_Fringe_Right", fringe_r_pts, [0.8, 1.2, 1.1, 0.8, 0.2], hair_dark_mat, bevel=0.007)

    # Forehead hair root volume (swept back cranium cap)
    crown_vol_pts = [
        (0.0, -0.088, 1.595),
        (0.0, -0.045, 1.645),
        (0.0, 0.015, 1.650)
    ]
    create_hair_strand("GEO-NYRA_Crown_Volume", crown_vol_pts, [1.4, 2.5, 2.0], hair_dark_mat, bevel=0.038)

    # 6. Silver Hoop Earrings
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

    # 7. Sports Bra Straps Framing Bust
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
            (sign * 0.072, -0.015, 1.395), # Trapezius/shoulder
            (sign * 0.065, -0.065, 1.340), # Clavicle
            (sign * 0.045, -0.115, 1.280)  # Sternum neckline
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

if __name__ == "__main__":
    build_nyra_phase2b_prototype()
