"""Shared sprite geometry and original animation timings (milliseconds)."""
from PIL import Image

CELL_WIDTH, CELL_HEIGHT = 192, 208
ATLAS_SIZE = (1536, 2288)
STATES = {
    'idle': (0, [280, 110, 110, 140, 140, 320]),
    'running-right': (1, [120] * 7 + [220]),
    'running-left': (2, [120] * 7 + [220]),
    'waving': (3, [140, 140, 140, 280]),
    'jumping': (4, [140, 140, 140, 140, 280]),
    'failed': (5, [140] * 7 + [240]),
    'waiting': (6, [150] * 5 + [260]),
    'running': (7, [120] * 5 + [220]),
    'review': (8, [150] * 5 + [280]),
}

def open_atlas(path):
    with Image.open(path) as image:
        if image.size != ATLAS_SIZE:
            raise ValueError(f'Expected v2 atlas {ATLAS_SIZE}, got {image.size}')
        if 'A' not in image.getbands():
            raise ValueError('Atlas must contain an alpha channel')
        return image.convert('RGBA')

def frames_for(atlas, state):
    row, timings = STATES[state]
    return [(atlas.crop((i * CELL_WIDTH, row * CELL_HEIGHT,
                         (i + 1) * CELL_WIDTH, (row + 1) * CELL_HEIGHT)), duration)
            for i, duration in enumerate(timings)]
