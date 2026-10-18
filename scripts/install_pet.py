"""Stage a local pet package; select it explicitly in the application's picker."""
import argparse
import json
import os
import re
import shutil
from pathlib import Path
from pet_format import open_atlas

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package', type=Path, required=True)
    p.add_argument('--pet-root', type=Path,
                   default=Path(os.environ.get('CODEX_HOME', Path.home()/'.codex'))/'pets')
    args = p.parse_args()
    manifest = json.loads((args.package/'pet.json').read_text(encoding='utf-8-sig'))
    pet_id = manifest.get('id', '')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', pet_id):
        p.error('pet.json id must be a safe lowercase folder slug')
    if manifest.get('spriteVersionNumber') != 2:
        p.error('Only v2 sprite packages are supported')
    relative = Path(manifest.get('spritesheetPath', ''))
    if relative.name != 'spritesheet.webp' or len(relative.parts) != 1:
        p.error('spritesheetPath must be spritesheet.webp')
    source = args.package/relative
    open_atlas(source)
    target = args.pet_root/pet_id
    if target.exists():
        p.error(f'{target} already exists; choose a new id or manage the old package explicitly')
    target.mkdir(parents=True)
    shutil.copy2(source, target/'spritesheet.webp')
    (target/'pet.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Package staged at {target}')
    print('Open Settings > Pets, refresh, then select the new pet.')
    print('This command does not change the active pet or application/account settings.')

if __name__ == '__main__':
    main()
