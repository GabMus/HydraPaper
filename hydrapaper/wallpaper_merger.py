from wand.image import Image
from gi.repository import Gio

def multi_setup_standalone(w1, h1, w2, h2, wp1, wp2, offx1, offy1, offx2, offy2, save_path):
    with Image(filename = wp1) as img1:
        with Image(filename = wp2) as img2:
            img1.transform(resize = '{0}x{1}^'.format(w1, h1))
            img1.crop(width = w1, height = h1, gravity = 'center')
            img2.transform(resize = '{0}x{1}^'.format(w2, h2))
            img2.crop(width = w2, height = h2, gravity = 'center')
            with Image() as n_img:
                n_width = img1.width+img2.width
                n_height = img1.height if img1.height>img2.height else img2.height
                n_img.blank(n_width, n_height)
                n_img.composite(left = offx1, top = offy1, image = img1)
                n_img.composite(left = offx2, top = offy2, image = img2)
                n_img.save(filename = save_path)

def set_wallpaper(path):
    gsettings = Gio.Settings.new('org.gnome.desktop.background')
    wp_key = 'picture-uri'
    mode_key = 'picture-options'
    mode_value = 'spanned'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, mode_value)
