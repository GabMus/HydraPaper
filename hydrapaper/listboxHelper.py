import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GdkPixbuf

def make_image_row(text, img_path):
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    label = Gtk.Label()
    label.set_text(text)
    icon = Gtk.Image()
    icon.set_from_resource(img_path)
    label.set_margin_left(12)
    label.set_margin_right(12)
    box.pack_start(icon, False, False, 0)
    box.pack_start(label, False, False, 0)
    row = Gtk.ListBoxRow()
    row.add(box)
    return row

def make_row(text):
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    label = Gtk.Label()
    label.set_text(text)
    label.set_margin_left(12)
    label.set_margin_right(12)
    box.set_margin_top(12)
    box.set_margin_bottom(12)
    box.pack_start(label, False, False, 0)
    row = Gtk.ListBoxRow()
    row.add(box)
    return row

def make_2x_row(text1, text2):
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    label1 = Gtk.Label()
    label1.set_text(text1)
    label1.set_margin_left(12)
    label1.set_margin_right(12)

    label2 = Gtk.Label()
    text2_for_label=text2
    if not text2_for_label:
        text2_for_label="Unassigned"
    label2.set_markup("<span color=\"#818181\">"+text2_for_label+"</span>")
    label2.set_margin_left(12)
    label2.set_margin_right(12)

    box.set_margin_top(12)
    box.set_margin_bottom(12)
    label1.set_size_request(200, 0)
    label2.set_size_request(200, 0)
    box.pack_start(label1, True, True, 0)
    box.pack_start(label2, True, False, 0)
    row = Gtk.ListBoxRow()
    row.add(box)
    row.value={'key': text1, 'val': text2}
    return row

def empty_listbox(listbox):
    while True:
        row = listbox.get_row_at_index(0)
        if row:
            listbox.remove(row)
        else:
            break
