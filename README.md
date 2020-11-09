# AddIMG
A lightweight image processing program written in Python.

**This program is based on [Bottle](https://github.com/bottlepy/bottle) and [Pillow](https://github.com/python-pillow/Pillow) project.**


## Introduction

The main purpose is to process the urls like:

```
https://img.addfn.cn/test.jpg__300x300.png
```

And return a PNG file with 300x300 resolution form original `test.jpg`

See [Deploy](./deploy.md) for more information.

## Features

- Support multiple input formats (Thanks to Pillow).
- Support multiple output formats (jpg, png, bmp and webp)
- Support whitelist mode
- Support to limit max resolution

## License
AddIMG is released under the MIT License. See LICENSE for more information.