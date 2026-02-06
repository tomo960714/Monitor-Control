from typing import Optional
from monitor_control.core import ddcutil

POWER_MODE_CODE = "D6"

# Usual DDC power modes:
# 1 = On            # LG doesn't support this after 5
# 4 = off/standby
# 5 = Off 

POWER_ON = 1
POWER_OFF = 5

def get_power_mode(display: Optional[int] = None, bus: Optional[int] = None) -> int:
    v = ddcutil.get_vcp(POWER_MODE_CODE, display=display, bus=bus)
    return v.current

def power_on(display: Optional[int] = None, bus: Optional[int] = None) -> None:
    ddcutil.set_vcp(POWER_MODE_CODE, POWER_ON, display=display, bus=bus)

def power_off(display: Optional[int] = None, bus: Optional[int] = None) -> None:
    ddcutil.set_vcp(POWER_MODE_CODE, POWER_OFF, display=display, bus=bus)

def toggle_power(display: Optional[int] = None, bus: Optional[int] = None) -> str:
    current_mode = get_power_mode(display=display, bus=bus)
    if current_mode == POWER_ON:
        power_off(display=display, bus=bus)
        return "off"
    else:
        power_on(display=display, bus=bus)
        return "on"