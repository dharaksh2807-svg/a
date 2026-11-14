"""Verify deliverable integrity; no external Python packages required."""
import hashlib
import json
import struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def require(condition,message):
    if not condition:
        raise AssertionError(message)
    checks.append(message)
try:
    for name in ['ART_DIRECTION.md','ASSET_RESEARCH.md','ASSET_LICENSES.md','PRODUCTION_PLAN.md','ENVIRONMENT_AUDIT.md','viewer/index.html','viewer/viewer.js','animations/README.md','textures/README.md']:
        require((ROOT/name).stat().st_size>0,f'{name} present')
    manifest=json.loads((ROOT/'references/licenses/rain-manifest.json').read_text())
    for f in manifest['files']:
        path=ROOT/f['path']
        require(hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256'],f'Upstream unchanged: {f["path"]}')
    for path in sorted((ROOT/'renders').glob('*.png'))+[ROOT/'references/concepts/runner-concepts.png']:
        data=path.read_bytes()
        require(data[:8]==b'\x89PNG\r\n\x1a\n' and all(v>0 for v in struct.unpack('>II',data[16:24])),f'PNG valid header/dimensions: {path.name}')
    for name in ['environment-smoke','rain-geometry-study']:
        data=(ROOT/f'exports/{name}.glb').read_bytes()
        magic,version,total=struct.unpack_from('<4sII',data)
        require(magic==b'glTF' and version==2 and total==len(data),f'GLB container valid: {name}')
        length,kind=struct.unpack_from('<I4s',data,12)
        require(kind==b'JSON',f'GLB JSON present: {name}')
        model=json.loads(data[20:20+length])
        if name=='rain-geometry-study':
            require(not model.get('skins') and not model.get('animations'),'Study correctly has no rig or animation')
            triangles=sum(model['accessors'][p['indices']]['count']//3 for m in model['meshes'] for p in m['primitives'])
            require(triangles==76974,'Study has measured 76,974 triangles')
        validation=json.loads((ROOT/f'qa/evidence/{name}-validation.json').read_text())
        require(validation['issues']['numErrors']==0,f'Khronos validator zero errors: {name}')
    engines=json.loads((ROOT/'qa/evidence/environment-results.json').read_text())
    require(engines['core']['status']=='pass','Mandatory Blender core operations passed')
    require(all(v['status']=='pass' for v in engines.values()),'CPU, Eevee and Metal probes passed on this host')
    result={'status':'pass','checks':checks}
    (ROOT/'qa/evidence/project-integrity.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'{len(checks)} integrity checks passed\nVERDICT: PASS')
except Exception as exc:
    (ROOT/'qa/evidence/project-integrity.json').write_text(json.dumps({'status':'fail','checks':checks,'error':str(exc)},indent=2)+'\n')
    print(f'VERDICT: FAIL -- {exc}')
    raise
