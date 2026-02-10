from __future__ import annotations
import sys

import gi
gi.require_version("Gtk", "4.0")

from gi.repository import Gtk
from .main_window import MainWindow


class MonitorControlApp(Gtk.Application):
    def do_activate(self) -> None:
        print("Activating GTK application")
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()

def run()-> None:
    app = MonitorControlApp()
    print("Running GTK application")
    app.run(sys.argv)

if __name__ == "__main__":
    run()
    