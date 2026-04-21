"""Protocol v1 — constants, error codes, and wire-format client.

Spec: ../../../docs/protocol-v1.md
Keep this file in sync with the spec.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Protocol

PROTOCOL_VERSION = "1"
SERIAL_BAUD = 115200
LINE_TERMINATOR = "\n"

# Frame prefixes.
FRAME_REQ = "REQ"
FRAME_OK = "OK"
FRAME_ERR = "ERR"
FRAME_STREAM = "STREAM"
FRAME_END = "END"


class ErrorCode(IntEnum):
    """Error codes — mirror docs/protocol-v1.md."""

    UNKNOWN_COMMAND = 1
    BAD_ARGUMENTS = 2
    NOT_IMPLEMENTED = 3
    HARDWARE_MISSING = 10
    HARDWARE_BUSY = 11
    HARDWARE_FAILURE = 12
    TIMEOUT = 20
    PROTOCOL_VERSION_MISMATCH = 30
    NFC_NO_TAG = 42
    NFC_UNSUPPORTED_TAG = 43
    NFC_READ_FAILURE = 44
    INTERNAL_ERROR = 255


@dataclass(frozen=True)
class OkFrame:
    """OK <id> <json_result>"""

    request_id: int
    result: dict[str, Any]


@dataclass(frozen=True)
class ErrFrame:
    """ERR <id> <error_code> <human_message>"""

    request_id: int
    code: ErrorCode
    message: str


@dataclass(frozen=True)
class StreamFrame:
    """STREAM <id> <json_chunk>"""

    request_id: int
    chunk: dict[str, Any]


@dataclass(frozen=True)
class EndFrame:
    """END <id>"""

    request_id: int


Frame = OkFrame | ErrFrame | StreamFrame | EndFrame


class ProtocolError(Exception):
    """Raised when the firmware returns an ERR frame or the protocol is violated."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code.name} (code {int(code)}): {message}")


def parse_frame(line: str) -> Frame:
    """Parse a single response line into a typed frame.

    Raises `ProtocolError(INTERNAL_ERROR, ...)` if the frame is malformed.
    """
    line = line.strip("\r\n ")
    if not line:
        raise ProtocolError(ErrorCode.INTERNAL_ERROR, "empty line")

    # Note: OK / STREAM carry free-form JSON (may contain spaces) as their final
    # payload, so we split with a max of 2 separators after the prefix.
    if line.startswith(FRAME_OK + " "):
        _, id_str, body = line.split(" ", 2)
        return OkFrame(request_id=int(id_str), result=json.loads(body))

    if line.startswith(FRAME_ERR + " "):
        _, id_str, code_str, message = line.split(" ", 3)
        return ErrFrame(
            request_id=int(id_str),
            code=ErrorCode(int(code_str)),
            message=message,
        )

    if line.startswith(FRAME_STREAM + " "):
        _, id_str, body = line.split(" ", 2)
        return StreamFrame(request_id=int(id_str), chunk=json.loads(body))

    if line.startswith(FRAME_END + " ") or line == FRAME_END:
        parts = line.split(" ", 1)
        id_str = parts[1] if len(parts) > 1 else "0"
        return EndFrame(request_id=int(id_str))

    raise ProtocolError(ErrorCode.INTERNAL_ERROR, f"unknown frame prefix: {line!r}")


class SerialLike(Protocol):
    """Minimal transport surface the ProtocolV1Client needs.

    Mirrors pyserial.Serial so we can swap in a mock for tests.
    """

    def write(self, data: bytes) -> int | None: ...
    def readline(self) -> bytes: ...
    def reset_input_buffer(self) -> None: ...


class ProtocolV1Client:
    """Send REQ frames and parse OK/ERR/STREAM/END responses.

    Thread-safe: one in-flight request at a time, guarded by a lock.
    """

    def __init__(self, transport: SerialLike) -> None:
        self._transport = transport
        self._next_id = 1
        self._lock = threading.Lock()

    def _allocate_id(self) -> int:
        req_id = self._next_id
        self._next_id += 1
        if self._next_id > 65535:
            self._next_id = 1
        return req_id

    def send_request(self, command: str, args: str = "") -> dict[str, Any]:
        """Send a REQ and return the OK result as a dict.

        Raises `ProtocolError` if the firmware returns ERR or if anything
        else violates the protocol (unexpected frame id, malformed line, etc.).

        If the response is a STREAM sequence, collects all chunks and returns
        `{"stream": [chunk1, chunk2, ...]}` when the END frame arrives.
        """
        with self._lock:
            req_id = self._allocate_id()
            line = f"{FRAME_REQ} {req_id} {command}"
            if args:
                line += f" {args}"
            line += LINE_TERMINATOR

            self._transport.reset_input_buffer()
            self._transport.write(line.encode("utf-8"))

            stream_chunks: list[dict[str, Any]] = []

            while True:
                raw = self._transport.readline()
                if not raw:
                    raise ProtocolError(
                        ErrorCode.TIMEOUT,
                        f"no response to REQ {req_id} {command}",
                    )
                decoded = raw.decode("utf-8", "replace").strip()

                # Firmware log lines (start with '#') are out-of-band — ignore.
                if decoded.startswith("#") or not decoded:
                    continue

                frame = parse_frame(decoded)

                if isinstance(frame, OkFrame):
                    if frame.request_id != req_id:
                        # Stale response from a previous request — skip.
                        continue
                    if stream_chunks:
                        return {"stream": stream_chunks, "final": frame.result}
                    return frame.result

                if isinstance(frame, ErrFrame):
                    # ERR id=0 is a protocol-level error (malformed REQ) and still
                    # belongs to this send.
                    if frame.request_id not in (req_id, 0):
                        continue
                    raise ProtocolError(frame.code, frame.message)

                if isinstance(frame, StreamFrame):
                    if frame.request_id != req_id:
                        continue
                    stream_chunks.append(frame.chunk)
                    continue

                if isinstance(frame, EndFrame):
                    if frame.request_id != req_id:
                        continue
                    return {"stream": stream_chunks}
