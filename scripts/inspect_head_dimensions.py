import bpy
import mathutils

blend_path = "source/upstream/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend"

bpy.ops.wm.read_factory_settings(use_empty=True)

with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.objects = [
        "GEO-body_female_realistic",
        "GEO-body_female_realistic.eye.L",
        "GEO-body_female_realistic.eye.R",
        "GEO-head_animation_realistic",
        "GEO-head_animation_realistic.sclera.L",
        "GEO-head_animation_realistic.sclera.R",
        "GEO-head_animation_realistic.iris.L",
        "GEO-head_animation_realistic.iris.R",
    ]

for obj in data_to.objects:
    bpy.context.scene.collection.objects.link(obj)

for obj in bpy.data.objects:
    print(f"\n--- {obj.name} ---")
    print(f"Dimensions: X={obj.dimensions.x:.3f}m, Y={obj.dimensions.y:.3f}m, Z={obj.dimensions.z:.3f}m")
    bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
    min_z = min(b.z for b in bbox)
    max_z = max(b.z for b in bbox)
    print(f"Z range: {min_z:.3f}m to {max_z:.3f}m (Height: {max_z - min_z:.3f}m)")
    
    # Check multires
    for m in obj.modifiers:
        if m.type == 'MULTIRES':
            print(f"Multires: total_levels={m.total_levels}, sculpt_levels={m.sculpt_levels}, render_levels={m.render_levels}")
