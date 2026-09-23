#include "safety_interface.h"

static int command_blocked = 0;

void safety_interface_init(void)
{
    command_blocked = 0;
}

void safety_block_commands(void)
{
    command_blocked = 1;
}

void safety_allow_commands(void)
{
    command_blocked = 0;
}

int safety_commands_blocked(void)
{
    return command_blocked;
}
