# Firmware unit tests

Tests run on PlatformIO's `native` platform — no Cardputter required.

```bash
cd firmware
pio test -e native
```

Each test suite is a subdirectory named `test_*/` with a `test_main.cpp` using the Unity framework.
