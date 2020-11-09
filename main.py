import re
from io import BytesIO
from pathlib import Path

from bottle import default_app, abort, HTTPResponse
from PIL import Image


app = default_app()
app.config.load_module('config', False)

img_root = app.config['IMG_ROOT']
img_url = app.config['IMG_URL']
max_size = app.config['MAX_SIZE']
whitelist_mode = app.config['WHITELIST_MODE']
whitelist = app.config['WHITELIST']
quality = app.config['QUALITY']

rule = re.compile(r'(?P<file>.*)__(?P<width>\d*)x(?P<height>\d*).(?P<suffix>jpg|png|bmp|webp)$')


def index_img(path):
    params = rule.match(path)
    if params is None:
        return abort(400)

    filename, width, height, suffix = params.groups()

    if '..' in filename or '__' in filename:
        return abort(400)

    filepath = Path(filename)
    real_path = img_root / filepath
    if not real_path.is_file() or not real_path.exists():
        return abort(400)

    img = Image.open(real_path)
    img_width = img.width
    img_height = img.height

    if width and height:
        img_width = int(width)
        img_height = int(height)
    elif width and not height:
        width = int(width)
        if width <= 10:
            img_width = img_width * width
            img_height = img_height * width
        else:
            img_height = int(width / img_width * img_height)
            img_width = width
    elif height and not width:
        height = int(height)
        if height <= 10:
            img_width = img_width * height // 10
            img_height = img_height * height // 10
        else:
            img_width = int(height/img_height*img_width)
            img_height = height
    else:
        return abort(400)

    if not img_width or not img_height:
        return abort(400)

    if not whitelist_mode and max_size and img_width*img_height > max_size:
        return abort(400)

    size = (img_width, img_height)
    if whitelist_mode and size not in whitelist:
        abort()

    img_resized = img.resize(size)
    output = BytesIO()
    output_params = quality[suffix]

    output_format = suffix if suffix != 'jpg' else 'jpeg'
    if output_params:
        img_resized.save(output, format=output_format, params=output_params)
    else:
        img_resized.save(output, format=output_format)

    res = HTTPResponse(status=200, body=output.getvalue())
    res.set_header(f'Content-Type', f'image/{suffix}')
    return res


app.route(f'{img_url}/<path:path>', 'GET', index_img)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)