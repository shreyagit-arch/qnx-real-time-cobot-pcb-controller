#ifndef I2C_INTERFACE_H
#define I2C_INTERFACE_H

int i2c_init(void);
int i2c_lcd_write(const char *message);
void i2c_shutdown(void);

#endif
