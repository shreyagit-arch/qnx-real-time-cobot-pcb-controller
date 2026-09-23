$base = "05_RaspberryPi_QNX\03_QNX_Integration"

# ============================================================
# GPIO INTERFACE
# LEDs, buttons and prototype E-STOP input.
# Physical GPIO access is NOT implemented yet.
# ============================================================

@'
#ifndef GPIO_INTERFACE_H
#define GPIO_INTERFACE_H

int gpio_init(void);
int gpio_set_led(int led_id, int state);
int gpio_read_button(int button_id);
void gpio_shutdown(void);

#endif
'@ | Set-Content "$base\include\gpio_interface.h"

@'
#include "gpio_interface.h"

int gpio_init(void)
{
    /* Placeholder until Raspberry Pi/QNX GPIO is physically verified. */
    return 0;
}

int gpio_set_led(int led_id, int state)
{
    (void)led_id;
    (void)state;
    return 0;
}

int gpio_read_button(int button_id)
{
    (void)button_id;
    return 0;
}

void gpio_shutdown(void)
{
}
'@ | Set-Content "$base\src\gpio_interface.c"


# ============================================================
# I2C INTERFACE
# Intended for the 16x2 LCD.
# LCD address and QNX I2C operation will be verified on hardware.
# ============================================================

@'
#ifndef I2C_INTERFACE_H
#define I2C_INTERFACE_H

int i2c_init(void);
int i2c_lcd_write(const char *message);
void i2c_shutdown(void);

#endif
'@ | Set-Content "$base\include\i2c_interface.h"

@'
#include "i2c_interface.h"

int i2c_init(void)
{
    return 0;
}

int i2c_lcd_write(const char *message)
{
    (void)message;
    return 0;
}

void i2c_shutdown(void)
{
}
'@ | Set-Content "$base\src\i2c_interface.c"


# ============================================================
# SERVO INTERFACE
# Intended for SG90 servos / 3-DOF arm.
# IMPORTANT: servo power must NOT come from Raspberry Pi GPIO.
# ============================================================

@'
#ifndef SERVO_INTERFACE_H
#define SERVO_INTERFACE_H

int servo_init(void);
int servo_set_angle(int servo_id, float angle_deg);
void servo_stop_all(void);
void servo_shutdown(void);

#endif
'@ | Set-Content "$base\include\servo_interface.h"

@'
#include "servo_interface.h"

int servo_init(void)
{
    return 0;
}

int servo_set_angle(int servo_id, float angle_deg)
{
    (void)servo_id;
    (void)angle_deg;
    return 0;
}

void servo_stop_all(void)
{
}

void servo_shutdown(void)
{
}
'@ | Set-Content "$base\src\servo_interface.c"


# ============================================================
# CAMERA INTERFACE
# Intended for USB webcam capture.
# No physical camera functionality is claimed yet.
# ============================================================

@'
#ifndef CAMERA_INTERFACE_H
#define CAMERA_INTERFACE_H

int camera_init(void);
int camera_capture_frame(void);
void camera_shutdown(void);

#endif
'@ | Set-Content "$base\include\camera_interface.h"

@'
#include "camera_interface.h"

int camera_init(void)
{
    return 0;
}

int camera_capture_frame(void)
{
    return 0;
}

void camera_shutdown(void)
{
}
'@ | Set-Content "$base\src\camera_interface.c"


# ============================================================
# SAFETY INTERFACE
# Provides command-blocking state at the hardware boundary.
# This complements the existing controller Safety Manager.
# ============================================================

@'
#ifndef SAFETY_INTERFACE_H
#define SAFETY_INTERFACE_H

void safety_interface_init(void);
void safety_block_commands(void);
void safety_allow_commands(void);
int safety_commands_blocked(void);

#endif
'@ | Set-Content "$base\include\safety_interface.h"

@'
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
'@ | Set-Content "$base\src\safety_interface.c"


# ============================================================
# TELEMETRY INTERFACE
# Boundary between QNX controller measurements and BAILEY-RT.
# Values are supplied by the controller/physical tests later.
# ============================================================

@'
#ifndef TELEMETRY_INTERFACE_H
#define TELEMETRY_INTERFACE_H

typedef struct
{
    double thermal_c;
    double sensor_metric;
    double power_deviation_percent;
    unsigned int communication_errors;

    unsigned long long vision_latency_us;
    unsigned long long ipc_latency_us;
    unsigned long long control_latency_us;
    unsigned long long e2e_latency_us;

    int safety_latched;
} BaileyTelemetry;

void telemetry_init(BaileyTelemetry *data);
int telemetry_publish(const BaileyTelemetry *data);

#endif
'@ | Set-Content "$base\include\telemetry_interface.h"

@'
#include "telemetry_interface.h"

void telemetry_init(BaileyTelemetry *data)
{
    if (data == 0)
        return;

    data->thermal_c = 0.0;
    data->sensor_metric = 0.0;
    data->power_deviation_percent = 0.0;
    data->communication_errors = 0;

    data->vision_latency_us = 0;
    data->ipc_latency_us = 0;
    data->control_latency_us = 0;
    data->e2e_latency_us = 0;

    data->safety_latched = 0;
}

int telemetry_publish(const BaileyTelemetry *data)
{
    if (data == 0)
        return -1;

    /*
     * Transport to BAILEY-RT is intentionally not implemented yet.
     * This function defines the integration boundary only.
     */
    return 0;
}
'@ | Set-Content "$base\src\telemetry_interface.c"


# ============================================================
# COMPILE TEST
# Verifies that all interface modules can be cross-compiled
# together for QNX AArch64 without claiming hardware operation.
# ============================================================

@'
#include "gpio_interface.h"
#include "i2c_interface.h"
#include "servo_interface.h"
#include "camera_interface.h"
#include "safety_interface.h"
#include "telemetry_interface.h"

int main(void)
{
    BaileyTelemetry telemetry;

    safety_interface_init();
    telemetry_init(&telemetry);

    gpio_init();
    i2c_init();
    servo_init();
    camera_init();

    telemetry_publish(&telemetry);

    camera_shutdown();
    servo_shutdown();
    i2c_shutdown();
    gpio_shutdown();

    return 0;
}
'@ | Set-Content "$base\src\integration_compile_test.c"

Write-Host ""
Write-Host "BAILEY-RT QNX integration skeleton created."
Write-Host "Headers : 6"
Write-Host "Modules : 6"
Write-Host "Compile test : 1"