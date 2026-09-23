#ifndef SAFETY_INTERFACE_H
#define SAFETY_INTERFACE_H

void safety_interface_init(void);
void safety_block_commands(void);
void safety_allow_commands(void);
int safety_commands_blocked(void);

#endif
