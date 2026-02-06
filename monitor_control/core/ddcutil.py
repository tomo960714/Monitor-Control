import logging
import re
import subprocess
from dataclasses import dataclass
from typing import List, Optional

from .errors import DDCCommandError, DDCParseError
from .models import Monitor, VCPValue

log = logging.getLogger(__name__)

@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str
    returncode: int

def _run(cmd: list[str], timeout_s: int = 5) -> RunResult:
    """Run a command and return the result."""
    try:
        p=subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except FileNotFoundError as e:
        raise DDCCommandError("ddcutil not found. Install it (sudo dnf install ddcutil).") from e
    except subprocess.TimeoutExpired as e:
        raise DDCCommandError(f"ddcutil command timed out after {timeout_s} seconds.") from e

    if p.returncode != 0:
        raise DDCCommandError(f"ddcutil command failed with return code {p.returncode}.", stderr=p.stderr)
    
    return RunResult(p.stdout, p.stderr, p.returncode)

def detect() -> List[Monitor]:
    """Parse detected monitors from ddcutil."""

    res = _run(["ddcutil", "detect"], timeout_s=10)
    text = res.stdout

    # Typical blocks:
    # Display 1
    #   I2C bus:  /dev/i2c-6
    #   DRM_connector:           card1-HDMI-A-1
    #   EDID synopsis:
    #       Mfg id:               AUS - UNK
    #       Model:                VZ249
    #       Product code:         9420  (0x24cc)
    #       Serial number:        N5LMRS022713
    #       Binary serial number: 16843009 (0x01010101)
    #       Manufacture year:     2022,  Week: 23
    #   VCP version:         2.1
    monitors: list[Monitor] = []
    
    # Split by "Display N" blocks
    blocks = re.split(r"(?m)^\s*Display\s+(\d+)\s*$", text)
    # re.split returns: [prefix, disp1, block1, disp2, block2, ...]

    # Sanity check on the split result - we expect at least one monitor block (meaning at least 3 blocks: prefix, disp1, block1)
    if len(blocks) < 3:
        return monitors # No monitors detected, return empty list
    
    it = iter(blocks[1:]) # Skip the prefix block
    for disp_str, block in zip(it, it):
        display=int(disp_str)

        bus_match = re.search(r"I2C\s+bus:\s*/dev/i2c-(\d+)", block)
        if not bus_match:
            bus_match = re.search (r"/dev/i2c-(\d+)", block)
        if not bus_match:
            log.warning(f"Could not find I2C bus for display {display}. Skipping.")
            
            raise DDCParseError(f"Could not find I2C bus for display {display}.")
        
        i2c_bus = int(bus_match.group(1))

        mfg = "Unknown"
        model = "Unknown"
        serial = None

        m = re.search(r"Mfg\s+id:\s*([A-Z0-9]{2,4})", block)
        if m:
            mfg = m.group(1).strip()
        
        m = re.search(r"Model:\s*(.+)", block)
        if m:
            model = m.group(1).strip()
        
        m = re.search(r"Serial\s+number:\s*(.+)", block)
        if m:
            serial = m.group(1).strip()
        
        monitors.append(Monitor(display=display, i2c_bus=i2c_bus, mfg=mfg, model=model, serial=serial))

    return monitors

def get_vcp(code: str, display: Optional[int] = None, bus: Optional[int] = None) -> VCPValue:
    cmd = ["ddcutil"]
    cmd += _target_args(display=display, bus=bus)
    cmd += ["getvcp", code]
    res = _run(cmd, timeout_s=5)

    out = res.stdout.strip()
    
    # Numeric format (e.g. brightness):
    # VCP code 0x10 (Brightness): current value =  50, max value = 100
    m = re.search(
        r"current\s+value\s*=\s*(\d+)\s*,\s*max\s+value\s*=\s*(\d+)",
        out,
        re.IGNORECASE,
    )
    if m:
        return VCPValue(code=code.upper(), current=int(m.group(1)), maximum=int(m.group(2)))

    # Status format (commonly for 0xD6):
    # VCP code 0xd6 (Power mode): DPM: On,  DPMS: Off (sl=0x01)
    m = re.search(r"\(sl\s*=\s*0x([0-9a-fA-F]+)\)", out)
    if m:
        current = int(m.group(1), 16)
        return VCPValue(code=code.upper(), current=current, maximum=0)

    raise DDCParseError(f"Could not parse getvcp output for code {code}: {out}")

def set_vcp(code: str, value: int, display: Optional[int] = None, bus: Optional[int] = None, sleep_multiplier: Optional[float] = None) -> None:
    cmd = ["ddcutil"]
    if sleep_multiplier is not None:
        cmd += [f"--sleep-multiplier={sleep_multiplier}"]
    cmd += _target_args(display=display, bus=bus)
    cmd += ["setvcp", code, str(value)]
    _run(cmd, timeout_s=5)

def _target_args(display: Optional[int] = None, bus: Optional[int] = None) -> list[str]:
    if display is not None and bus is not None:
        raise ValueError("Cannot specify both display and bus. They are mutually exclusive ways to target a monitor.")
    if display is not None:
        return [f"--display={str(display)}"]
    if bus is not None:
        return [f"--bus={bus}"]
    return []