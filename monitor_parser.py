from os import environ as env
import xmltodict

HOME=env.get('HOME')
MONITORS_XML_PATH='/.config/monitors.xml'

class Monitor:

    def __init__(self, width, height, offset_x, offset_y, primary=False):
        self.width = int(width)
        self.height = int(height)
        self.primary = primary
        if self.primary:
            self.offset_x = 0
            self.offset_y = 0
        self.offset_x = int(offset_x)
        self.offset_y = int(offset_y)

def build_monitors_from_dict(path_to_monitors_xml):
    """Builds a list of Monitor objects from a logicalmonitor dictionary list
    parsed from ~/.config/monitors.xml"""
    with open(path_to_monitors_xml) as fd:
        doc = xmltodict.parse(fd.read())
    lm_list = doc['monitors']['configuration'][1]['logicalmonitor']
    monitors = []
    for lm in lm_list:
        monitors.append(Monitor(
            lm['monitor']['mode']['width'],
            lm['monitor']['mode']['height'],
            lm['x'],
            lm['y'],
            ('primary' in lm)
        ))
    if not monitors[0].primary:
        monitors[0], monitors[1] = monitors[1], monitors[0]
    return monitors
