// pocket-field firmware — Arduino entry point.
//
// Responsibilities:
//   1. Bring up USB CDC serial at 115200.
//   2. Construct the SerialCli and register system.* commands.
//   3. Read line-terminated frames from Serial, dispatch through the CLI,
//      write responses back.
//
// Hardware bring-up (M5 init, display, keyboard, Grove I2C) lands in subsequent
// Phase 1 commits once the Evil-Cardputter ADV code is ported in.

#include <Arduino.h>

#include "commands/system_cmds.h"
#include "protocol.h"
#include "serial_cli.h"

static pocket_field::SerialCli g_cli;
static String g_line_buffer;

void setup() {
    Serial.begin(pocket_field::SERIAL_BAUD);
    // Brief wait for USB CDC to be ready on ESP32-S3. Don't block forever —
    // device should still run without an attached host.
    for (unsigned long start = millis(); !Serial && millis() - start < 2000;) {
        delay(10);
    }

    pocket_field::commands::register_system_commands(g_cli);

    Serial.println("# pocket-field firmware boot");
    Serial.print("# protocol ");
    Serial.print(pocket_field::PROTOCOL_VERSION);
    Serial.print(" / firmware ");
    Serial.println(POCKET_FIELD_FW_VERSION);
    Serial.println("# ready");
}

void loop() {
    while (Serial.available() > 0) {
        const char c = static_cast<char>(Serial.read());
        if (c == pocket_field::LINE_TERMINATOR) {
            if (!g_line_buffer.isEmpty()) {
                std::string line(g_line_buffer.c_str());
                std::string response = g_cli.handle_line(line);
                Serial.println(response.c_str());
                g_line_buffer.clear();
            }
        } else if (c != '\r') {
            g_line_buffer += c;
            // Guard against pathologically long lines.
            if (g_line_buffer.length() > 512) {
                g_line_buffer.clear();
            }
        }
    }
    delay(1);
}
