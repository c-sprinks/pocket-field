// pocket-field firmware — protocol v1 constants
//
// Wire format spec: docs/protocol-v1.md
// Keep this file in sync with the spec.

#pragma once

namespace pocket_field {

// Protocol version reported by system.version.
// Bump major for breaking wire-format changes.
constexpr const char* PROTOCOL_VERSION = "1";

// Line terminator for all frames.
constexpr char LINE_TERMINATOR = '\n';

// Serial baud rate.
constexpr unsigned long SERIAL_BAUD = 115200;

// Frame prefixes.
constexpr const char* FRAME_REQ    = "REQ";
constexpr const char* FRAME_OK     = "OK";
constexpr const char* FRAME_ERR    = "ERR";
constexpr const char* FRAME_STREAM = "STREAM";
constexpr const char* FRAME_END    = "END";

// Error codes — mirror docs/protocol-v1.md.
enum class Error : int {
    UNKNOWN_COMMAND            = 1,
    BAD_ARGUMENTS              = 2,
    NOT_IMPLEMENTED            = 3,
    HARDWARE_MISSING           = 10,
    HARDWARE_BUSY              = 11,
    HARDWARE_FAILURE           = 12,
    TIMEOUT                    = 20,
    PROTOCOL_VERSION_MISMATCH  = 30,
    NFC_NO_TAG                 = 42,
    NFC_UNSUPPORTED_TAG        = 43,
    NFC_READ_FAILURE           = 44,
    INTERNAL_ERROR             = 255,
};

}  // namespace pocket_field
