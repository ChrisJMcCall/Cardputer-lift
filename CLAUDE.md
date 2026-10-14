# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A workout tracker for an M5Stack Cardputer (ESP32), written in MicroPython using the M5Stack UIFlow2 runtime (`M5`, `M5.Widgets`, `nvs`, `network`, `ntptime`).

## Running

Source lives in `src/`. `mpremote mount src repl --inject-file util/launch.py` mounts a directory on the device without causing unnecessary writes on the device's flash memory. Within the terminal you can then use Ctrl-C, Ctrl-K to restart the application.

## Architecture notes

- Entry point follows the UIFlow2 template: `setup()` then `loop()` under `if __name__ == '__main__'`, with errors routed to `utility.print_error_msg` (provided by device firmware).
- Wi-Fi credentials are read from the device's NVS (`ssid0`/`pswd0`), not from the code. Set them on the device; never hardcode them.
- Time: `ntptime.settime()` sets the RTC to UTC. `now()` applies `UTC_OFFSET_HOURS` (currently a fixed offset, no DST handling) to produce local time. Use `now()` rather than `time.localtime()` directly.
- Do not keep everything in 1 file. Use python modules to organize.
- Modules in `src/`: `lift.py` (entry point), `date_time.py` (Wi-Fi/NTP/local time), `ui/` (one module per screen, see below), `db.py` (storage).
- Storage is a `btree` database at `/sd/app_data/lift/lift.db` on the Cardputer SD card (mounted by `db.py`; a card must be inserted). Keys are prefixed `ex:`, `plan:`, `meta:` (`meta:order` is the plan display order) with JSON values. Only `db.py` touches it; screens go through its functions.
- `ui/`: `nav.py` is the router and keyboard glue (`nav.go('<name>', *args)` swaps the active screen; screen names are mapped to classes there). `base.py` has the `Screen`/`ListScreen` base classes, colors and key codes. Each other module is one screen; screens draw only when `self.dirty` is set.
