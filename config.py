IMG_ROOT = 'images'

IMG_URL = ''

WHITELIST_MODE = False

WHITELIST = (
    (300, 300),
    (600, 600)
)

MAX_SIZE = 1000*1000

QUALITY = {
    'bmp': None,
    'png': {'compress_level': 6},
    'jpg': {'quality': 75},
    'webp': {'lossless': False, 'quality': 80}
}
