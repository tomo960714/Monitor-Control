from __future__ import annotations
from typing import List, Optional

from monitor_control.core import ddcutil
from monitor_control.core.models import Monitor

def list_monitors() -> List[Monitor]:
    """List all connected monitors."""
    return ddcutil.detect()

def find_monitor(display: Optional[int] = None, bus: Optional[int] = None) -> Monitor:
    """Find a monitor by display number or bus number."""
    monitors = list_monitors()
    if display is not None:
        for m in monitors:
            if m.display == display:
                return m
        raise ValueError(f"No monitor found with display number {display}")
    if bus is not None:
        for m in monitors:
            if m.i2c_bus == bus:
                return m
        raise ValueError(f"No monitor found with bus number {bus}")
    raise ValueError("Provide either display or bus number to find a monitor")
