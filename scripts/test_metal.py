import bpy

preferences = bpy.context.preferences
cycles_prefs = preferences.addons['cycles'].preferences
cycles_prefs.refresh_devices()
print("Cycles compute device types:")
for t in cycles_prefs.get_device_types(bpy.context):
    print(" - Type:", t)
devices = cycles_prefs.devices
print("Available devices:")
for d in devices:
    print(f" - {d.name} ({d.type}) use={d.use}")
