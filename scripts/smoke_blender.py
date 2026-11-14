"""Run with Blender --background --factory-startup --python scripts/smoke_blender.py."""
import bpy
import json
import platform
import sys
import time
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
mode = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'core'
report = {"blender": bpy.app.version_string, "python": sys.version, "platform": platform.platform(), "tests": {}}

def test(name, fn):
    start = time.monotonic()
    try:
        result = fn()
        report["tests"][name] = {"pass": True, "seconds": round(time.monotonic()-start, 3), "result": result}
    except Exception as exc:
        report["tests"][name] = {"pass": False, "error": repr(exc)}
    (ROOT / f"qa/evidence/blender-{mode}.json").write_text(json.dumps(report, indent=2))

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.object
obj.name = "ENVIRONMENT_TEST_CUBE_NOT_CHARACTER"
mat = bpy.data.materials.new("Test coral")
mat.diffuse_color = (0.8, 0.12, 0.07, 1)
obj.data.materials.append(mat)
bevel = obj.modifiers.new("Edge highlights", "BEVEL")
bevel.width, bevel.segments = 0.1, 3
bpy.ops.object.camera_add(location=(4,-6,3))
camera = bpy.context.object
camera.rotation_euler = (Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
scene = bpy.context.scene
scene.camera = camera
bpy.ops.object.light_add(type="AREA", location=(1,-4,5))
bpy.context.object.data.energy = 1000
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 5
scene.render.resolution_x = scene.render.resolution_y = 256
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.world.color = (0.2,0.2,0.2)
report['engine_probe'] = mode

def save():
    path = ROOT/'source/blender/environment-smoke.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    assert path.stat().st_size > 0
    return {'path':str(path.relative_to(ROOT)), 'bytes':path.stat().st_size}

def render(engine, device=None):
    scene.render.engine = engine
    if engine == 'CYCLES':
        scene.cycles.samples = 8
        scene.cycles.device = device
        scene.cycles.use_denoising = False
    path = ROOT/f'renders/environment-{engine.lower()}-{device or "default"}.png'
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    assert path.read_bytes().startswith(b'\x89PNG')
    return {'path':str(path.relative_to(ROOT)), 'bytes':path.stat().st_size}

def metal():
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'
    prefs.get_devices()
    report['cycles_devices'] = [{'name':d.name,'type':d.type} for d in prefs.devices]
    assert any(d.type=='METAL' for d in prefs.devices), 'No Metal device'
    for d in prefs.devices:
        d.use = d.type == 'METAL'
    return render('CYCLES', 'GPU')

def export():
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    path = ROOT/'exports/environment-smoke.glb'
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True, export_animations=False)
    assert path.read_bytes()[:4] == b'glTF'
    return {'path':str(path.relative_to(ROOT)), 'bytes':path.stat().st_size}

if mode == 'core':
    test('create_object', lambda: {'name':obj.name,'vertices':len(obj.data.vertices)})
    test('save_blend', save)
    test('cycles_cpu_render', lambda: render('CYCLES','CPU'))
    test('export_glb', export)
elif mode == 'metal':
    test('cycles_metal_render', metal)
elif mode == 'eevee':
    test('eevee_render', lambda: render('BLENDER_EEVEE'))
print(json.dumps(report, indent=2))
ok = bool(report['tests']) and all(v['pass'] for v in report['tests'].values())
print('VERDICT: PASS' if ok else 'VERDICT: FAIL -- see engine JSON report')
if not ok:
    sys.exit(1)
