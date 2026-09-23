#ifndef CAMERA_INTERFACE_H
#define CAMERA_INTERFACE_H

int camera_init(void);
int camera_capture_frame(void);
void camera_shutdown(void);

#endif
