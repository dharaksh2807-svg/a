"""Identical studio, cameras, color management and sampling for both checkpoints."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:];variant=args[0]
src=R.parents[1]/'candidates/candidate-a/renders/original/nyra-review.blend' if variant=='before' else R/'NYRA-Final-Recovery.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.context.scene;c=s.camera
s.render.engine='CYCLES';s.cycles.samples=40;s.cycles.use_denoising=True;s.cycles.seed=17
s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
views={
 'front':((0,-4,1),(0,0,.89),2.04,(1000,1300)),
 'rear':((0,4,1),(0,0,.89),2.04,(1000,1300)),
 'side':((-4,0,1),(0,0,.89),2.04,(1000,1300)),
 'three-quarter':((2.7,-4,1.5),(0,0,.89),2.04,(1000,1300)),
 'face':((.04,-4,1.63),(0,-.025,1.58),.46,(1000,1200)),
 'abdomen':((0,-3,1.23),(0,0,1.23),.36,(1100,900)),
 'abdomen-oblique':((1.5,-3,1.28),(0,-.04,1.23),.37,(1100,900)),
 'abdomen-clay':((1.5,-3,1.28),(0,-.04,1.23),.37,(1100,900)),
 'clay':((2.7,-4,1.5),(0,0,.89),2.04,(1000,1300)),
 'footwear':((.9,-2, .34),(0,-.04,.12),.48,(1100,800)),
 'gameplay':((0,4,2.25),(0,0,1),3.6,(1280,720))}
clay=bpy.data.materials.get('Clay | reveals generated surface')
objects=[o for o in s.objects if o.type=='MESH' and o.name!='Studio floor'];mats={o.name:list(o.data.materials) for o in objects}
for name in (args[1].split(',') if len(args)>1 else views):
 pos,tgt,scale,res=views[name];c.location=pos;c.rotation_euler=(Vector(tgt)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale
 s.render.resolution_x,s.render.resolution_y=res;s.render.resolution_percentage=100
 for o in objects:
  for i,m in enumerate(mats[o.name]):o.data.materials[i]=clay if 'clay' in name else m
 s.render.filepath=str(R/'renders'/f'{variant}-{name}.png');bpy.ops.render.render(write_still=True)
(R/f'{variant}-cameras.json').write_text(json.dumps(views,indent=2))
