from monitor_control.core import ddcutil

BRIGHTNESS_CODE = "10"


def get_brightness(display: int | None = None, bus: int | None = None) -> tuple[int, int]:
    v = ddcutil.get_vcp(BRIGHTNESS_CODE, display=display, bus=bus)
    return v.current, v.maximum


def set_brightness(
    value: int,
    display: int | None = None,
    bus: int | None = None,
    sleep_multiplier: float | None = 0.2,
) -> None:

    if not (0 <= value <= 100):
        raise ValueError("Brightness value must be between 0 and 100")
    ddcutil.set_vcp(
        BRIGHTNESS_CODE, value, display=display, bus=bus, sleep_multiplier=sleep_multiplier
    )
