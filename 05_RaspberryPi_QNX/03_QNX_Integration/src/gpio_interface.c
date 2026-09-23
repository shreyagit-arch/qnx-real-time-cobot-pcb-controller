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
