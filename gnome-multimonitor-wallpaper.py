#!/usr/bin/env python3

from wand.image import Image
from sys import argv

from gi.repository import Gio

if len(argv) < 4:
    print('Usage: {0} left_wallpaper right_wallpaper destination'.format(argv[0]))
    exit(1)

def multi_setup_standalone(w1, h1, w2, h2, wp1, wp2, save_path):
    with Image(filename=wp1) as img1:
        with Image(filename=wp2) as img2:
            img1.transform(resize='{0}x{1}^'.format(w1, h1))
            img1.crop(width=w1, height=h1, gravity='center')
            img2.transform(resize='{0}x{1}^'.format(w2, h2))
            img2.crop(width=w2, height=h2, gravity='center')
            right_top_offset=abs(img1.height-img2.height)
            with Image() as n_img:
                n_width=img1.width+img2.width
                n_height=img1.height if img1.height>img2.height else img2.height
                n_img.blank(n_width, n_height)
                n_img.composite(left=0, top=0, image=img1)
                n_img.composite(left=img1.width, top=right_top_offset, image=img2)
                n_img.save(filename=save_path)

def set_wallpaper(path):
    gsettings = Gio.Settings.new('org.gnome.desktop.background')
    wp_key='picture-uri'
    mode_key='picture-options'
    mode_value='spanned'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, mode_value)

multi_setup_standalone(2560, 1440, 1920, 1080, argv[1], argv[2], argv[3])
set_wallpaper(argv[3])
