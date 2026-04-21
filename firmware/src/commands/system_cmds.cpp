// pocket-field firmware — system.* command handlers.
//
// Keep JSON generation hand-built for now; pulling ArduinoJson in a future phase
// when response complexity justifies the dependency.

#include "commands/system_cmds.h"

#include <sstream>

#ifndef POCKET_FIELD_NATIVE_TEST
  #include <Arduino.h>  // millis()
#endif

namespace pocket_field::commands {

namespace {

// Placeholder when native tests run without Arduino's millis().
unsigned long uptime_ms() {
#ifdef POCKET_FIELD_NATIVE_TEST
    return 0UL;
#else
    return ::millis();
#endif
}

// Placeholder — real battery ADC wiring lands in Phase 2+.
int battery_pct() {
    return -1;  // -1 signals "unknown / not wired"
}

Response on_version(const Request&) {
    std::ostringstream body;
    body << R"({"protocol":")" << PROTOCOL_VERSION
         << R"(","firmware":")" << POCKET_FIELD_FW_VERSION
         << R"(","hardware":"cardputter-adv"})";
    return Response{0, true, body.str(), Error::INTERNAL_ERROR};
}

Response on_help(const Request&) {
    // Hard-coded for v0.1. Phase 1+: build dynamically from the SerialCli registry.
    const char* body =
        R"({"commands":[)"
        R"({"name":"system.version","description":"firmware and protocol version"},)"
        R"({"name":"system.help","description":"list registered commands"},)"
        R"({"name":"system.status","description":"runtime device state"})"
        R"(]})";
    return Response{0, true, body, Error::INTERNAL_ERROR};
}

Response on_status(const Request&) {
    std::ostringstream body;
    body << R"({"uptime_ms":)" << uptime_ms()
         << R"(,"battery_pct":)" << battery_pct()
         << R"(,"peripherals":{"pn532":false}})";
    return Response{0, true, body.str(), Error::INTERNAL_ERROR};
}

}  // namespace

void register_system_commands(SerialCli& cli) {
    cli.register_command("system.version", on_version);
    cli.register_command("system.help", on_help);
    cli.register_command("system.status", on_status);
}

}  // namespace pocket_field::commands
