// pocket-field firmware — SerialCli
//
// Pure C++ parser + dispatcher for protocol v1 frames (docs/protocol-v1.md).
// No Arduino dependencies — the native test platform exercises this directly.
// main.cpp bridges Serial bytes ↔ handle_line().

#pragma once

#include <functional>
#include <map>
#include <string>

#include "protocol.h"

namespace pocket_field {

// Parsed REQ frame.
struct Request {
    int id = 0;
    std::string command;  // e.g. "system.version"
    std::string args;     // raw arg string, handler-parsed
};

// Handler return value. `ok=true` → OK frame; `ok=false` → ERR frame.
struct Response {
    int id = 0;
    bool ok = true;
    std::string body;        // JSON for OK, human message for ERR
    Error error_code = Error::INTERNAL_ERROR;  // only meaningful when ok=false
};

using CommandHandler = std::function<Response(const Request&)>;

class SerialCli {
public:
    // Register a handler for a command name. Overwrites any previous handler.
    void register_command(const std::string& name, CommandHandler handler);

    // Parse a full line (without trailing '\n') and return the response frame
    // ready to write out. Always returns a non-empty string.
    // If the line is malformed or the command is unknown, returns an ERR frame.
    std::string handle_line(const std::string& line);

    // Lower-level — exposed for testing.
    static bool parse_request(const std::string& line, Request& out);
    static std::string format_ok(int id, const std::string& json_body);
    static std::string format_err(int id, Error code, const std::string& message);

private:
    std::map<std::string, CommandHandler> commands_;
};

}  // namespace pocket_field
