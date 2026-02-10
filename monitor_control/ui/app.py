from __future__ import annotations

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from .main_window import MainWindow

class MonitorControlApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.tomo96.monitorcontrol")

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()

def run()-> None:
    app = MonitorControlApp()
    app.run(None)
    