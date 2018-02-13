import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

class Monitor:

    def __init__(self, width, height, offset_x, offset_y, index, name, primary=False):
        self.width = int(width)
        self.height = int(height)
        self.primary = primary
        self.offset_x = int(offset_x)
        self.offset_y = int(offset_y)
        self.index = index
        self.name = name
        self.wallpaper = None

    def __repr__(self):
        return self.name

def build_monitors_from_gdk():
    monitors = []
    try:
        display = Gdk.Display.get_default()
        num_monitors = display.get_n_monitors()
        for i in range(0, num_monitors):
            monitor = display.get_monitor(i)
            monitor_rect = monitor.get_geometry()
            monitors.append(Monitor(
                monitor_rect.width,
                monitor_rect.height,
                monitor_rect.x,
                monitor_rect.y,
                i,
                'Monitor {0} ({1})'.format(
                    i,
                    monitor.get_model()
                ),
                monitor.is_primary()
            ))
    except Exception as e:
        print('Error: error parsing monitors (Gdk)')
        import traceback
        traceback.print_exc()
        monitors = None
    return monitors
