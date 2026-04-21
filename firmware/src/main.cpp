// pocket-field firmware — Arduino entry point.
//
// Responsibilities:
//   1. Bring up M5Cardputer hardware (display, power, USB CDC serial).
//   2. Construct the SerialCli, register system.* command handlers.
//   3. Read line-terminated protocol v1 frames from Serial, dispatch
//      through the CLI, write responses back.
//
// Notes for the Cardputter ADV:
//   - M5Cardputer.begin() handles display + power init. The ADV keyboard
//     chip differs from the original; we don't use the M5 keyboard API in
//     Phase 1, so the ADV difference doesn't affect us here.
//   - USB CDC is the ESP32-S3's native USB — enumerates as /dev/ttyACM*.
//   - Feature module init (NFC, WiFi, etc.) lands in later phases.

#include <Arduino.h>
#include <M5Cardputer.h>

#include "commands/system_cmds.h"
#include "protocol.h"
#include "serial_cli.h"

static pocket_field::SerialCli g_cli;
static String g_line_buffer;

// Draw a simple boot screen on the Cardputter display.
static void draw_boot_screen() {
    auto& d = M5Cardputer.Display;
    d.setRotation(1);  // landscape, USB port on the left
    d.fillScreen(TFT_BLACK);
    d.setTextColor(TFT_GREEN, TFT_BLACK);
    d.setTextSize(2);
    d.setCursor(6, 6);
    d.print("pocket-field");

    d.setTextSize(1);
    d.setTextColor(TFT_WHITE, TFT_BLACK);
    d.setCursor(6, 30);
    d.printf("firmware %s", POCKET_FIELD_FW_VERSION);
    d.setCursor(6, 44);
    d.printf("protocol v%s", pocket_field::PROTOCOL_VERSION);

    d.setTextColor(TFT_YELLOW, TFT_BLACK);
    d.setCursor(6, 64);
    d.print("USB serial 115200");

    d.setTextColor(TFT_CYAN, TFT_BLACK);
    d.setCursor(6, 78);
    d.print("awaiting host...");
}

void setup() {
    // Configure M5Cardputer: enable display, skip the LED / speaker / SD
    // until a feature needs them. Serial is the ESP32-S3's native USB CDC.
    auto cfg = M5.config();
    M5Cardputer.begin(cfg, /*keyboard=*/false);

    Serial.begin(pocket_field::SERIAL_BAUD);
    // Brief wait for USB CDC to be ready. Don't block forever — the device
    // should still run without an attached host (we just won't talk to anyone).
    for (unsigned long start = millis(); !Serial && millis() - start < 2000;) {
        delay(10);
    }

    draw_boot_screen();
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
