"""Verify original checkpoints and texture-only comparison geometry; inventory raw outputs."""
import argparse,hashlib,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--pipeline',type=Path,required=True);a=p.parse_args();sys.path.insert(0,str(a.pipeline));import numpy as np
from image_to_3dlab.photo_paint import read_glb
root=Path(__file__).resolve().parents[1];r=root/'recovery/nyra'
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
checks=[]
for f in json.loads((r/'checkpoint-manifest.json').read_text())['files']:
    assert digest(root/f['path'])==f['sha256'],f['path'];checks.append({'path':f['path'],'preserved':True})
for c in 'ab':
    d=r/'candidates'/f'candidate-{c}';raw=read_glb(d/f'nyra-{c}.glb');paint=read_glb(d/f'nyra-{c}-pixel-match.glb')
    assert all(np.array_equal(raw[i],paint[i]) for i in range(3)),f'{c}: Pixel Match modified geometry'
    assert not np.array_equal(raw[3],paint[3]),f'{c}: Pixel Match made no texture change'
    checks.append({'candidate':c,'pixel_match_positions_uv_indices_unchanged':True,'base_color_changed':True})
    inventory=[]
    for f in sorted(d.rglob('*')):
        if f.is_file() and 'renders' not in f.parts and f.name!='preservation-manifest.json':
            inventory.append({'path':str(f.relative_to(root)),'bytes':f.stat().st_size,'sha256':digest(f)})
    (d/'preservation-manifest.json').write_text(json.dumps(inventory,indent=2))
(r/'qa/preservation-verification.json').write_text(json.dumps(checks,indent=2));print('VERDICT: PASS — original checkpoints and both geometry/UV comparisons verified')
