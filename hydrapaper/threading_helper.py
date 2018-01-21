import threading
from gi.repository import Gtk

def do_async(function, args): # args must be tuple
    t = threading.Thread(
        group = None,
        target = function,
        name = None,
        args = args
    )
    t.start()
    return t

def wait_for_thread(thread):
    while thread.is_alive():
        while Gtk.events_pending():
            Gtk.main_iteration()
    return
