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

        # This is a list of Monitor objects
        self.monitors = MonitorParser.build_monitors_from_dict()
        self.wallpapers_list = []

        self.wallpapers_folders_toggle = self.builder.get_object('wallpapersFoldersToggle')
        self.wallpapers_folders_popover = self.builder.get_object('wallpapersFoldersPopover')
        self.wallpapers_folders_popover_listbox = self.builder.get_object('wallpapersFoldersPopoverListbox')

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
                ]
            }
            self.save_config_file(n_config)
            return n_config
        else:
            with open(self.CONFIG_FILE_PATH, 'r') as fd:
                config = json.loads(fd.read())
                fd.close()
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
        image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
        box.pack_start(image, False, False, 0)
        box.pack_start(label, False, False, 0)
        box.set_margin_left(24)
        box.set_margin_right(24)
        return box

    def make_wallpapers_flowbox_item(self, wp_path, return_widget_pointer=-1):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        wp_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(wp_path, 250, 250, True)
        image = Gtk.Image.new_from_pixbuf(wp_pixbuf)
        box.pack_start(image, False, False, 0)
        box.set_margin_left(12)
        box.set_margin_right(12)
        box.wallpaper_path = wp_path
        if type(return_widget_pointer) == list:
            return_widget_pointer.append(box)
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
            widget = [] # workaround: passing widget as a list to pass its reference
            widget_thread = ThreadingHelper.do_async(
                self.make_wallpapers_flowbox_item,
                (w, widget)
            )
            ThreadingHelper.wait_for_thread(widget_thread)
            self.wallpapers_flowbox.insert(
                widget[0],
            -1) # -1 appends to the end
            widget[0].show_all()
            self.wallpapers_flowbox.show_all()

    def get_wallpapers_list(self, *args):
        for path in self.configuration['wallpapers_paths']:
            if os.path.isdir(path):
                pictures = os.listdir(path)
                for pic in pictures:
                    if pathlib.Path(pic).suffix.lower() not in IMAGE_EXTENSIONS:
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
            else:
                break

    def refresh_wallpapers_flowbox(self):
        self.empty_wallpapers_flowbox()
        get_wallpapers_thread = ThreadingHelper.do_async(self.get_wallpapers_list, (0,))
        ThreadingHelper.wait_for_thread(get_wallpapers_thread)
        self.fill_wallpapers_flowbox_async()

    def do_activate(self):
        self.add_window(self.window)
        self.window.set_wmclass('HydraPaper', 'HydraPaper')
        self.window.set_title('HydraPaper')

        appMenu = Gio.Menu()
        appMenu.append("About", "app.about")
        appMenu.append("Quit", "app.quit")
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_activate)
        self.builder.get_object("aboutdialog").connect(
            "delete-event", lambda *_:
                self.builder.get_object("aboutdialog").hide() or True
        )
        self.add_action(about_action)
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_activate)
        self.add_action(quit_action)
        self.set_app_menu(appMenu)

        self.fill_monitors_flowbox()
        self.fill_wallpapers_folders_popover_listbox()

        self.window.show_all()

        self.refresh_wallpapers_flowbox()


    def run_startup_async_operations(self):
        init_wp_thread = ThreadingHelper.do_async(self.init_wallpapers, (0,))
        ThreadingHelper.wait_for_thread(init_wp_thread)
        self.wallpapers_flowbox.show_all()

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

    def on_quit_activate(self, *args):
        self.quit()

    def onDeleteWindow(self, *args):
        self.quit()

    # Handler functions START

    def on_aboutdialog_close(self, *args):
        self.builder.get_object("aboutdialog").hide()

    def on_wallpapersFlowbox_child_activated(self, flowbox, selected_item):
        self.set_monitor_wallpaper_preview(
            selected_item.get_child().wallpaper_path
        )

    def apply_button_async_handler(self, btn):
        if len(self.monitors) == 1:
            WallpaperMerger.set_wallpaper(self.monitors[0].wallpaper)
            return
        if len(self.monitors) != 2:
            print('Configurations different from 2 monitors are not supported for now :(')
            exit(1)
        if not (self.monitors[0].wallpaper and self.monitors[1].wallpaper):
            print('Set both wallpapers before applying')
            return
        if not os.path.isdir('{0}/Pictures/HydraPaper'.format(HOME)):
            os.mkdir('{0}/Pictures/HydraPaper'.format(HOME))
        saved_wp_path = '{0}/Pictures/HydraPaper/{1}.png'.format(HOME, hashlib.sha256(
            'HydraPaper{0}{1}'.format(self.monitors[0].wallpaper, self.monitors[1].wallpaper).encode()
        ).hexdigest())
        WallpaperMerger.multi_setup_standalone(
            self.monitors[0],
            self.monitors[1],
            saved_wp_path
        )
        WallpaperMerger.set_wallpaper(saved_wp_path)

    def on_applyButton_clicked(self, btn):
        # disable interaction
        self.apply_button.set_sensitive(False)
        self.monitors_flowbox.set_sensitive(False)
        self.wallpapers_flowbox.set_sensitive(False)
        # activate spinner
        self.apply_spinner.start()
        # run thread
        thread = ThreadingHelper.do_async(self.apply_button_async_handler, (btn,))
        # wait for thread to finish
        ThreadingHelper.wait_for_thread(thread)
        # restore interaction and deactivate spinner
        self.apply_button.set_sensitive(True)
        self.monitors_flowbox.set_sensitive(True)
        self.wallpapers_flowbox.set_sensitive(True)
        self.apply_spinner.stop()

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
