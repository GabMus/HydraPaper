from os import environ as env
import xmltodict
import json

HOME=env.get('HOME')
MONITORS_XML_PATH='/.config/monitors.xml'

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
    with open(path_to_monitors_xml) as fd:
        doc = xmltodict.parse(fd.read())
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
    if not monitors[0].primary:
        monitors[0], monitors[1] = monitors[1], monitors[0]
    return monitors
