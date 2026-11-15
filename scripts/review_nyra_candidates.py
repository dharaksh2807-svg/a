"""Preserve both texture variants and render actual generated surfaces sequentially."""
import argparse,json,subprocess,time,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--pipeline',type=Path,required=True);p.add_argument('--project',type=Path,required=True);a=p.parse_args();root=a.project/'recovery/nyra';status=root/'qa/review-status.json';python=a.pipeline/'.venv/bin/python'
def record(**values):status.write_text(json.dumps({'updated':time.strftime('%Y-%m-%dT%H:%M:%S%z'),**values},indent=2))
def wait_idle():
    while subprocess.run(['pgrep','-x','trellis-cli'],capture_output=True).returncode==0:record(stage='waiting_for_Metal');time.sleep(15)
def run(command,log):
    wait_idle()
    with log.open('w') as f:r=subprocess.run([str(x) for x in command],stdout=f,stderr=subprocess.STDOUT,cwd=a.project)
    if r.returncode:record(stage='failed',log=str(log),returncode=r.returncode);raise SystemExit(r.returncode)
while True:
    state=json.loads((root/'qa/generation-status.json').read_text())
    if state['stage']=='failed':raise SystemExit('Generation failed; no review attempted')
    if state['stage']=='both_candidates_generated_awaiting_visual_review':break
    time.sleep(15)
for letter in ['a','b']:
    folder=root/'candidates'/f'candidate-{letter}';raw=folder/f'nyra-{letter}.glb';painted=folder/f'nyra-{letter}-pixel-match.glb'
    record(stage='pixel_match',candidate=letter)
    if not painted.exists():run([python,a.pipeline/'scripts/photo_paint.py',raw,raw.with_suffix('.svviews'),painted,'--weights',folder/'pixel-match-trust.png'],folder/'pixel-match.log')
    for variant,source,views in [('original',raw,'front,three-quarter,side,rear,face,clay,wireframe,wireframe-face,gameplay'),('pixel-match',painted,'front,rear,face')]:
        out=folder/'renders'/variant;out.mkdir(parents=True,exist_ok=True)
        record(stage='rendering',candidate=letter,variant=variant)
        if not (out/'nyra-review.blend').exists():run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--disable-autoexec','--python',a.project/'scripts/render_replacement.py','--','--input',source,'--output',out,'--views',views],folder/f'render-{variant}.log')
record(stage='ready_for_visual_comparison')
