import bpy

# Set up test render
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') else 'BLENDER_EEVEE'
print("EEVEE engine name:", scene.render.engine)
scene.render.engine = 'CYCLES'
print("Cycles engine set successfully")
