# __main__.py
#
# Copyright (C) 2017 GabMus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import pathlib
import json

import argparse
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GdkPixbuf

from . import monitor_parser as MonitorParser
from . import wallpaper_merger as WallpaperMerger
from . import threading_helper as ThreadingHelper
from . import listbox_helper as ListboxHelper

import hashlib # for pseudo-random wallpaper name generation

HOME = os.environ.get('HOME')

HYDRAPAPER_CACHE_PATH = '{0}/.cache/hydrapaper'.format(HOME)

IMAGE_EXTENSIONS = [
    '.jpg',
    '.jpeg',
    '.png',
    '.tiff',
    '.svg'
]

class Application(Gtk.Application):
    def __init__(self, **kwargs):
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/ui.glade'
        )
        super().__init__(
            application_id='org.gabmus.hydrapaper',
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.RESOURCE_PATH = '/org/gabmus/hydrapaper/'

        self.CONFIG_FILE_PATH = '{0}/.config/hydrapaper.json'.format(HOME)

        self.configuration = self.get_config_file()

        self.builder.connect_signals(self)

        settings = Gtk.Settings.get_default()
        # settings.set_property("gtk-application-prefer-dark-theme", True)

        self.window = self.builder.get_object('window')

        self.mainBox = self.builder.get_object('mainBox')
        self.apply_button = self.builder.get_object('applyButton')
        self.apply_spinner = self.builder.get_object('applySpinner')

        self.monitors_flowbox = self.builder.get_object('monitorsFlowbox')
        self.wallpapers_flowbox = self.builder.get_object('wallpapersFlowbox')
        self.wallpapers_flowbox_favorites = self.builder.get_object('wallpapersFlowboxFavorites')

        self.wallpaper_selection_mode_toggle = self.builder.get_object('wallpaperSelectionModeToggle')

        self.wallpaper_selection_mode_toggle.set_active(
            not self.configuration['selection_mode'] == 'single'
        )

        self.add_to_favorites_toggle = self.builder.get_object('addToFavoritesButton')

        self.wallpapers_flowbox_favorites.set_activate_on_single_click(
            self.configuration['selection_mode'] == 'single'
        )
        self.wallpapers_flowbox.set_activate_on_single_click(
            self.configuration['selection_mode'] == 'single'
        )

        self.selected_wallpaper_path_entry = self.builder.get_object('selectedWallpaperPathEntry')

        self.wallpapers_flowbox_itemoptions_popover = self.builder.get_object('wallpapersFlowboxItemoptionsPopover')

        # handle longpress gesture for wallpapers_flowbox
        self.wallpapers_flowbox_longpress_gesture = Gtk.GestureLongPress.new(self.wallpapers_flowbox)
        self.wallpapers_flowbox_longpress_gesture.set_propagation_phase(Gtk.PropagationPhase.TARGET)
        self.wallpapers_flowbox_longpress_gesture.set_touch_only(False)
        self.wallpapers_flowbox_longpress_gesture.connect("pressed", self.on_wallpapersFlowbox_rightclick_or_longpress, self.wallpapers_flowbox)

        self.wallpapers_flowbox_favorites_longpress_gesture = Gtk.GestureLongPress.new(self.wallpapers_flowbox_favorites)
        self.wallpapers_flowbox_favorites_longpress_gesture.set_propagation_phase(Gtk.PropagationPhase.TARGET)
        self.wallpapers_flowbox_favorites_longpress_gesture.set_touch_only(False)
        self.wallpapers_flowbox_favorites_longpress_gesture.connect("pressed", self.on_wallpapersFlowbox_rightclick_or_longpress, self.wallpapers_flowbox_favorites)

        self.errorDialog = Gtk.MessageDialog()
        self.errorDialog.add_button('Ok', 0)
        self.errorDialog.set_default_response(0)
        self.errorDialog.set_transient_for(self.window)

        self.favorites_box = self.builder.get_object('favoritesBox')

        self.child_at_pos = None
        # This is a list of Monitor objects
        self.monitors = MonitorParser.build_monitors_from_dict()
        if not self.monitors:
            self.errorDialog.set_markup(
                '''
<b>Oh noes! 😱</b>

There was an error parsing your monitors.xml file.
That\'s really unfortunate 😿.
Try going to your GNOME display settings, changing your resolution or monitor arrangement, and changing it back to normal.

Then come back here. If it still doesn\'t work, considering filling an issue <a href="https://github.com/gabmus/hydrapaper/issues">on HydraPaper\'s bugtracker</a>, including the output of `cat ~/.config/monitors.xml`
                '''
            )
            self.errorDialog.run()
            exit(1)
        self.sync_monitors_from_config()
        self.wallpapers_list = []

        self.wallpapers_folders_toggle = self.builder.get_object('wallpapersFoldersToggle')
        self.wallpapers_folders_popover = self.builder.get_object('wallpapersFoldersPopover')
        self.wallpapers_folders_popover_listbox = self.builder.get_object('wallpapersFoldersPopoverListbox')

    def sync_monitors_from_config(self):
        for m in self.monitors:
            if m.name in self.configuration['monitors'].keys():
                m.wallpaper = self.configuration['monitors'][m.name]
            else:
                self.configuration['monitors'][m.name] = m.wallpaper
        self.save_config_file(self.configuration)

    def dump_monitors_to_config(self):
        for m in self.monitors:
            if m.name in self.configuration['monitors'].keys():
                self.configuration['monitors'][m.name] = m.wallpaper
        self.save_config_file(self.configuration)

    def save_config_file(self, n_config=None):
        if not n_config:
            n_config = self.configuration
        with open(self.CONFIG_FILE_PATH, 'w') as fd:
            fd.write(json.dumps(n_config))
            fd.close()

    def get_config_file(self):
        if not os.path.isfile(self.CONFIG_FILE_PATH):
            n_config = {
                'wallpapers_paths': [
                    '{0}/Pictures'.format(HOME),
                    '/usr/share/backgrounds/gnome/'
                ],
                'selection_mode': 'single',
                'monitors': {},
                'favorites': []
            }
            self.save_config_file(n_config)
            return n_config
        else:
            with open(self.CONFIG_FILE_PATH, 'r') as fd:
                config = json.loads(fd.read())
                fd.close()
                if not 'wallpapers_paths' in config.keys():
                    config['wallpapers_paths'] = [
                        '{0}/Pictures'.format(HOME),
                        '/usr/share/backgrounds/gnome/'
                    ]
                    self.save_config_file(config)
                if not 'selection_mode' in config.keys():
                    config['selection_mode'] = 'single'
                    self.save_config_file(config)
                if not 'monitors' in config.keys():
                    config['monitors'] = {}
                    self.save_config_file(config)
                if not 'favorites' in config.keys():
                    config['favorites'] = []
                    self.save_config_file(config)
                return config

    def remove_wallpaper_folder(self, btn):
        # btn.value contains the path to remove
        self.configuration['wallpapers_paths'].pop(
            self.configuration['wallpapers_paths'].index(btn.value)
        )
        self.save_config_file()
        self.fill_wallpapers_folders_popover_listbox()
        self.refresh_wallpapers_flowbox()

    def fill_wallpapers_folders_popover_listbox(self):
        ListboxHelper.empty_listbox(self.wallpapers_folders_popover_listbox)
        for path in self.configuration['wallpapers_paths']:
            self.wallpapers_folders_popover_listbox.add(
                ListboxHelper.make_label_button_row(
                    path,
                    'Remove',
                    self.remove_wallpaper_folder)
            )
        self.wallpapers_folders_popover_listbox.show_all()

    def set_monitor_wallpaper_preview(self, wp_path):
        monitor_widgets = self.monitors_flowbox.get_selected_children()[0].get_children()[0].get_children()
        for w in monitor_widgets:
            if type(w) == Gtk.Image:
                m_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(wp_path, 64, 64, True)
                w.set_from_pixbuf(m_pixbuf)
            elif type(w) == Gtk.Label:
                current_m_name = w.get_text()
                for m in self.monitors:
                    if m.name == current_m_name:
                        m.wallpaper = wp_path

    def make_monitors_flowbox_item(self, monitor):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label()
        label.set_text(monitor.name)
        image = Gtk.Image()
        if monitor.wallpaper:
            m_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(monitor.wallpaper, 64, 64, True)
            image.set_from_pixbuf(m_pixbuf)
        else:
            image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
        box.pack_start(image, False, False, 0)
        box.pack_start(label, False, False, 0)
        box.set_margin_left(24)
        box.set_margin_right(24)
        return box

    def make_wallpaper_pixbuf(self, wp_path, return_pixbuf_pointer=-1):
        wp_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(wp_path, 250, 250, True)
        if type(return_pixbuf_pointer) == list:
            return_pixbuf_pointer.append(wp_pixbuf)
        return wp_pixbuf

    def make_wallpapers_flowbox_item(self, wp_path):
        pixbuf_fake_list=[]
        pixbuf_thread = ThreadingHelper.do_async(
            self.make_wallpaper_pixbuf,
            (wp_path, pixbuf_fake_list)
        )
        ThreadingHelper.wait_for_thread(pixbuf_thread)
        if len(pixbuf_fake_list) == 1:
            wp_pixbuf = pixbuf_fake_list[0]
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            image = Gtk.Image.new_from_pixbuf(wp_pixbuf)
            box.pack_start(image, False, False, 0)
            box.set_margin_left(12)
            box.set_margin_right(12)
            box.wallpaper_path = wp_path
            return box

    def fill_monitors_flowbox(self):
        for m in self.monitors:
            self.monitors_flowbox.insert(
                self.make_monitors_flowbox_item(m),
            -1) # -1 appends to the end

    def fill_wallpapers_flowbox(self):
        for w in self.wallpapers_list:
            widget = self.make_wallpapers_flowbox_item(w)
            self.wallpapers_flowbox.insert(
                widget,
            -1) # -1 appends to the end
            # widget.show_all()

    def fill_wallpapers_flowbox_async(self):
        for w in self.wallpapers_list:
            if w in self.configuration['favorites']:
                target_wallpapers_flowbox = self.wallpapers_flowbox_favorites
            else:
                target_wallpapers_flowbox = self.wallpapers_flowbox
            widget = self.make_wallpapers_flowbox_item(w)
            target_wallpapers_flowbox.insert(widget, -1) # -1 appends to the end
            widget.show_all()
            target_wallpapers_flowbox.show_all()

    def check_if_image(self, pic):
        path = pathlib.Path(pic)
        return (
            path.suffix.lower() in IMAGE_EXTENSIONS and
            path.exists() and
            not path.is_dir()
        )

    def get_wallpapers_list(self, *args):
        for path in self.configuration['wallpapers_paths']:
            if os.path.isdir(path):
                pictures = os.listdir(path)
                for pic in pictures:
                    picpath = '{0}/{1}'.format(path, pic)
                    if not self.check_if_image(picpath):
                        pictures.pop(pictures.index(pic))
                self.wallpapers_list.extend(['{0}/'.format(path) + pic for pic in pictures])

    def init_wallpapers(self, nothing): # Threading wants args to be passed to the function. I will pass something unimportant
        self.get_wallpapers_list()
        self.fill_wallpapers_flowbox()

    def empty_wallpapers_flowbox(self):
        self.wallpapers_list = []
        while True:
            item = self.wallpapers_flowbox.get_child_at_index(0)
            if item:
                self.wallpapers_flowbox.remove(item)
                item.destroy()
            else:
                break
        while True:
            item = self.wallpapers_flowbox_favorites.get_child_at_index(0)
            if item:
                self.wallpapers_flowbox_favorites.remove(item)
                item.destroy()
            else:
                break

    def refresh_wallpapers_flowbox(self):
        self.empty_wallpapers_flowbox()
        if len(self.configuration['favorites']) == 0:
            self.favorites_box.hide()
        else:
            self.favorites_box.show_all()
        get_wallpapers_thread = ThreadingHelper.do_async(self.get_wallpapers_list, (0,))
        ThreadingHelper.wait_for_thread(get_wallpapers_thread)
        self.fill_wallpapers_flowbox_async()

    def do_activate(self):
        self.add_window(self.window)
        self.window.set_wmclass('HydraPaper', 'HydraPaper')
        self.window.set_title('HydraPaper')

        appMenu = Gio.Menu()
        appMenu.append("About", "app.about")
        appMenu.append("Settings", "app.settings")
        appMenu.append("Quit", "app.quit")

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_activate)
        self.builder.get_object("aboutdialog").connect(
            "delete-event", lambda *_:
                self.builder.get_object("aboutdialog").hide() or True
        )
        self.add_action(about_action)

        settings_action = Gio.SimpleAction.new("settings", None)
        settings_action.connect("activate", self.on_settings_activate)
        self.builder.get_object("settingsWindow").connect(
            "delete-event", lambda *_:
                self.builder.get_object("settingsWindow").hide() or True
        )
        self.add_action(settings_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_activate)
        self.add_action(quit_action)
        self.set_app_menu(appMenu)

        self.fill_monitors_flowbox()
        self.fill_wallpapers_folders_popover_listbox()

        self.window.show_all()

        self.refresh_wallpapers_flowbox()

    def do_command_line(self, args):
        """
        GTK.Application command line handler
        called if Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        must call the self.do_activate() to get the application up and running.
        """
        Gtk.Application.do_command_line(self, args)  # call the default commandline handler
        # make a command line parser
        parser = argparse.ArgumentParser(prog='gui')
        # add a -c/--color option
        parser.add_argument('-q', '--quit-after-init', dest='quit_after_init', action='store_true', help='initialize application (e.g. for macros initialization on system startup) and quit')
        # parse the command line stored in args, but skip the first element (the filename)
        self.args = parser.parse_args(args.get_arguments()[1:])
        # call the main program do_activate() to start up the app
        self.do_activate()
        return 0

    def on_about_activate(self, *args):
        self.builder.get_object("aboutdialog").show()

    def on_settings_activate(self, *args):
        self.builder.get_object("settingsWindow").show()

    def on_quit_activate(self, *args):
        self.quit()

    def onDeleteWindow(self, *args):
        self.quit()

    # Handler functions START

    def on_wallpapersFlowbox_rightclick_or_longpress(self, gesture_or_event, x, y, flowbox):
        self.child_at_pos = flowbox.get_child_at_pos(x,y)
        if not self.child_at_pos:
            return
        self.wallpapers_flowbox_itemoptions_popover.set_relative_to(self.child_at_pos.get_child())
        flowbox.select_child(self.child_at_pos)
        if flowbox == self.wallpapers_flowbox:
            self.add_to_favorites_toggle.set_label('❤ Add to favorites')
        else:
            self.add_to_favorites_toggle.set_label('💔 Remove from favorites')
        wp_path = self.child_at_pos.get_child().wallpaper_path
        self.selected_wallpaper_path_entry.set_text(wp_path)
        self.builder.get_object('selectedWallpaperName').set_text(pathlib.Path(wp_path).name)
        self.on_wallpapersFlowbox_child_activated(flowbox, self.child_at_pos)
        self.wallpapers_flowbox_itemoptions_popover.popup()

    def on_wallpapersFlowbox_button_release_event(self, flowbox, event):
        if event.button == 3: # 3 is the right mouse button
            self.on_wallpapersFlowbox_rightclick_or_longpress(
                event,
                event.x,
                event.y,
                flowbox
            )

    def on_aboutdialog_close(self, *args):
        self.builder.get_object("aboutdialog").hide()

    def on_wallpapersFlowbox_child_activated(self, flowbox, selected_item):
        self.set_monitor_wallpaper_preview(
            selected_item.get_child().wallpaper_path
        )

    def apply_button_async_handler(self, monitors):
        if len(monitors) == 1:
            WallpaperMerger.set_wallpaper(monitors[0].wallpaper, 'zoom')
            return
        #if len(self.monitors) != 2:
        #    print('Configurations different from 2 monitors are not supported for now :(')
        #    exit(1)
        if not os.path.isdir(HYDRAPAPER_CACHE_PATH):
            os.mkdir(HYDRAPAPER_CACHE_PATH)
        new_wp_filename = '_'.join(([m.wallpaper for m in monitors]))
        saved_wp_path = '{0}/{1}.png'.format(HYDRAPAPER_CACHE_PATH, hashlib.sha256(
            'HydraPaper{0}'.format(new_wp_filename).encode()
        ).hexdigest())
        if not os.path.isfile(saved_wp_path):
            WallpaperMerger.multi_setup_pillow(
                monitors,
                saved_wp_path
            )
        else:
            print(
                'Hit cache for wallpaper {0}. Skipping merge operation.'.format(
                    saved_wp_path
                )
            )
        WallpaperMerger.set_wallpaper(saved_wp_path)

    def on_addToFavoritesToggle_clicked(self, button):
        print('asking to popdown')
        self.wallpapers_flowbox_itemoptions_popover.popdown()
        print('popped down popover')
        self.wallpapers_flowbox_itemoptions_popover.set_relative_to(self.wallpapers_flowbox)
        print('changed popover relative')
        if not self.child_at_pos:
            return
        wp_path = self.child_at_pos.get_child().wallpaper_path
        if 'add' in button.get_label().lower():
            self.configuration['favorites'].append(wp_path)
        else:
            self.configuration['favorites'].pop(self.configuration['favorites'].index(wp_path))
        self.save_config_file()
        self.refresh_wallpapers_flowbox()

    def on_applyButton_clicked(self, btn):
        for m in self.monitors:
            if not m.wallpaper:
                print('Set all of the wallpapers before applying')
                self.errorDialog.set_markup('Set all of the wallpapers before applying')
                self.errorDialog.run()
                self.errorDialog.hide()
                return
        # disable interaction
        self.apply_button.set_sensitive(False)
        self.monitors_flowbox.set_sensitive(False)
        self.wallpapers_flowbox.set_sensitive(False)
        # activate spinner
        self.apply_spinner.start()
        # run thread
        thread = ThreadingHelper.do_async(self.apply_button_async_handler, (self.monitors[:],))
        # wait for thread to finish
        ThreadingHelper.wait_for_thread(thread)
        # restore interaction and deactivate spinner
        self.apply_button.set_sensitive(True)
        self.monitors_flowbox.set_sensitive(True)
        self.wallpapers_flowbox.set_sensitive(True)
        self.apply_spinner.stop()
        self.dump_monitors_to_config()

    def on_wallpapersFoldersToggle_toggled(self, toggle):
        if toggle.get_active():
            self.wallpapers_folders_popover.popup()
        else:
            self.wallpapers_folders_popover.popdown()

    def on_wallpapersFoldersPopover_closed(self, popover):
        self.wallpapers_folders_toggle.set_active(False)

    def on_newWallpapersFolderFileChooserButton_file_set(self, filechooser_btn):
        self.configuration['wallpapers_paths'].append(filechooser_btn.get_filename())
        self.save_config_file()
        filechooser_btn.unselect_all()
        self.fill_wallpapers_folders_popover_listbox()
        self.refresh_wallpapers_flowbox()

    def on_wallpaperSelectionModeToggle_state_set(self, switch, doubleclick_activate):
        if doubleclick_activate:
            self.configuration['selection_mode'] = 'double'
        else:
            self.configuration['selection_mode'] = 'single'
        self.wallpapers_flowbox.set_activate_on_single_click(not doubleclick_activate)
        self.wallpapers_flowbox_favorites.set_activate_on_single_click(not doubleclick_activate)
        self.save_config_file(self.configuration)

    # Handler functions END


def main():
    application = Application()

    try:
        ret = application.run(sys.argv)
    except SystemExit as e:
        ret = e.code

    sys.exit(ret)


if __name__ == '__main__':
    main()
