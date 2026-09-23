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
