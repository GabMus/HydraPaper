from gi.repository import Gio
from os.path import isdir
from os import mkdir
from PIL import Image
from PIL.ImageOps import fit

import hashlib # for pseudo-random wallpaper name generation

TMP_DIR='/tmp/HydraPaper/'

def multi_setup_pillow(monitors, save_path):
    images = list(map(Image.open, [m.wallpaper for m in monitors]))
    resolutions = [(m.width, m.height) for m in monitors]
    widths = [r[0] for r in resolutions]
    heights = [r[1] for r in resolutions]
    offsets = [(m.offset_x, m.offset_y) for m in monitors]
    n_images = []
    for i, r in zip(images, resolutions):
        n_images.append(fit(i, r, method=Image.LANCZOS))
    final_image = Image.new('RGB', (sum(widths), max(heights)))
    for i, o in zip(n_images, offsets):
        final_image.paste(i, o)
    final_image.save(save_path)

def set_wallpaper(path, wp_mode='spanned'):
    gsettings = Gio.Settings.new('org.gnome.desktop.background')
    wp_key = 'picture-uri'
    mode_key = 'picture-options'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, wp_mode)
