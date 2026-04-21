# pocket-field-fw

Firmware for the M5Stack Cardputter ADV. Part of the [pocket-field](../README.md) project.

## Prerequisites

- [PlatformIO](https://platformio.org/) (VSCode extension or CLI)
- M5Stack Cardputter ADV (ESP32-S3FN8)
- USB-C cable

## Build and flash

```bash
cd firmware
pio run                 # compile for cardputter-adv
pio run -t upload       # flash connected Cardputter
pio device monitor      # open serial monitor at 115200 baud
```

## Run unit tests (no hardware needed)

```bash
pio test -e native
```

## Status

Phase 0 skeleton. Not flashable as a useful firmware yet. See [../ROADMAP.md](../ROADMAP.md).
