"""Run independent local multi-view candidates, serially and only while Metal is idle."""
import argparse, json, subprocess, time
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('--pipeline',type=Path,required=True);p.add_argument('--project',type=Path,required=True);a=p.parse_args()
root=a.project/'recovery/nyra'; status=root/'qa/generation-status.json'
def record(**values):
    status.write_text(json.dumps({'updated':time.strftime('%Y-%m-%dT%H:%M:%S%z'),**values},indent=2))
def active():return subprocess.run(['pgrep','-x','trellis-cli'],capture_output=True,text=True).stdout.split()
assert (root/'inputs/visual-approval.json').is_file(), 'Inspect cutouts before launching'
for letter,seed in [('a',42),('b',1337)]:
    folder=root/'candidates'/f'candidate-{letter}';folder.mkdir(parents=True,exist_ok=True)
    out=folder/f'nyra-{letter}.glb'
    if out.is_file() and out.with_suffix('.provenance.json').is_file():continue
    while True:
        busy=active()
        if busy:record(stage='waiting_for_Metal',candidate=letter,active_pids=busy);time.sleep(15);continue
        time.sleep(12)
        if not active():break
    command=[str(a.pipeline/'.venv/bin/python'),str(a.pipeline/'scripts/pixal3d_generate.py'),str(root/'inputs/nyra-front.png'),str(out),'--back',str(root/'inputs/nyra-back.png'),'--res','1024','--steps','12','--seed',str(seed),'--no-matte']
    record(stage='generating',candidate=letter,seed=seed,command=command)
    with (folder/'generation.log').open('w') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,cwd=a.pipeline)
    if result.returncode or not out.is_file():
        record(stage='failed',candidate=letter,returncode=result.returncode);raise SystemExit(1)
record(stage='both_candidates_generated_awaiting_visual_review')
