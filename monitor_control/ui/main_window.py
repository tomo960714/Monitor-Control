from __future__ import annotations

import logging
from typing import Dict, Optional

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GLib

from monitor_control.services import discovery, brightness, power
from monitor_control.core.errors import DDCError

log = logging.getLogger(__name__)

class MainWindow(Adw.ApplicationWindow):
    """
    Simple Ui:
    - Enumerate windows
    - Brightness slider
    - Power toggle
    """
    def __init__(self, application: Adw.Application) -> None:
        super().__init__(application=application)
        self.set_title("Monitor Control")
        self.set_default_size(760,520)

        self._debounce_handles: Dict[int, int] = {}  # display -> GLib source id

        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Monitor Control"))
        self.set_titlebar(header)

        self._status = Gtkk.Label(label="")
        self._status.set_xalign(0)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", self._on_refresh_clicked)
        header.pack_end(refresh_btn)

        # main layout
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        outer.set_margin_top(12)
        outer.set_margin_bottom(12)
        outer.set_margin_start(12)
        outer.set_margin_end(12)

        self._list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        outer.append(self._list_box)
        outer.append(Adw.Separator())
        outer.append(self._status)

        scroller = Gtk.ScrolledWindow()
        scroller.set_child(outer)

        self.set_content(scroller)

        # initial load
        self._rebuild_monitor_list()
    
    def _set_status(self, message: str) -> None:
        self._status.set_label(message)
    
    def _on_refresh_clicked(self, _button: Gtk.Button) -> None:
        self._rebuild_monitor_list()

    def _rebuild_monitor_lsit(self) -> None:

        #clear exitin widgets
        child = self._list_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self._list_box.remove(child)
            child = next_child
        
        try:
            monitors = discovery.list_monitors()
        except Exception as e:
            log.exception("Failed to list monitors")
            self._set_status(f"Error detecting monitors: {str(e)}")
            return
        
        if not monitors:
            self._set_status("No monitors detected. Check DDC/CI + permissions.")
            return
        
        self._set_status(f"Detected {len(monitors)} monitor(s).")

        for mon in monitors:
            card = self._build_monitor_card(mon.display, mon.model, mon.mfg, mon.i2c_bus)
            self._list_box.append(card)

    def _build_monitor_card(self, display: int, model: str, mfg: str, bus: int) -> Gtk.Widget:

        title = f"Display {display}: {mfg} {model} (bus /dev/i2c-{bus})"

        group = Adw.PreferenceGroup(title=title)

        row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=9)
        row_box.set_margin_top(8)
        row_box.set_margin_bottom(8)
        row_box.set_margin_start(8)
        row_box.set_margin_end(8)

        # brightness row
        brightness_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        brightness_label = Gtk.Label(label="Brightness")
        brightness_label.set_xalign(0)
        brightness_label.set_hexpand(True)

        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_hexpand(True)
        slider.set_draw_value(True)

        #Load current brightness
        try:
            cur, mx = brightness.get_brightness(display=display)
            slider.set_range(0, mx if mx > 0 else 100)
            slider.set_value(cur)
        except DDCError as e:
            log.warning(f"Failed to get brightness for display {display}: {str(e)}")
            slider.set_sensitive(False)

        slider.connect("value-changed", self._on_brightness_changed, display)

        brightness_row.append(brightness_label)
        brightness_row.append(slider)

        # power toggle row
        power_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        power_label = Gtk.Label(label="Power toggle")
        power_label.set_xalign(0)
        power_label.set_hexpand(True)

        on_btn = Gtk.Button(label="On")
        off_btn = Gtk.Button(label="Off")

        on_btn.connect("clicked",self._on_power_on, display)
        off_btn.connect("clicked",self._on_power_off, display)

        power_row.append(power_label)
        power_row.append(on_btn)
        power_row.append(off_btn)

        row_box.append(brightness_row)
        row_box.append(power_row)

        # wrap in a container
        row = Adw.ActionRow()
        row.set_title("Controls")
        row.set_subtitle("Brightness and power")
        row.add_suffix(row_box)
        row.set_activatable(False)

        group.add(row)
        return group
    
    def _on_power_on(self,_btn: Gtk.Button, display: int) -> None:
        
        try:
            power.power_on(display=display)
            self._set_status(f"Powered on display {display}.")
        except Exception as e:
            log.exception(f"Failed to power on display {display}")
            self._set_status(f"Display {display}: Failed to power on: {str(e)}")

    def _on_power_off(self,_btn: Gtk.Button, display: int) -> None:
        try:
            power.power_off(display=display)
            self._set_status(f"Powered off display {display}.")
        except Exception as e:
            log.exception(f"Failed to power off display {display}")
            self._set_status(f"Display {display}: Failed to power off: {str(e)}")
    
    def _on_brightness_changed(self, slider: Gtk.Scale, display: int) -> None:

        # Debounce rapid slider changes
        value = int(slider.get_value())

        # cancel pending change if exists
        if display in self._debounce_handles:
            GLib.source_remove(self._debounce_handles[display])
            del self._debounce_handles[display]

        def apply_value() -> bool:
            try:
                brightness.set_brightness(value, display=display)
                self._set_status(f"Set brightness of display {display} to {value}.")
            except Exception as e:
                log.exception(f"Failed to set brightness for display {display}")
                self._set_status(f"Display {display}: Failed to set brightness: {str(e)}")
            finally:
                self._debounce_handles.pop(display, None)  # clean up handle
            return False  # one-shot timer
        
        handle = GLib.timeout_add(150, apply_value)
        self._debounce_handles[display] = handle
        
            



