import bpy
import math
import mathutils

bpy.ops.wm.read_factory_settings(use_empty=True)

# Test creating a curve-based hair strand with taper and bevel
curve_data = bpy.data.curves.new("HairStrand", type='CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.008
curve_data.bevel_resolution = 4
curve_data.fill_mode = 'FULL'

polyline = curve_data.splines.new('BEZIER')
polyline.bezier_points.add(2) # 3 points total

pts = [
    (0.01, -0.10, 1.60),   # Root near parting
    (0.035, -0.11, 1.52),  # Mid sweep past cheek
    (0.025, -0.09, 1.44)   # Tip at jaw
]

for i, p in enumerate(pts):
    bp = polyline.bezier_points[i]
    bp.co = p
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'
    # Taper radius from root to tip
    bp.radius = 1.0 - (i * 0.4)

curve_obj = bpy.data.objects.new("HairStrand", curve_data)
bpy.context.scene.collection.objects.link(curve_obj)

print("Curve hair strand created successfully!")
print("Objects in scene:", [o.name for o in bpy.data.objects])
