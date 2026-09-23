#ifndef SERVO_INTERFACE_H
#define SERVO_INTERFACE_H

int servo_init(void);
int servo_set_angle(int servo_id, float angle_deg);
void servo_stop_all(void);
void servo_shutdown(void);

#endif
