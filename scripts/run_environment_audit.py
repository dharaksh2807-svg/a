"""Bound optional GPU probes so an unavailable backend cannot block core checks."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BLENDER = os.environ.get('BLENDER') or shutil.which('blender') or '/Applications/Blender.app/Contents/MacOS/Blender'
results={}
timeout = float(os.environ.get('BLENDER_PROBE_TIMEOUT','180'))
for mode in ['core','eevee','metal']:
    output=ROOT/f'qa/evidence/blender-{mode}.log'
    with output.open('w') as log:
        try:
            run=subprocess.run([BLENDER,'--background','--factory-startup','--python',str(ROOT/'scripts/smoke_blender.py'),'--',mode],stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
            results[mode]={'exit_code':run.returncode,'status':'pass' if run.returncode==0 else 'fail'}
        except subprocess.TimeoutExpired:
            results[mode]={'status':'timeout','limit_seconds':timeout,'note':'Process terminated by audit runner; capability not verified.'}
    (ROOT/'qa/evidence/environment-results.json').write_text(json.dumps(results,indent=2))
    print(mode,results[mode],flush=True)
print('VERDICT: PASS' if results['core']['status']=='pass' else 'VERDICT: FAIL -- mandatory Blender operations failed')
sys.exit(0 if results['core']['status']=='pass' else 1)
