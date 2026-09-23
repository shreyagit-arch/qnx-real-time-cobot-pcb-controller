#ifndef GPIO_INTERFACE_H
#define GPIO_INTERFACE_H

int gpio_init(void);
int gpio_set_led(int led_id, int state);
int gpio_read_button(int button_id);
void gpio_shutdown(void);

#endif
