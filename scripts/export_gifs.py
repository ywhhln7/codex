"""Export exact-timing transparent GIF previews from an existing atlas."""
import argparse
from pathlib import Path
from pet_format import STATES, frames_for, open_atlas

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--atlas', type=Path, required=True)
    p.add_argument('--out', type=Path, default=Path('artifacts/gifs'))
    args = p.parse_args()
    atlas = open_atlas(args.atlas)
    args.out.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        pairs = frames_for(atlas, state)
        images, durations = zip(*pairs)
        images[0].save(args.out / f'{state}.gif', save_all=True,
                       append_images=list(images[1:]), duration=list(durations),
                       loop=0, disposal=2, optimize=False)
    print(f'Exported {len(STATES)} GIFs to {args.out}')

if __name__ == '__main__':
    main()
