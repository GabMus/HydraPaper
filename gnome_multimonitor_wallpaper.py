#!/usr/bin/env python3

from wand.image import Image
from sys import argv
from gi.repository import Gio

import monitor_parser

if len(argv) < 4:
    print('Usage: {0} left_wallpaper right_wallpaper destination'.format(argv[0]))
    exit(1)

def multi_setup_standalone(w1, h1, w2, h2, wp1, wp2, right_left_offset, right_top_offset, save_path):
    with Image(filename = wp1) as img1:
        with Image(filename = wp2) as img2:
            img1.transform(resize = '{0}x{1}^'.format(w1, h1))
            img1.crop(width = w1, height = h1, gravity = 'center')
            img2.transform(resize = '{0}x{1}^'.format(w2, h2))
            img2.crop(width = w2, height = h2, gravity = 'center')
            if right_top_offset == -1: # this means auto
                right_top_offset = abs(img1.height-img2.height)
            with Image() as n_img:
                n_width = img1.width+img2.width
                n_height = img1.height if img1.height>img2.height else img2.height
                n_img.blank(n_width, n_height)
                n_img.composite(left = 0, top = 0, image = img1)
                n_img.composite(left = right_left_offset, top = right_top_offset, image = img2)
                n_img.save(filename = save_path)

def set_wallpaper(path):
    gsettings = Gio.Settings.new('org.gnome.desktop.background')
    wp_key = 'picture-uri'
    mode_key = 'picture-options'
    mode_value = 'spanned'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, mode_value)

monitors = monitor_parser.build_monitors_from_dict(
    '{0}{1}'.format(
        monitor_parser.HOME,
        monitor_parser.MONITORS_XML_PATH)
)

if len(monitors)!=2:
    print('Configurations different from 2 monitors are not supported for now')
    exit(2)

multi_setup_standalone(
    monitors[0].width,
    monitors[0].height,
    monitors[1].width,
    monitors[1].height,
    argv[1], # wallpaper 1
    argv[2], # wallpaper 2
    monitors[1].offset_x,
    monitors[1].offset_y,
    argv[3] # destination
)

set_wallpaper(argv[3])
