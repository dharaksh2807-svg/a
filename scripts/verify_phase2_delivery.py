"""Verify delivered assets and record content hashes without rerendering."""
from pathlib import Path
import json,hashlib,struct
root=Path(__file__).resolve().parents[1]
qa=root/'qa/phase2'
source=json.loads((qa/'source-validation.json').read_text());assert source['pass']
validation=json.loads((qa/'glb-validation.json').read_text());assert validation['issues']['numErrors']==0
stats=json.loads((qa/'mesh-statistics.json').read_text())
glb=root/'exports/nyra-visual.glb';b=glb.read_bytes();assert b[:4]==b'glTF'
n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);assert len(g['meshes'])==5 and not g.get('skins') and not g.get('animations')
triangles=sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])
assert triangles==stats['export_triangles'];assert len(b)==stats['glb_bytes']
assert len(g['materials'])==5 and all('baseColorTexture' in m['pbrMetallicRoughness'] for m in g['materials'])
assert all('uri' not in i for i in g['images'])
views=json.loads((qa/'renders.json').read_text());assert len(views)==10
files=[root/'source/blender/nyra/nyra-visual.blend',glb,*sorted((root/'textures/nyra').glob('*.png'))]
for r in views:
 p=root/r['file'];data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';assert struct.unpack_from('>II',data,16)==(1200,1500);files.append(p)
report={'pass':True,'render_count':len(views),'render_dimensions':[1200,1500],'glb_triangles':triangles,'glb_bytes':len(b),'glb_errors':validation['issues']['numErrors'],'glb_warnings':validation['issues']['numWarnings'],'files':[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
(qa/'deliverables.json').write_text(json.dumps(report,indent=2)+'\n');print('VERDICT: PASS',len(files),'assets;',triangles,'GLB triangles')
