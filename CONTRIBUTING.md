# Contributing

Thanks for your interest. This project is in early development, so contributions and feedback are especially welcome.

## Before you contribute

- Read [ARCHITECTURE.md](ARCHITECTURE.md) and [docs/protocol-v1.md](docs/protocol-v1.md).
- Check [ROADMAP.md](ROADMAP.md) — if your idea isn't there, open an issue first so we can discuss scope before you spend time on code.
- For non-trivial changes, open an issue describing the approach before starting a PR.

## Dev environment

### Firmware (`firmware/`)

- **Toolchain**: [PlatformIO](https://platformio.org/)
- **Board**: `m5stack-stamps3` (ESP32-S3FN8)
- **Framework**: Arduino

```bash
cd firmware
pio run              # build
pio run -t upload    # flash connected Cardputter ADV
pio test             # unit tests on native platform
```

### MCP server (`mcp/`)

- **Python**: 3.11+
- **Tooling**: [uv](https://github.com/astral-sh/uv) recommended, but `pip` works

```bash
cd mcp
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
ruff check .
mypy src/
```

## Coding standards

- **Firmware**: C++17, `clang-format` config in `firmware/.clang-format`
- **Python**: `ruff` + `mypy` in strict mode, enforced in CI

## Commit messages

- Present tense, short subject line under 72 chars
- Reference issues where relevant
- AI-assisted commits are welcome and should be credited in the commit trailer

## Pull requests

- Keep PRs focused — one feature or fix per PR
- Update docs when you change behavior
- Tests required for new commands and protocol changes
- CI must be green before merge

## Licensing

By submitting a contribution, you agree that it will be licensed under the same [MIT License](LICENSE) as the rest of the project.
