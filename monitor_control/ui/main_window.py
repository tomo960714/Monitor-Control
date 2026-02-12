from __future__ import annotations

import logging

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gtk

from monitor_control.services import brightness, discovery, power

log = logging.getLogger(__name__)


class MainWindow(Gtk.ApplicationWindow):
    """
    Simple Ui:
    - Enumerate windows
    - Brightness slider
    - Power toggle
    """

    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        self.set_title("Monitor Control")
        self.set_default_size(760, 520)

        self._debounce_handles: dict[int, int] = {}  # display -> GLib source id

        header = Gtk.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Monitor Control"))
        self.set_titlebar(header)

        self._status = Gtk.Label(label="")
        self._status.set_xalign(0)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", self._on_refresh_clicked)
        header.pack_end(refresh_btn)

        self._list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._list.set_margin_top(12)
        self._list.set_margin_bottom(12)
        self._list.set_margin_start(12)
        self._list.set_margin_end(12)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        outer.append(self._list)
        outer.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        outer.append(self._status)

        scroller = Gtk.ScrolledWindow()
        scroller.set_child(outer)
        self.set_child(scroller)

        self._rebuild_monitor_list()

    def _set_status(self, message: str) -> None:
        self._status.set_label(message)

    def _on_refresh_clicked(self, _button: Gtk.Button) -> None:
        self._rebuild_monitor_list()

    def _clear_monitor_list(self) -> None:
        child = self._list.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self._list.remove(child)
            child = next_child

    def _rebuild_monitor_list(self) -> None:

        self._clear_monitor_list()
        monitors = discovery.list_monitors()
        if not monitors:
            self._set_status("No monitors detected. Check DDC/CI + permissions.")
            return

        self._set_status(f"Detected {len(monitors)} monitor(s).")

        for mon in monitors:
            self._list.append(
                self._build_monitor_card(mon.display, mon.model, mon.mfg, mon.i2c_bus)
            )

    def _build_monitor_card(self, display: int, model: str, mfg: str, bus: int) -> Gtk.Widget:
        frame = Gtk.Frame()
        frame.set_margin_top(6)

        v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        v.set_margin_top(10)
        v.set_margin_bottom(10)
        v.set_margin_start(10)
        v.set_margin_end(10)
        title = Gtk.Label(label=f"Display {display}: {mfg} {model} (bus /dev/i2c-{bus})")
        title.set_xalign(0)
        v.append(title)

        # brightness row
        brightness_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        brightness_label = Gtk.Label(label="Brightness")
        brightness_label.set_xalign(0)
        brightness_label.set_hexpand(True)

        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        slider.set_hexpand(True)
        slider.set_draw_value(True)

        try:
            cur, mx = brightness.get_brightness(display=display)
            slider.set_range(0, mx if mx > 0 else 100)
            slider.set_value(cur)
        except Exception:
            slider.set_sensitive(False)

        slider.connect("value-changed", self._on_brightness_changed, display)

        brightness_row.append(brightness_label)
        brightness_row.append(slider)
        v.append(brightness_row)

        # power toggle row
        power_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        power_label = Gtk.Label(label="Power toggle")
        power_label.set_xalign(0)
        power_label.set_hexpand(True)

        on_btn = Gtk.Button(label="On")
        off_btn = Gtk.Button(label="Off")

        on_btn.connect("clicked", self._on_power_on, display)
        off_btn.connect("clicked", self._on_power_off, display)

        power_row.append(power_label)
        power_row.append(on_btn)
        power_row.append(off_btn)
        v.append(power_row)

        frame.set_child(v)
        return frame

    def _on_power_on(self, _btn: Gtk.Button, display: int) -> None:

        try:
            power.power_on(display=display)
            self._set_status(f"Powered on display {display}.")
        except Exception as e:
            log.exception(f"Failed to power on display {display}")
            self._set_status(f"Display {display}: Failed to power on: {str(e)}")

    def _on_power_off(self, _btn: Gtk.Button, display: int) -> None:
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

        self._debounce_handles[display] = GLib.timeout_add(150, apply_value)
