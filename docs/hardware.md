# Hardware

## M5Stack Cardputter ADV

- **MCU**: ESP32-S3FN8 (Xtensa LX7 dual core, 240 MHz, 8 MB flash)
- **Keyboard**: ADV-specific — different chip from original Cardputter. Most Cardputter firmware images built for the original won't work.
- **Display**: ST7789 color TFT
- **Storage**: microSD slot
- **Power**: USB-C + internal battery
- **Grove ports**: I2C (yellow/white on standard Grove cable)

## PN532 NFC Unit

- **M5Stack part**: NFC Unit (PN532)
- **Protocol**: I2C via Grove port
- **I2C address**: `0x24` (default) or configurable
- **Supported tags** (for pocket-field v0.1):
  - MIFARE Classic 1k/4k — UID + sector reads (with default keys)
  - MIFARE Ultralight — UID + page reads
  - MIFARE DESFire EV1/EV2 — UID only (crypto not attempted)
  - HID iCLASS (non-SE) — UID reads
  - ISO14443A generic — UID reads
- **Not supported** (documented honestly):
  - HID iCLASS SE / SE2 / Seos — cryptographically secured, out of scope
  - NFC-V / ISO15693 — not implemented in v0.1
  - Active card emulation — not implemented in v0.1

## Wiring

Plug the PN532 Grove cable into the Cardputter ADV's Grove port. No soldering needed for v0.1.

## Power considerations

USB-powered Cardputter + PN532 draws about 150-200 mA peak. Any standard USB port handles this.

Battery life running NFC scans continuously: rough estimate 2-3 hours on a full charge. Idle: several hours.

## Other accessories (not used in v0.1 but on the roadmap)

- **Glass2 HUD** — I2C OLED status display. Planned for Phase 5+.
- **Roller Switch** — Grove rotary input. Planned for Phase 5+.
- **LoRa Cap 868 MHz** (SX1276) — pogo-pin stack. Planned for Phase 5+ long-range reporting.
