"""Build nine animation rows using the attributed upstream deterministic tools."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from pet_format import STATES

UPSTREAM = Path(__file__).resolve().parents[1]/'third_party/hatch_pet/scripts'

def call(script, *args):
    subprocess.run([sys.executable, str(UPSTREAM/script), *map(str,args)], check=True)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--stable-states', default='jumping',
                   help='Comma-separated states requiring shared-scale/vertical registration')
    args = p.parse_args()
    run = args.run.resolve()
    stable = [s for s in args.stable_states.split(',') if s]
    if any(s not in STATES for s in stable):
        p.error('Unknown state in --stable-states')
    frames = run/'frames'
    call('extract_strip_frames.py','--decoded-dir',run/'decoded',
         '--output-dir',frames,'--states','all','--method','auto')
    manifest_path = frames/'frames-manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if stable:
        call('extract_strip_frames.py','--decoded-dir',run/'decoded','--output-dir',frames,
             '--states',','.join(stable),'--method','stable-slots')
        fixed = json.loads(manifest_path.read_text(encoding='utf-8'))
        replacements = {row['state']:row for row in fixed['rows']}
        manifest['rows'] = [replacements.get(row['state'],row) for row in manifest['rows']]
        manifest_path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    call('inspect_frames.py','--frames-root',frames,'--json-out',run/'qa/review.json',
         '--require-components','--allow-stable-slots')
    call('compose_atlas.py','--frames-root',frames,'--output',run/'final/standard.png',
         '--webp-output',run/'final/standard.webp')
    call('make_contact_sheet.py',run/'final/standard.webp','--output',run/'qa/standard-contact.png')
    call('render_animation_previews.py','--frames-root',frames,'--output-dir',run/'qa/previews')
    print('Intermediate atlas only. Review motion and finish both look rows before packaging v2.')

if __name__ == '__main__':
    main()
