import bpy
import math
import mathutils
import numpy as np

def create_facial_prototype():
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

    # Ensure shape keys exist (create Basis)
    if not body.data.shape_keys:
        body.shape_key_add(name="Basis")
    basis = body.data.shape_keys.key_blocks["Basis"]

    coords = np.array([v.co for v in me.vertices], dtype=np.float32)
    n_verts = len(coords)

    def apply_deformation(name, deform_func):
        sk = body.shape_key_add(name=name)
        new_coords = coords.copy()
        for i in range(n_verts):
            p = mathutils.Vector(coords[i])
            if p.z > 1.30 and p.y < 0.05: # Head region only
                offset = deform_func(p)
                if offset:
                    new_coords[i] += np.array(offset, dtype=np.float32)
        sk.data.foreach_set("co", new_coords.ravel())
        sk.value = 1.0
        return sk

    # Smooth Gaussian / polynomial falloff
    def gfalloff(p, center, radius):
        dist_sq = (p.x - center[0])**2 + (p.y - center[1])**2 + (p.z - center[2])**2
        r_sq = radius**2
        if dist_sq >= r_sq:
            return 0.0
        return math.exp(-2.2 * dist_sq / r_sq) * (1.0 - dist_sq / r_sq)**2

    # --- Shape Key 1: Jaw & Chin Sculpt ---
    def deform_jaw_chin(p):
        dx, dy, dz = 0.0, 0.0, 0.0
        
        # Chin apex refinement: delicate pointed chin, advanced forward and elevated
        w_chin = gfalloff(p, (0.0, -0.115, 1.420), 0.042)
        if w_chin > 0:
            dy -= 0.0055 * w_chin # Forward in -Y
            dz += 0.0035 * w_chin # Lift in +Z
            # Taper lateral chin
            dx -= math.copysign(0.0038 * abs(p.x) / 0.02, p.x) * w_chin

        # Mandibular angle definition (softly squared feminine jawline)
        for sign in [-1.0, 1.0]:
            w_angle = gfalloff(p, (sign * 0.058, -0.050, 1.428), 0.038)
            if w_angle > 0:
                dx += sign * 0.0038 * w_angle # Defined jaw corner
                dy -= 0.0028 * w_angle
                dz += 0.0022 * w_angle
            
            # Taper lower cheek toward jaw
            w_taper = gfalloff(p, (sign * 0.048, -0.082, 1.435), 0.032)
            if w_taper > 0:
                dx -= sign * 0.0032 * w_taper # Slim lower cheek
                dy += 0.0018 * w_taper
        
        # Submental / under-jaw tightness
        w_under = gfalloff(p, (0.0, -0.065, 1.405), 0.048)
        if w_under > 0:
            dz += 0.0045 * w_under
            dy += 0.0030 * w_under

        if dx != 0 or dy != 0 or dz != 0:
            return (dx, dy, dz)
        return None

    # --- Shape Key 2: Zygomatic & Cheek Sculpt ---
    def deform_cheeks(p):
        dx, dy, dz = 0.0, 0.0, 0.0
        # High, prominent sculpted cheekbones (NYRA zygomatic arch)
        for sign in [-1.0, 1.0]:
            w_cheek = gfalloff(p, (sign * 0.062, -0.076, 1.518), 0.046)
            if w_cheek > 0:
                dx += sign * 0.0068 * w_cheek # Outward projection
                dy -= 0.0046 * w_cheek        # Anterior projection
                dz += 0.0038 * w_cheek        # Superior elevation
            
            # Submalar athletic hollow definition
            w_sub = gfalloff(p, (sign * 0.052, -0.065, 1.470), 0.035)
            if w_sub > 0:
                dx -= sign * 0.0032 * w_sub   # Sculpted cheek hollow
                dy += 0.0024 * w_sub

        if dx != 0 or dy != 0 or dz != 0:
            return (dx, dy, dz)
        return None

    # --- Shape Key 3: Almond Eyes & Canthal Tilt ---
    def deform_eyes(p):
        dx, dy, dz = 0.0, 0.0, 0.0
        for sign in [-1.0, 1.0]:
            # Lateral canthus (outer corner): positive canthal tilt sweep
            w_lat = gfalloff(p, (sign * 0.052, -0.096, 1.536), 0.026)
            if w_lat > 0:
                dz += 0.0052 * w_lat          # Lift outer eye corner
                dx += sign * 0.0032 * w_lat   # Widen almond aperture
                dy -= 0.0018 * w_lat

            # Upper eyelid apex: open aperture and define almond curvature
            w_lid = gfalloff(p, (sign * 0.034, -0.110, 1.546), 0.025)
            if w_lid > 0:
                dz += 0.0036 * w_lid          # Open upper lid
                dy += 0.0022 * w_lid

            # Supratarsal crease (double eyelid fold)
            w_crease = gfalloff(p, (sign * 0.036, -0.106, 1.554), 0.024)
            if w_crease > 0:
                dy += 0.0028 * w_crease       # Deepen fold
                dz += 0.0018 * w_crease

            # Medial canthus (tear duct): slight downward anchor
            w_med = gfalloff(p, (sign * 0.016, -0.125, 1.531), 0.016)
            if w_med > 0:
                dz -= 0.0018 * w_med
                dx -= sign * 0.0010 * w_med

        if dx != 0 or dy != 0 or dz != 0:
            return (dx, dy, dz)
        return None

    # --- Shape Key 4: Nose Refinement ---
    def deform_nose(p):
        dx, dy, dz = 0.0, 0.0, 0.0
        
        # Nasal tip: refine, slight upturned break
        w_tip = gfalloff(p, (0.0, -0.1674, 1.5024), 0.026)
        if w_tip > 0:
            dy -= 0.0038 * w_tip              # Forward tip projection
            dz += 0.0042 * w_tip              # Supratip break & upward tilt
            dx -= math.copysign(0.0028 * abs(p.x) / 0.012, p.x) * w_tip # Slim tip width

        # Alar base (nostril wings): narrow width
        for sign in [-1.0, 1.0]:
            w_ala = gfalloff(p, (sign * 0.017, -0.150, 1.488), 0.022)
            if w_ala > 0:
                dx -= sign * 0.0035 * w_ala   # Narrow nostril width
                dz += 0.0016 * w_ala

        # Nasal bridge (dorsum): slim straight width
        w_bridge = gfalloff(p, (0.0, -0.145, 1.522), 0.028)
        if w_bridge > 0:
            dx -= math.copysign(0.0022 * abs(p.x) / 0.010, p.x) * w_bridge

        if dx != 0 or dy != 0 or dz != 0:
            return (dx, dy, dz)
        return None

    # --- Shape Key 5: Lips & Cupid's Bow ---
    def deform_lips(p):
        dx, dy, dz = 0.0, 0.0, 0.0
        
        # Upper lip Cupid's bow peaks
        for sign in [-1.0, 1.0]:
            w_peak = gfalloff(p, (sign * 0.0075, -0.154, 1.465), 0.016)
            if w_peak > 0:
                dz += 0.0036 * w_peak         # Sharp Cupid peaks
                dy -= 0.0032 * w_peak         # Forward projection
                dx += sign * 0.0012 * w_peak

        # Philtrum groove (depression between peaks)
        w_phil = gfalloff(p, (0.0, -0.150, 1.474), 0.014)
        if w_phil > 0:
            dy += 0.0025 * w_phil             # Deepen philtrum

        # Lower lip fullness & central cushion
        w_low = gfalloff(p, (0.0, -0.153, 1.444), 0.024)
        if w_low > 0:
            dy -= 0.0048 * w_low              # Plush lower lip
            dz -= 0.0015 * w_low
            # Central bilobed cleft
            w_cleft = gfalloff(p, (0.0, -0.153, 1.442), 0.009)
            dy += 0.0018 * w_cleft

        # Commissures (mouth corners): micro-lift for confident composure
        for sign in [-1.0, 1.0]:
            w_corner = gfalloff(p, (sign * 0.025, -0.138, 1.455), 0.018)
            if w_corner > 0:
                dz += 0.0026 * w_corner       # Subtle lift
                dy += 0.0014 * w_corner

        if dx != 0 or dy != 0 or dz != 0:
            return (dx, dy, dz)
        return None

    # Apply modular shape keys
    sk_jaw = apply_deformation("NYRA_Jaw_and_Chin", deform_jaw_chin)
    sk_cheeks = apply_deformation("NYRA_Cheekbones_Zygomatic", deform_cheeks)
    sk_eyes = apply_deformation("NYRA_Almond_Eyes", deform_eyes)
    sk_nose = apply_deformation("NYRA_Nose_Refinement", deform_nose)
    sk_lips = apply_deformation("NYRA_Lips_and_Philtrum", deform_lips)

    # Combined master prototype key
    def deform_master(p):
        offsets = [
            deform_jaw_chin(p),
            deform_cheeks(p),
            deform_eyes(p),
            deform_nose(p),
            deform_lips(p)
        ]
        dx = sum(o[0] for o in offsets if o)
        dy = sum(o[1] for o in offsets if o)
        dz = sum(o[2] for o in offsets if o)
        if dx != 0 or dy != 0 or dz != 0:
            return (dx, dy, dz)
        return None

    # Reset component keys to 0 and set Master to 1.0 for clean inspection
    for sk in [sk_jaw, sk_cheeks, sk_eyes, sk_nose, sk_lips]:
        sk.value = 0.0

    sk_master = apply_deformation("NYRA_Master_Prototype", deform_master)
    sk_master.value = 1.0

    # Eyeballs follow the almond socket deformation
    eye_l.location.x += 0.0012
    eye_l.location.z += 0.0022
    eye_l.location.y -= 0.0012

    eye_r.location.x -= 0.0012
    eye_r.location.z += 0.0022
    eye_r.location.y -= 0.0012

    # Save editable prototype blend file
    save_path = "production_v3/prototype/nyra_head_prototype.blend"
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"Saved updated editable prototype blend to: {save_path}")

if __name__ == "__main__":
    create_facial_prototype()
