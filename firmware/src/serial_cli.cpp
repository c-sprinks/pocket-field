// pocket-field firmware — SerialCli implementation
//
// Pure C++, no Arduino dependencies.

#include "serial_cli.h"

#include <sstream>

namespace pocket_field {

void SerialCli::register_command(const std::string& name, CommandHandler handler) {
    commands_[name] = std::move(handler);
}

bool SerialCli::parse_request(const std::string& line, Request& out) {
    // Expected: "REQ <id> <command> [args...]"
    // At minimum: "REQ <id> <command>"
    std::istringstream iss(line);
    std::string prefix;
    if (!(iss >> prefix) || prefix != FRAME_REQ) {
        return false;
    }
    if (!(iss >> out.id) || out.id < 1 || out.id > 65535) {
        return false;
    }
    if (!(iss >> out.command) || out.command.empty()) {
        return false;
    }
    // Rest of the line (may be empty) is the args.
    std::getline(iss, out.args);
    // Trim one leading space if present (from the separator between command and args).
    if (!out.args.empty() && out.args.front() == ' ') {
        out.args.erase(0, 1);
    }
    return true;
}

std::string SerialCli::format_ok(int id, const std::string& json_body) {
    std::ostringstream oss;
    oss << FRAME_OK << ' ' << id << ' ' << json_body;
    return oss.str();
}

std::string SerialCli::format_err(int id, Error code, const std::string& message) {
    std::ostringstream oss;
    oss << FRAME_ERR << ' ' << id << ' ' << static_cast<int>(code) << ' ' << message;
    return oss.str();
}

std::string SerialCli::handle_line(const std::string& line) {
    Request req;
    if (!parse_request(line, req)) {
        return format_err(0, Error::BAD_ARGUMENTS, "malformed REQ frame");
    }

    auto it = commands_.find(req.command);
    if (it == commands_.end()) {
        return format_err(req.id, Error::UNKNOWN_COMMAND, "command not registered: " + req.command);
    }

    Response resp = it->second(req);
    resp.id = req.id;  // handler doesn't need to care; we stamp it here.

    if (resp.ok) {
        return format_ok(resp.id, resp.body);
    }
    return format_err(resp.id, resp.error_code, resp.body);
}

}  // namespace pocket_field
