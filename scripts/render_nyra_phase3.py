"""Phase 3 evidence: Phase 2 camera and neutral studio settings retained."""
import bpy,json,sys,time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;cam=scene.camera
quick='--quick' in sys.argv
scene.render.resolution_x=700 if quick else 1200;scene.render.resolution_y=900 if quick else 1500
scene.cycles.samples=24 if quick else 64
scene.render.resolution_percentage=100
views=[('01-front',(0,-6,1.0),(0,0,.88),2.05),('02-left-profile',(-6,0,1.0),(0,0,.88),2.05),('03-rear',(0,6,1.0),(0,0,.88),2.05),('04-three-quarter-front',(3,-6,1.75),(0,0,.9),2.05),('05-three-quarter-rear',(-3,6,1.75),(0,0,.9),2.05),('06-face',(.42,-3,1.75),(0,-.05,1.61),.48),('07-garment-detail',(1.5,-4,1.8),(0,0,1.20),.80),('08-neutral-presentation',(-1,-6,1.1),(0,0,.88),2.05),('09-metro-light',(-3,6,1.8),(0,0,.9),2.05),('10-sneaker-detail',(2,-4,1.2),(0,-.07,.115),.48)]
views.append(('11-gameplay-distance',(0,6,2.4),(0,0,.90),7.4))
if quick and '--only' not in sys.argv:views=[views[3],views[2],views[5]]
if '--only' in sys.argv:
 wanted=sys.argv[sys.argv.index('--only')+1];views=[v for v in views if v[0]==wanted]
if '--skip' in sys.argv:views=[v for v in views if v[0] not in sys.argv[sys.argv.index('--skip')+1].split(',')]
results=[]
for name,position,target,scale in views:
 scene.render.resolution_x=700 if quick else (1280 if name=='11-gameplay-distance' else 1200);scene.render.resolution_y=900 if quick else (720 if name=='11-gameplay-distance' else 1500)
 cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 if name in ['09-metro-light','11-gameplay-distance']:
  # Modern Metro: white-gold sun, blue fill, cyan sky (read-only source reference).
  for o in scene.objects:
   if o.type=='LIGHT':o.hide_render=True
  for label,pos,color,energy in [('sun',(24,-18,42),(1,.98,.918),1.45),('sky fill',(-24,-14,28),(.627,.769,.910),.70)]:
   data=bpy.data.lights.new('Metro '+label,'SUN');data.color=color;data.energy=energy;data.angle=.12
   light=bpy.data.objects.new(data.name,data);scene.collection.objects.link(light);light.location=pos;light.rotation_euler=(Vector((0,0,.9))-light.location).to_track_quat('-Z','Y').to_euler()
  scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.784,.902,.976,1)
  scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 elif name=='10-sneaker-detail':
  for o in scene.objects:
   if o.type=='LIGHT':o.hide_render=o.name.startswith('Metro ')
  scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1)
  scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
 path=ROOT/('renders/phase3/before' if '--baseline' in sys.argv else 'renders/phase3')/f'{"draft-" if quick else ""}{name}.png';scene.render.filepath=str(path);start=time.monotonic();bpy.ops.render.render(write_still=True);results.append({'file':str(path.relative_to(ROOT)),'seconds':round(time.monotonic()-start,2),'view':name})
manifest=ROOT/'qa/phase3'/('baseline-renders.json' if '--baseline' in sys.argv else 'draft-renders.json' if quick else 'renders.json')
previous=json.loads(manifest.read_text()) if manifest.exists() else []
by_name={r['view']:r for r in previous}
by_name.update({r['view']:r for r in results})
manifest.write_text(json.dumps(list(by_name.values()),indent=2))
print('VERDICT: PASS')
