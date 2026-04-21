"""Hardware backend implementations.

Each backend wraps a class of physical device and exposes the same abstract
interface (see `base.Backend`). Adding hardware support means adding a new
backend module, not changing tools or the server.

Current backends:
  - cardputter (Phase 3) — M5Stack Cardputter ADV over USB serial
  - proxmark3 (Phase 5+) — Proxmark3 via the pm3 CLI subprocess
"""
