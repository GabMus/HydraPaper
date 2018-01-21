from wand.image import Image
from gi.repository import Gio

def multi_setup_standalone(m1, m2, save_path):
    with Image(filename = m1.wallpaper) as img1:
        with Image(filename = m2.wallpaper) as img2:
            img1.transform(resize = '{0}x{1}^'.format(m1.width, m1.height))
            img1.crop(width = m1.width, height = m1.height, gravity = 'center')
            img2.transform(resize = '{0}x{1}^'.format(m2.width, m2.height))
            img2.crop(width = m2.width, height = m2.height, gravity = 'center')
            with Image() as n_img:
                n_width = img1.width+img2.width
                n_height = img1.height if img1.height>img2.height else img2.height
                n_img.blank(n_width, n_height)
                n_img.composite(left = m1.offset_x, top = m1.offset_y, image = img1)
                n_img.composite(left = m2.offset_x, top = m2.offset_y, image = img2)
                n_img.save(filename = save_path)

def set_wallpaper(path):
    gsettings = Gio.Settings.new('org.gnome.desktop.background')
    wp_key = 'picture-uri'
    mode_key = 'picture-options'
    mode_value = 'spanned'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, mode_value)
