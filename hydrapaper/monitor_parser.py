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

def build_monitors_from_dict(path_to_monitors_xml='{0}{1}'.format(HOME, MONITORS_XML_PATH)):
    """Builds a list of Monitor objects from a logicalmonitor dictionary list
    parsed from ~/.config/monitors.xml"""

    if not isfile(path_to_monitors_xml):
        print('Error: {0} doesn\'t exist!'.format(path_to_monitors_xml))
        return None
    try:
        with open(path_to_monitors_xml) as fd:
            doc = xmltodict.parse(fd.read())
        if doc['monitors']['@version'] == '1': # Really expect version 2 in most cases
            return _monitor_parser_v1(doc)
        if type(json.loads(json.dumps(doc['monitors']['configuration']))) == list:
            lm_list = doc['monitors']['configuration'][-1]['logicalmonitor']
        else:
            lm_list = doc['monitors']['configuration']['logicalmonitor']
        monitors = []
        index = 1
        if type(json.loads(json.dumps(lm_list))) == list: # TODO: find a better way to convert ordered dict to dict or list
            for lm in lm_list:
                monitors.append(Monitor(
                    lm['monitor']['mode']['width'],
                    lm['monitor']['mode']['height'],
                    lm['x'],
                    lm['y'],
                    index,
                    '{0} - {1}'.format(
                        lm['monitor']['monitorspec']['vendor'],
                        lm['monitor']['monitorspec']['connector']
                    ),
                    ('primary' in lm)
                ))
                index += 1
        else:
            monitors.append(Monitor(
                lm_list['monitor']['mode']['width'],
                lm_list['monitor']['mode']['height'],
                lm_list['x'],
                lm_list['y'],
                index,
                '{0} - {1}'.format(
                    lm_list['monitor']['monitorspec']['vendor'],
                    lm_list['monitor']['monitorspec']['connector']
                ),
                ('primary' in lm_list)
            ))
        return monitors
    except Exception as e:
        print('Error: error parsing {0}\n\nException:'.format(
            path_to_monitors_xml
        ))
        import traceback
        traceback.print_exc()
        return None

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
