import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GdkPixbuf
from . import threading_helper as ThreadingHelper
from . import wallpaper_flowbox_item as WallpaperFlowboxItem

class WallpaperGallery(Gtk.Window):

    def __init__(self, monitor, wallpapers, *args, **kwds):
        super().__init__(*args, **kwds)

        #self.set_no_show_all(True)

        self.monitor = monitor
        self.wallpapers = wallpapers

        self.mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.buttonbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # window specs
        self.set_title('HydraPaper Gallery')
        self.set_default_size(self.monitor.width, 200)
        #self.set_resizable(False)
        self.set_gravity(Gdk.Gravity.SOUTH_WEST)
        self.set_decorated(False)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.NEVER
        )
        self.viewport = Gtk.Viewport()
        self.scrolled_window.add(self.viewport)

        self.flowbox = Gtk.FlowBox(orientation=Gtk.Orientation.HORIZONTAL)
        self.flowbox.set_max_children_per_line(9999) # maybe unnecessary

        for wp in self.wallpapers:
            print(wp)
            fbitem = WallpaperFlowboxItem.WallpaperBox(wp)
            fbitem.set_wallpaper_thumb()
            self.flowbox.insert(
                fbitem,
                -1
            )
            fbitem.show()

        self.viewport.add(self.flowbox)

        #self.buttonbox.add()

        #self.mainbox.pack_start(self.buttonbox, False, False, 0)
        self.mainbox.pack_start(self.scrolled_window, True, True, 0)
        self.add(self.mainbox)


        # def show(self, *args):
        #     super().show(*args)
        #     self.mainbox.show_all()

    def re_resize(self):
        self.resize(self.monitor.width, 200)
