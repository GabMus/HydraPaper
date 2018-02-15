import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class WallpapersFolderListBoxRow(Gtk.ListBoxRow):
    def __init__(self, folder_path, folder_active, on_switch_state_set):
        super().__init__()

        self.folder_path = folder_path

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.label = Gtk.Label()
        self.switch = Gtk.Switch()

        self.label.set_text(folder_path)
        self.label.set_margin_left(12)
        self.label.set_margin_right(6)
        self.label.set_halign(Gtk.Align.START)

        self.switch.value = folder_path
        self.switch.set_active(folder_active)
        self.switch.set_margin_left(6)
        self.switch.set_margin_right(12)

        self.switch.connect('state-set', on_switch_state_set)

        self.box.pack_start(self.label, True, True, 0)
        self.box.pack_start(self.switch, False, False, 0)
        self.box.set_margin_top(6)
        self.box.set_margin_bottom(6)

        self.value = folder_path

        self.add(self.box)
