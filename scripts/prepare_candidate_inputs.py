"""Prepare local cutouts with the installed AssetFurnace matte implementation.
Waits for image-to-3D inference to be idle; never downloads weights.
"""
import argparse,json,sys,time,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--pipeline',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.pipeline))
from PIL import Image
import numpy as np
from image_to_3dlab.matte import cut_out,new_session,matte_model,is_matted

def active_metal():
 r=subprocess.run(['pgrep','-x','trellis-cli'],capture_output=True,text=True);return r.stdout.split()
a.output.mkdir(parents=True,exist_ok=True)
while active_metal():
 (a.output/'preparation-status.json').write_text(json.dumps({'stage':'waiting_for_Metal_inference_to_finish','pids':active_metal()}));time.sleep(15)
# A second idle observation prevents starting in a short transition between queued candidates.
time.sleep(12)
while active_metal():time.sleep(15)
session=new_session(allow_download=False);report={'matte_model':matte_model(),'images':[]}
for filename,target in [('01-front-a-pose.png','front'),('02-rear-a-pose.png','back'),('03-left-profile.png','side'),('04-face-front.png','face')]:
 im=Image.open(a.source/filename);cut,model=cut_out(im,session=session,allow_download=False);alpha=np.asarray(cut.getchannel('A'));yy,xx=np.where(alpha>32);bbox=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
 cut.getchannel('A').save(a.output/f'{target}-mask-original.png')
 if target in ['front','back']:
  crop=cut.crop(bbox);canvas=Image.new('RGBA',(1024,1536),(0,0,0,0));scale=min(924/crop.width,1416/crop.height);new=(round(crop.width*scale),round(crop.height*scale));crop=crop.resize(new,Image.Resampling.LANCZOS);canvas.alpha_composite(crop,((1024-new[0])//2,1476-new[1]));cut=canvas
 assert is_matted(cut)
 cut.save(a.output/f'nyra-{target}.png')
 bg=Image.new('RGBA',cut.size,(82,86,96,255));bg.alpha_composite(cut);bg.convert('RGB').save(a.output/f'{target}-mask-preview.jpg',quality=92)
 report['images'].append({'source':filename,'output':f'nyra-{target}.png','source_size':list(im.size),'source_foreground_bbox':bbox,'output_size':list(cut.size),'transparent_fraction':float((np.asarray(cut.getchannel('A'))<16).mean())})
(a.output/'mask-report.json').write_text(json.dumps(report,indent=2));(a.output/'preparation-status.json').write_text(json.dumps({'stage':'complete_awaiting_visual_mask_check'}));print('VERDICT: PASS — four local cutouts prepared; no downloads')
