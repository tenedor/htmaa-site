//
// rgb-button.ftdi.44.c
//
// 115200 baud FTDI character echo, with flash string
//
// set lfuse to 0x7E for 20 MHz xtal
//
// Daniel Windham
// 11/04/15
//
// adapted from
// Neil Gershenfeld
// 12/8/10
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
#define input(directions,pin) (directions &= ~pin) // set port direction for input
#define pullup(port,pin) (port |= pin) // set internal pullup on input pin
#define set(port,pin) (port |= pin) // set port pin
#define clear(port,pin) (port &= (~pin)) // clear port pin
#define pin_test(pins,pin) (pins & pin) // test for port pin

#define led_r_direction DDRB
#define led_r_port PORTB
#define led_r_pin (1 << PB2)

#define led_g_direction DDRA
#define led_g_port PORTA
#define led_g_pin (1 << PA6)

#define led_b_direction DDRA
#define led_b_port PORTA
#define led_b_pin (1 << PA7)

#define buttons_direction DDRA
#define buttons_port PINA
#define buttons_pins PINA
#define button_0_pin (1 << PA5)
#define button_1_pin (1 << PA4)
#define button_2_pin (1 << PA3)
#define button_3_pin (1 << PA2)

void set_rgb_pulse_rates(int button_states[4], int rgb_pulses_per_ms[3]) {
  rgb_pulses_per_ms[0] = 0;
  rgb_pulses_per_ms[1] = 0;
  rgb_pulses_per_ms[2] = 0;
  if (button_states[0]) {
    rgb_pulses_per_ms[0] += 20;
    rgb_pulses_per_ms[1] += 0;
    rgb_pulses_per_ms[2] += 0;
  }
  if (button_states[1]) {
    rgb_pulses_per_ms[0] += 0;
    rgb_pulses_per_ms[1] += 50;
    rgb_pulses_per_ms[2] += 0;
  }
  if (button_states[2]) {
    rgb_pulses_per_ms[0] += 0;
    rgb_pulses_per_ms[1] += 0;
    rgb_pulses_per_ms[2] += 50;
  }
  if (button_states[3]) {
    if (button_states[0] || button_states[1] || button_states[2]) {
      rgb_pulses_per_ms[0] *= 2;
      rgb_pulses_per_ms[1] *= 2;
      rgb_pulses_per_ms[2] *= 2;
    } else {
      rgb_pulses_per_ms[0] += 10;
      rgb_pulses_per_ms[1] += 25;
      rgb_pulses_per_ms[2] += 25;
    }
  }
}

int main(void) {
  // set clock divider to /1
  CLKPR = (1 << CLKPCE);
  CLKPR = (0 << CLKPS3) | (0 << CLKPS2) | (0 << CLKPS1) | (0 << CLKPS0);

  // initialize rgb output pins
  set(led_r_port, led_r_pin);
  set(led_g_port, led_g_pin);
  set(led_b_port, led_b_pin);
  output(led_r_direction, led_r_pin);
  output(led_g_direction, led_g_pin);
  output(led_b_direction, led_b_pin);

  input(buttons_direction, button_0_pin);
  input(buttons_direction, button_1_pin);
  input(buttons_direction, button_2_pin);
  input(buttons_direction, button_3_pin);
  pullup(buttons_port, button_0_pin);
  pullup(buttons_port, button_1_pin);
  pullup(buttons_port, button_2_pin);
  pullup(buttons_port, button_3_pin);

  unsigned int elapsed_us = 0;
  int button_polls_per_second = 10;
  int button_states[4] = {0, 0, 0, 0};
  int rgb_pulses_per_ms[3] = {0, 0, 0};

  while (1) {
    _delay_us(1);
    elapsed_us++;

    // poll button state
    if (elapsed_us % 1000 < button_polls_per_second) {
      if (!pin_test(buttons_pins, button_0_pin)) {
        button_states[0] = 10;
      } else if (button_states[0]) {
        button_states[0]--;
      }
      if (!pin_test(buttons_pins, button_1_pin)) {
        button_states[1] = 10;
      } else if (button_states[1]) {
        button_states[1]--;
      }
      if (!pin_test(buttons_pins, button_2_pin)) {
        button_states[2] = 10;
      } else if (button_states[2]) {
        button_states[2]--;
      }
      if (!pin_test(buttons_pins, button_3_pin)) {
        button_states[3] = 10;
      } else if (button_states[3]) {
        button_states[3]--;
      }
    }

    // calculate rgb values
    set_rgb_pulse_rates(button_states, rgb_pulses_per_ms);

    // update red led
    if (elapsed_us % 1000 < rgb_pulses_per_ms[0]) {
      clear(led_r_port, led_r_pin);
    } else {
      set(led_r_port, led_r_pin);
    }
    // update green led
    if (elapsed_us % 1000 < rgb_pulses_per_ms[1]) {
      clear(led_g_port, led_g_pin);
    } else {
      set(led_g_port, led_g_pin);
    }
    // update blue led
    if (elapsed_us % 1000 < rgb_pulses_per_ms[2]) {
      clear(led_b_port, led_b_pin);
    } else {
      set(led_b_port, led_b_pin);
    }
  }
}
