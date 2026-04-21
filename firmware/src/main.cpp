// pocket-field firmware — entry point
//
// Phase 0: skeleton only. Phase 1 will wire up the SerialCli
// subsystem and register command modules.

#include <Arduino.h>
#include "protocol.h"

void setup() {
    Serial.begin(pocket_field::SERIAL_BAUD);
    while (!Serial && millis() < 2000) {
        // wait briefly for USB CDC
    }
    Serial.println("# pocket-field firmware booting");
    Serial.print("# protocol version: ");
    Serial.println(pocket_field::PROTOCOL_VERSION);
    Serial.print("# firmware version: ");
    Serial.println(POCKET_FIELD_FW_VERSION);
    Serial.println("# ready");
}

void loop() {
    // Phase 1: SerialCli::poll() goes here.
    delay(10);
}
