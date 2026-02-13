# MonitorControl

A local Linux monitor control utility built on top of `ddcutil`. Overengineered solution to fix my annoyance with status leds.

MonitorControl allows you to control external monitors via DDC/CI directly from:

- A command-line interface (CLI)
- A GTK 4 graphical interface
- A systemd user service (auto power on login / off on logout)

Designed and tested primarily on Fedora (Wayland).

---

## Overview

MonitorControl wraps `ddcutil` and provides:

- Monitor discovery
- Brightness control (VCP 0x10)
- Power control (VCP 0xD6)
- A GTK-based GUI
- Login/logout automation via systemd

The project emphasizes:

- Strict static typing (`mypy --strict`)
- Clean architecture (core / services / UI separation)
- Testable parsing logic
- Hardware isolation via a small `_run()` abstraction

---

## Requirements

### System Requirements

- Linux (tested on Fedora)
- `ddcutil`
- DDC/CI enabled in monitor OSD
- I²C device access for your user

Install system dependency:

```bash
sudo dnf install ddcutil
```


## GTK Requirements

MonitorControl’s GUI uses GTK 4 and runs with the system Python (recommended on Fedora).

Install required system packages:

```bash
sudo dnf install gtk4 libadwaita python3-gobject
```

GTK should **not** be installed via pip inside Conda. Use system packages.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd MonitorControl
```

### 2. Create development environment

```bash
conda env create -f environment.yml
conda activate monitorctl
```

### 3. Install in editable mode

```bash
pip install -e .
```

This ensures the CLI and tests can import the package correctly.

---

## CLI Usage

### List monitors

```bash
monitorctl list
```

### Get brightness

```bash
monitorctl get --display 1
```

### Set brightness

```bash
monitorctl set --display 1 --value 70
```

### Turn monitor off

```bash
monitorctl off --display 1
```

### Turn monitor on

```bash
monitorctl on --display 1
```

> Note: Some monitors do not support power-on from full off state via DDC.

### Toggle power

```bash
monitorctl toggle --display 1
```

---

## GUI Usage

Launch the GTK interface:

```bash
monitorctl gui
```

Or directly:

```bash
python -m monitor_control.ui.app
```

The GUI allows:

- Monitor selection
- Brightness adjustment
- Power control

---

## APC (Automatic Power Control)

MonitorControl provides a **systemd user service** that automatically manages monitor power state based on your desktop session lifecycle.

### Behavior

- Monitors are turned **on** when your user session starts (login).
- Monitors are turned **off** when your user session stops (logout or shutdown).

This is implemented using a **user-level systemd service**, meaning:

- No root privileges required
- Tied directly to your user session
- Works reliably under Wayland (GNOME tested)

---

### Enable Automatic Power Control

Enable the service:

```bash
systemctl --user enable monitor-session.service
```

This will automatically start the service when you log in.

---

### Manual Testing

You can test the behavior without logging out:

Start (simulate login):

```bash
systemctl --user start monitor-session.service
```

Stop (simulate logout):

```bash
systemctl --user stop monitor-session.service
```

---

### Debugging

Check service status:

```bash
systemctl --user status monitor-session.service
```

View logs:

```bash
journalctl --user -u monitor-session.service
```

---

### Notes & Caveats

- Some monitors do **not** support powering on from full hardware-off state via DDC.
- If `ddcutil` reports “Display not found”, the monitor may not yet be initialized at login.
- Behavior depends on monitor firmware DDC/CI implementation.

If powering on does not work, consider using toggle behavior or allowing the monitor to enter standby instead of full power-off.


## Development

### Type Checking

```bash
mypy monitor_control
```

Strict mode is enabled.

### Linting & Formatting

```bash
ruff check . --fix
ruff format .
```

### Testing

Tests mock `ddcutil` calls — no physical monitor required.

```bash
pytest
```

---

## Architecture

```
monitor_control/
    core/         # ddcutil wrapper + parsing logic
    services/     # brightness, power, discovery logic
    ui/           # GTK 4 interface
    config/       # configuration
    cli.py        # Typer CLI entrypoint
```

### Design Principles

- Strict typing (`mypy --strict`)
- Fail-fast parsing
- Clear separation of concerns
- Testable hardware abstraction
- Minimal coupling between UI and core logic

All hardware interaction goes through a small `_run()` wrapper, making parsing fully unit-testable.

---

## Limitations

- Not all monitors support power-on via DDC.
- Internal laptop panels typically do not support DDC.
- Requires DDC/CI support enabled in monitor OSD.
- Wayland behavior may vary depending on system configuration.
