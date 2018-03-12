from gi.repository import Gio
from PIL import Image
from PIL.ImageOps import fit

TMP_DIR='/tmp/HydraPaper/'

def multi_setup_pillow(monitors, save_path, wp_setter_func=None):
    # detect if setup is vertical or horizontal

    images = list(map(Image.open, [m.wallpaper for m in monitors]))
    highest_scaling = max([m.scaling for m in monitors])
    # resolutions = [(m.width, m.height) for m in monitors]
    # widths, heights = [r[0] for r in resolutions], [r[1] for r in resolutions]
    # offsets = [(m.offset_x, m.offset_y) for m in monitors]
    # offsets_x, offsets_y = [o[0] for o in offsets], [o[1] for o in offsets]

    resolutions = []
    widths = []
    heights = []
    offsets = []
    offsets_x = []
    offsets_y = []
    for m in monitors:
        if m.scaling == highest_scaling:
            resolutions.append((m.width, m.height))
            widths.append(m.width)
            heights.append(m.height)
            offsets.append((m.offset_x, m.offset_y))
            offsets_x.append(m.offset_x)
            offsets_y.append(m.offset_y)
        else:
            resolutions.append((m.width*highest_scaling, m.height*highest_scaling))
            widths.append(m.width*highest_scaling)
            heights.append(m.height*highest_scaling)
            offsets.append((m.offset_x*highest_scaling, m.offset_y*highest_scaling))
            offsets_x.append(m.offset_x*highest_scaling)
            offsets_y.append(m.offset_y*highest_scaling)

    # calculate new wallpaper size

    zero_offset_width = 0
    zero_offset_height = 0
    for m in monitors:
        if m.offset_x == 0:
            zero_offset_width = m.width
        if m.offset_y == 0:
            zero_offset_height = m.height
#         # DEBUG
#         print('''
# ________________________________
# | Name: {0}
# | Resolution: {1} x {2}
# | Offset: {3}, {4}
# |_______________________________
# '''.format(m.name, m.width, m.height, m.offset_x, m.offset_y))

    final_image_width = 0
    for i, offx in enumerate(offsets_x):
        if offx == max(offsets_x):
            if offx < zero_offset_width:
                final_image_width = max(widths)
                break
            final_image_width = offx + widths[i]
            break

    final_image_height = 0
    for i, offy in enumerate(offsets_y):
        if offy == max(offsets_y):
            if offy < zero_offset_height:
                final_image_height = max(heights)
                break
            final_image_height = offy + heights[i]
            break

#    # DEBUG
#    print('Final Size: {} x {}'.format(final_image_width, final_image_height))

    n_images = []
    for i, r in zip(images, resolutions):
        n_images.append(fit(i, r, method=Image.LANCZOS))
    final_image = Image.new('RGB', (final_image_width, final_image_height))
    for i, o in zip(n_images, offsets):
        final_image.paste(i, o)
    final_image.save(save_path)

def set_wallpaper_gnome(path, wp_mode='spanned'):
    gsettings = Gio.Settings.new('org.gnome.desktop.background')
    wp_key = 'picture-uri'
    mode_key = 'picture-options'
    gsettings.set_string(wp_key, 'file://{}'.format(path))
    gsettings.set_string(mode_key, wp_mode)

def set_wallpaper_mate(path, wp_mode='spanned'):
    gsettings = Gio.Settings.new('org.mate.background')
    wp_key = 'picture-filename'
    mode_key = 'picture-options'
    gsettings.set_string(wp_key, path)
    gsettings.set_string(mode_key, wp_mode)
