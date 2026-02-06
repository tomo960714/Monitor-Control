# monitor-control

A small Fedora-friendly monitor control tool using DDC/CI via `ddcutil`.

## Requirements
- `ddcutil` installed and working
- DDC/CI enabled in monitor OSD
- I2C permissions configured so `ddcutil detect` works without sudo

## Install (dev)
pip install -e .

## Usage
monitorctl list
monitorctl get brightness --display 1
monitorctl set brightness 60 --display 1
monitorctl off --display 1
monitorctl on --display 1
