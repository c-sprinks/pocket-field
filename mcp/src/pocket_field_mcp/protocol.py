"""Protocol v1 constants and frame parsing.

Wire format spec: ../../docs/protocol-v1.md
Keep this file in sync with the spec.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

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
    result: dict


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
    chunk: dict


@dataclass(frozen=True)
class EndFrame:
    """END <id>"""

    request_id: int


Frame = OkFrame | ErrFrame | StreamFrame | EndFrame


# Phase 1 will add the parse_frame() implementation here.
