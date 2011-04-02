#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

from epuck import Controller, WrongCommand

class Disco(object):
    """Test leds.

    Tests few effects with leds. The effect can be changed with turning switch.

    Turning switch values:

        0 -- Two rotating lights.
        1 -- Two rotating light in opposite directions.
        2 -- Blinking front led.
        15 -- Turn the effects off.

    """
    def __init__(self):
        logging.basicConfig(level=logging.WARNING)
        self.c = Controller('/dev/rfcomm2', asynchronous=True)
        self.state_request = None
        # Get first state
        self.state = self.c.get_turning_switch().get_response()

    def init_vars(self):
        """Initialize vars used for effects."""
        self.prev_i, self.i = 0, 0
        self.prev_j, self.j = 4, 4

    def init_state(self):
        """Initialize state."""
        self.init_vars()
        # Turn off all leds
        self.c.stop()
        self.c.set_front_led(0)

    def get_state(self):
        """Get the value of turning switch."""
        # The get_state has been called for the first time
        if self.state_request is None:
            self.state_request = self.c.get_turning_switch()
        # The response has been received
        elif self.state_request.response_received():
            new_state = self.state_request.get_response()
            # New state
            if new_state != self.state:
                self.state = new_state
                self.init_state()
            # Check the turning switch
            self.state_request = self.c.get_turning_switch()

    def run(self):
        """Do a step in the chosen effect."""
        if self.state == 0 or self.state == 1:
            self.c.set_led(self.prev_i, 0)
            self.c.set_led(self.i, 1)
            self.c.set_led(self.prev_j, 0)
            self.c.set_led(self.j, 1)
        elif self.state == 2:
            self.c.set_front_led(self.i)

    def update(self):
        """Update the vars used for chosen effect."""
        if self.state == 0:
            self.prev_i = self.i
            self.prev_j = self.j
            self.i = (self.i + 1) % 8
            self.j = (self.j + 1) % 8
        if self.state == 1:
            self.prev_i = self.i
            self.prev_j = self.j
            self.i = (self.i + 1) % 8
            self.j = (self.j - 1) % 8
        elif self.state == 2:
            self.i = 0 if self.i else 1

    def main_loop(self):
        """Main loop."""
        self.init_vars()
        while self.state != 15:
            # Update the state.
            self.get_state()
            # Do a step in the effect.
            self.run()
            # Update the effect.
            self.update()
            # Wait.
            time.sleep(0.1)

        # Turn off all leds.
        self.init_state()

d = Disco()
d.main_loop()

