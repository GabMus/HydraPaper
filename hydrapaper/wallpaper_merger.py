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

def multi_setup_standalone(m1, m2, save_path):

    return multi_setup_pillow([m1, m2], save_path)

def n_way_setup(monitors_list, save_path):
    return
    #if not isdir(TMP_DIR):
    #    os.mkdir(TMP_DIR)

    # TODO: find the leftmost monitor and make it 0
    # TODO: start from 0 and iterate proceeding with the closest monitor
    saved_wp_path = '{0}/{1}.png'.format(TMP_DIR, hashlib.sha256(
            'HydraPaper{0}{1}'.format(self.monitors[0].wallpaper, self.monitors[1].wallpaper).encode()
        ).hexdigest())

def set_wallpaper(path):
    gsettings = Gio.Settings.new('org.gnome.desktop.background')
    wp_key = 'picture-uri'
    mode_key = 'picture-options'
    mode_value = 'spanned'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, mode_value)
