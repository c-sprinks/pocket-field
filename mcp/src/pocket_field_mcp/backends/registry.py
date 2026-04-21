"""Backend registry.

Holds all configured hardware backends. Looked up by name or by capability.
"""

from __future__ import annotations

from .base import Backend, Capability


class BackendRegistry:
    def __init__(self) -> None:
        self._backends: dict[str, Backend] = {}

    def register(self, backend: Backend) -> None:
        """Add a backend. Raises if the name is already registered."""
        if backend.name in self._backends:
            raise ValueError(f"backend already registered: {backend.name}")
        self._backends[backend.name] = backend

    def get(self, name: str) -> Backend | None:
        return self._backends.get(name)

    def all(self) -> list[Backend]:
        return list(self._backends.values())

    def connected(self) -> list[Backend]:
        return [b for b in self._backends.values() if b.is_connected()]

    def with_capability(self, cap: Capability) -> list[Backend]:
        return [b for b in self._backends.values() if b.supports(cap)]
