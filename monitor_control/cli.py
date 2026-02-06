import typer
from rich import print
from rich.table import Table

from monitor_control.utils.logging import setup_logging
from monitor_control.services import discovery,brightness,power

app = typer.Typer(add_completion=False)

@app.callback()
def main():
    setup_logging()

def _target_opts(
        display: int | None = typer.Option(None, "--display", "-d", help="ddcutil Display number"),
        bus: int | None = typer.Option(None, "--bus", "-b", help="ddcutil I2C bus number")
):
    if display is None and bus is None:
        #defult to display 1 if no options are provided for now
        return {"display": 1, "bus": None}
    if display is not None and bus is not None:
        raise typer.BadParameter("Cannot specify both display and bus options")
    return {"display": display, "bus": bus}

@app.command("list")
def list_cmd():
    mons = discovery.list_monitors()
    if not mons:
        print("[yellow]No monitors found. Ensure DDC/CI is enabled and permissions are set.[/yellow]")
        raise typer.Exit(code=1)
    
    table = Table(title="Detected Monitors")
    table.add_column("Display #", justify="right")
    table.add_column("I2C Bus", justify="right")
    table.add_column("Mfg", justify="left")
    table.add_column("Model", justify="left")
    table.add_column("Serial", overflow="fold")

    for m in mons:
        table.add_row(str(m.display), f"/dev/i2c-{m.i2c_bus}", m.mfg, m.model, m.serial or "")
    print(table)

get_app = typer.Typer()
set_app = typer.Typer()
app.add_typer(get_app, name="get")
app.add_typer(set_app, name="set")

@get_app.command("brightness")
def get_brightness_cmd(
    display: int | None = typer.Option(None, "--display", "-d", help="ddcutil Display number"),
    bus: int | None = typer.Option(None, "--bus", "-b", help="ddcutil I2C bus number")
):
    t = _target_opts(display, bus)
    curr, mx = brightness.get_brightness(display=t["display"], bus=t["bus"])
    print(f"Brightness: [bold]{curr}[/bold]/{mx}")

@set_app.command("brightness")
def set_brightness_cmd(
    value: int = typer.Argument(..., help="Brightness value [0-100]"),
    display: int | None = typer.Option(None, "--display", "-d", help="ddcutil Display number"),
    bus: int | None = typer.Option(None, "--bus", "-b", help="ddcutil I2C bus number")
):
    t = _target_opts(display, bus)
    brightness.set_brightness(value, display=t["display"], bus=t["bus"])
    print(f"Brightness set to [bold]{value}[/bold]")

app.command("off")
def power_off_cmd(
    display: int | None = typer.Option(None, "--display", "-d", help="ddcutil Display number"),
    bus: int | None = typer.Option(None, "--bus", "-b", help="ddcutil I2C bus number")
):
    t = _target_opts(display, bus)
    power.power_off(display=t["display"], bus=t["bus"])
    print("Power state set to [bold]Off[/bold]")

app.command("on")
def power_on_cmd(
    display: int | None = typer.Option(None, "--display", "-d", help="ddcutil Display number"),
    bus: int | None = typer.Option(None, "--bus", "-b", help="ddcutil I2C bus number")
):
    t = _target_opts(display, bus)
    power.power_on(display=t["display"], bus=t["bus"])
    print("Power state set to [bold]On[/bold]")

@app.command("toggle")
def power_toggle_cmd(
    display: int | None = typer.Option(None, "--display", "-d", help="ddcutil Display number"),
    bus: int | None = typer.Option(None, "--bus", "-b", help="ddcutil I2C bus number")
):
    t = _target_opts(display, bus)
    state = power.toggle_power(display=t["display"], bus=t["bus"])
    print("Power state [bold]{state}[/bold]")