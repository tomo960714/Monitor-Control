from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Monitor:
    display: int                    # ddcutil Display N
    i2c_bus: int                    # I2C bus number, e.g. 3 dor /dev/i2c-4
    model: str = "Unknown"          # Monitor model, e.g. "LG 29UM68-P"
    mfg: str = "Unknown"            # Manufacturer, e.g. "LG"
    serial: Optional[str] = None    # Optional serial number

@dataclass(frozen=True)
class VCPValue:
    code: str                      # VCP code, e.g. "10" for brightness
    current: int
    maximum: int