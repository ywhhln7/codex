"""Export separate looping H.264 MP4s from an existing v2 pet atlas."""
import argparse
import json
import math
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageColor
import imageio_ffmpeg
from pet_format import STATES, frames_for, open_atlas

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--atlas', type=Path, required=True)
    p.add_argument('--out', type=Path, default=Path('artifacts/videos'))
    p.add_argument('--state', choices=['all', *STATES], default='all')
    p.add_argument('--loops', type=int, default=6)
    p.add_argument('--size', type=int, default=720)
    p.add_argument('--fps', type=int, default=50)
    p.add_argument('--background', default='#FFF6F7')
    args = p.parse_args()
    if args.loops < 1 or args.fps < 1 or args.size < 64 or args.size % 2:
        p.error('loops/fps must be positive; size must be even and >= 64')
    try:
        background = ImageColor.getrgb(args.background)
    except ValueError as exc:
        p.error(str(exc))
    atlas = open_atlas(args.atlas)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    args.out.mkdir(parents=True, exist_ok=True)
    states = list(STATES) if args.state == 'all' else [args.state]

    def export(state):
        encoded = []
        elapsed_ms = 0
        emitted = 0
        for cell, duration in frames_for(atlas, state):
            scale = min(args.size * .74 / 192, args.size * .80 / 208)
            cell = cell.resize((round(192 * scale), round(208 * scale)), Image.Resampling.LANCZOS)
            canvas = Image.new('RGBA', (args.size, args.size), (*background, 255))
            canvas.alpha_composite(cell, ((args.size-cell.width)//2, (args.size-cell.height)//2))
            elapsed_ms += duration
            target = math.floor(elapsed_ms * args.fps / 1000 + .5)
            encoded.append((canvas.convert('RGB').tobytes(), target - emitted))
            emitted = target
        target = args.out / f'{state}.mp4'
        command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y',
                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{args.size}x{args.size}',
                   '-r', str(args.fps), '-i', 'pipe:0', '-an', '-c:v', 'libx264',
                   '-threads', '2', '-preset', 'veryfast', '-crf', '18',
                   '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(target)]
        # File-backed stderr avoids pipe deadlock if the encoder reports many errors.
        log = args.out / f'.{state}.encoder.log'
        with log.open('wb') as errors:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=errors)
            try:
                for _ in range(args.loops):
                    for data, count in encoded:
                        for _ in range(count):
                            process.stdin.write(data)
                process.stdin.close()
                code = process.wait()
            except BaseException:
                process.kill()
                process.wait()
                raise
        if code:
            raise RuntimeError(f'{state}: {log.read_text(errors="replace")}')
        log.unlink()
        return {'state': state, 'file': target.name, 'loops': args.loops,
                'duration_seconds': round(emitted * args.loops / args.fps, 3),
                'size': [args.size, args.size], 'fps': args.fps}

    with ThreadPoolExecutor(max_workers=min(3, len(states))) as pool:
        result = list(pool.map(export, states))
    (args.out / 'manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
