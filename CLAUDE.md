# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A workout tracker for an M5Stack Cardputer (ESP32), written in MicroPython using the M5Stack UIFlow2 runtime (`M5`, `M5.Widgets`, `nvs`, `network`, `ntptime`).

## Running

Run on a connected device with `mpremote run lift.py`. The VS Code task "Run file" (`.vscode/tasks.json`) does the same for the current file.

## Architecture notes

- Entry point follows the UIFlow2 template: `setup()` then `loop()` under `if __name__ == '__main__'`, with errors routed to `utility.print_error_msg` (provided by device firmware).
- Wi-Fi credentials are read from the device's NVS (`ssid0`/`pswd0`), not from the code. Set them on the device; never hardcode them.
- Time: `ntptime.settime()` sets the RTC to UTC. `now()` applies `UTC_OFFSET_HOURS` (currently a fixed offset, no DST handling) to produce local time. Use `now()` rather than `time.localtime()` directly.
- Code uses 2-space indentation.
