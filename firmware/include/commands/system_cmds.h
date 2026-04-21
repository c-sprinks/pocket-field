// pocket-field firmware — system.* command handlers.
//
// system.version, system.help, system.status.

#pragma once

#include "../serial_cli.h"

namespace pocket_field::commands {

// Register all system.* handlers with the given SerialCli instance.
void register_system_commands(SerialCli& cli);

}  // namespace pocket_field::commands
