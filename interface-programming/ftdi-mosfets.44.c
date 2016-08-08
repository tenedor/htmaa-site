//
// ftdi-mosfets.44.c
//
// ftdi communication and mosfet power switches
//
// Daniel Windham
// 11/25/15
//
// adapted from
// Neil Gershenfeld
// 11/14/10
//
// (c) Massachusetts Institute of Technology 2010
// This work may be reproduced, modified, distributed,
// performed, and displayed for any purpose. Copyright is
// retained and must be preserved. The work is provided
// as is; no warranty is provided, and users accept all 
// liability.
//

#include <avr/io.h>
#include <util/delay.h>
#include <avr/pgmspace.h>

#define output(directions,pin) (directions |= pin) // set port direction for output
#define set(port,pin) (port |= pin) // set port pin
#define clear(port,pin) (port &= (~pin)) // clear port pin
#define pin_test(pins,pin) (pins & pin) // test for port pin
#define bit_test(byte,bit) (byte & (1 << bit)) // test for bit set
#define bit_delay_time 103 // bit delay for 9600 with overhead
#define bit_delay() _delay_us(bit_delay_time) // RS232 bit delay
#define half_bit_delay() _delay_us(bit_delay_time/2) // RS232 half bit delay
#define char_delay() _delay_ms(10) // char delay

#define serial_port PORTA
#define serial_direction DDRA
#define serial_pins PINA
#define serial_pin_in (1 << PA6)
#define serial_pin_out (1 << PA7)

#define mosfet_switch_port PORTA // mosfet switch port
#define mosfet_switch_direction DDRA // mosfet switch direction
#define mosfet_switch_0 (1 << PA4) // mosfet switch pins
#define mosfet_switch_1 (1 << PA3) // "
#define mosfet_switch_2 (1 << PA2) // "
#define mosfet_switch_3 (1 << PA1) // "
#define laser_mosfet_switch (1 << PA0) // laser mosfet switch pin

void get_char(volatile unsigned char *pins, unsigned char pin, char *rxbyte) {
  //
  // read character into rxbyte on pins pin
  //    assumes line driver (inverts bits)
  //
  *rxbyte = 0;
  while (pin_test(*pins,pin))
    //
    // wait for start bit
    //
    ;
  //
  // delay to middle of first data bit
  //
  half_bit_delay();
  bit_delay();
  //
  // unrolled loop to read data bits
  //
  if pin_test(*pins,pin)
    *rxbyte |= (1 << 0);
  else
    *rxbyte |= (0 << 0);
  bit_delay();
  if pin_test(*pins,pin)
    *rxbyte |= (1 << 1);
  else
    *rxbyte |= (0 << 1);
  bit_delay();
  if pin_test(*pins,pin)
    *rxbyte |= (1 << 2);
  else
    *rxbyte |= (0 << 2);
  bit_delay();
  if pin_test(*pins,pin)
    *rxbyte |= (1 << 3);
  else
    *rxbyte |= (0 << 3);
  bit_delay();
  if pin_test(*pins,pin)
    *rxbyte |= (1 << 4);
  else
    *rxbyte |= (0 << 4);
  bit_delay();
  if pin_test(*pins,pin)
    *rxbyte |= (1 << 5);
  else
    *rxbyte |= (0 << 5);
  bit_delay();
  if pin_test(*pins,pin)
    *rxbyte |= (1 << 6);
  else
    *rxbyte |= (0 << 6);
  bit_delay();
  if pin_test(*pins,pin)
    *rxbyte |= (1 << 7);
  else
    *rxbyte |= (0 << 7);
  //
  // wait for stop bit
  //
  bit_delay();
  half_bit_delay();
}

void put_char(volatile unsigned char *port, unsigned char pin, char txchar) {
  //
  // send character in txchar on port pin
  //    assumes line driver (inverts bits)
  //
  // start bit
  //
  clear(*port,pin);
  bit_delay();
  //
  // unrolled loop to write data bits
  //
  if bit_test(txchar,0)
    set(*port,pin);
  else
    clear(*port,pin);
  bit_delay();
  if bit_test(txchar,1)
    set(*port,pin);
  else
    clear(*port,pin);
  bit_delay();
  if bit_test(txchar,2)
    set(*port,pin);
  else
    clear(*port,pin);
  bit_delay();
  if bit_test(txchar,3)
    set(*port,pin);
  else
    clear(*port,pin);
  bit_delay();
  if bit_test(txchar,4)
    set(*port,pin);
  else
    clear(*port,pin);
  bit_delay();
  if bit_test(txchar,5)
    set(*port,pin);
  else
    clear(*port,pin);
  bit_delay();
  if bit_test(txchar,6)
    set(*port,pin);
  else
    clear(*port,pin);
  bit_delay();
  if bit_test(txchar,7)
    set(*port,pin);
  else
    clear(*port,pin);
  bit_delay();
  //
  // stop bit
  //
  set(*port,pin);
  bit_delay();
  //
  // char delay
  //
  bit_delay();
}

void put_string(volatile unsigned char *port, unsigned char pin, char *str) {
  //
  // print a null-terminated string
  //
  static int index;
  index = 0;
  do {
    put_char(port, pin, str[index]);
    ++index;
  } while (str[index] != 0);
}

int main(void) {
  // set clock divider to /1
  CLKPR = (1 << CLKPCE);
  CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);

  // initialize mosfet pins
  clear(mosfet_switch_port, mosfet_switch_0);
  clear(mosfet_switch_port, mosfet_switch_1);
  clear(mosfet_switch_port, mosfet_switch_2);
  clear(mosfet_switch_port, mosfet_switch_3);
  output(mosfet_switch_direction, mosfet_switch_0);
  output(mosfet_switch_direction, mosfet_switch_1);
  output(mosfet_switch_direction, mosfet_switch_2);
  output(mosfet_switch_direction, mosfet_switch_3);

  // initialize laser-mosfet pin
  clear(mosfet_switch_port, laser_mosfet_switch);
  output(mosfet_switch_direction, laser_mosfet_switch);

  // initialize output pins
  set(serial_port, serial_pin_out);
  output(serial_direction, serial_pin_out);

  char chr;
  char chr2 = 'a';

  while (1) {
    get_char(&serial_pins, serial_pin_in, &chr);
    if (chr == 'a') {
      set(mosfet_switch_port, laser_mosfet_switch);
    } else if (chr == 'b') {
      clear(mosfet_switch_port, laser_mosfet_switch);
      put_char(&serial_port, serial_pin_out, chr2);
      // increment chr2, staying inside the ascii printable character space
      chr2++;
      if (chr2 > 126) {
        chr2 = 33;
      }
    }
  }
}
