#!/usr/bin/python
# -*- coding: utf-8 -*-

import decorator
import logging

from comm.async import AsyncComm
from comm.sync import SyncComm
from comm import CommError
from epuck import EPuckError


class ControllerError(EPuckError):
    """E-Puck robot is not responding as it should."""
    pass

class WrongCommand(ControllerError):
    """E-Puck doesn't understand the given command."""
    pass


class Controller(object):
    """Control E-Puck robot.

    Give commands to e-puck robot via bluetooth connection. Uses modified BTcom
    tool.

    Atributes:
        MAX_SPEED -- Maximum speed of e-puck's motors measured in pulses per
                     second. -MAX_SPEED is maximum backward speed.

    """

    MAX_SPEED = 1000

    def __init__(self, port, asynchronous=False, update=0, **kwargs):
        """Create new controller.

        Arguments:
            port -- The device where e-puck robot is connected (e.g. /dev/rfcomm0).
            asynchronous -- Set True to use asynchronous communication.
                Synchronous communication is default.
            update -- How often download sensor informations from robot. 0
                turns it off.

        """

        if asynchronous:
            self.comm = AsyncComm(port, **kwargs)
            self.comm.start()
        else:
            self.comm = SyncComm(port, **kwargs)

        self.update_every = update
        self.command_i = 0

        self.motor_speed = [0, 0]
        self.body_led = False
        self.front_led = False
        self.leds = 8 * [False]

        self.logger = logging.getLogger('Controller')

    def command(func):
        def _command(func, self, *args, **kwargs):
            self.command_i = (self.command_i + 1) % 255
            return func(self, *args, **kwargs)
        return decorator.decorator(_command, func)


    @command
    def set_motor_speed(self, left, right):
        """Set the speed of the motors."""
        try:
            if (-self.MAX_SPEED <= left <= self.MAX_SPEED) \
            and (-self.MAX_SPEED <= right <= self.MAX_SPEED):
                command = "D%c,%d,%d\r\n" % (self.command_i, left, right)
                ret = self.comm.send_command(command, self.command_i, 'd')
                return ret
            else:
                raise WrongCommand("Speed is out of bounds.")
        except CommError as e:
            self.logger.error(e)

    @command
    def get_motor_speed(self):
        """Get speed of motors.

        The speed is measured in pulses per second, one pulse is
        aproximately 0.13mm. The speed can be in range
        (-MAX_SPEED, MAX_SPEED).

        Returns tuple (left motor speed, right motor speed).

        """
        def _parse_response(response):
            try:
                left, right = response.strip().split(',')
                return (int(left), int(right))
            except Exception as e:
                self.logger.error(e)

        command = "E%c\r\n" % self.command_i
        ret = self.comm.send_command(command, self.command_i, 'e', _parse_response)
        return ret


    @command
    def set_body_led(self, value):
        """Set the green body LED's status.

        Arguments:
            value - boolean, turn the led on.

        """
        pass

    @command
    def get_body_led(self):
        """Get the green body LED's status. """
        pass


    @command
    def set_front_led(self, value):
        """Set the bright front LED's status.

        Arguments:
            value - boolean, turn the led on.

        """
        pass

    @command
    def get_front_led(self):
        """Get the bright front LED's status. """
        pass


    @command
    def set_led(self, led_no, value):
        """Set the LED's status.

        There are 8 LEDs on the e-puck robot. The LED number 0 is the frontal
        one, the LED numbering is increasing clockwise.

        Arguments:
            led_no - number of the led (0 - 7).
            value - boolean, turn the led on.

        """
        pass

    @command
    def get_led(self, led_no):
        """Get the LED's status.

        There are 8 LEDs on the e-puck robot. The LED number 0 is the frontal
        one, the LED numbering is increasing clockwise.

        Arguments:
            led_no - number of the led (0 - 7).

        """
        pass


    @command
    def get_turning_switch(self):
        """Get the position of the rotating 16 positions switch.

        Position 0 correspond to the arrow pointing on the right when looking
        in the same direction as the robot.

        """
        pass


    @command
    def get_proximity_sensors(self):
        """Get the values of the 8 proximity sensors.

        The 12 bit values of the 8 proximity sensors. For left and right side
        there is one sensor situated 10 degrees from the front, others are 45
        degrees and 90 degrees from the front. For each side there is also one
        sensor on the back side.

        The keys for sensor values are following: L10, L45, L90, LB, R10, R45,
        R90, RB.

        The values are in range [0, 4095].

        """
        pass


    @command
    def get_ambient_sensors(self):
        """Get the values of the 8 ambient light sensors.

        The 12 bit values of the 8 ambient light sensors. For left and right
        side there is one sensor situated 10 degrees from the front, others are
        45 degrees and 90 degrees from the front. For each side there is also
        one sensor on the back side.

        The keys for sensor values are following: L10, L45, L90, LB, R10, R45,
        R90, RB.

        The values are in range [0, 4095].

        """
        pass


    @command
    def set_camera(self, options):
        """Set the camera properties."""
        pass

    @command
    def get_photo(self):
        """Take a photo."""
        pass


    @command
    def reset(self):
        """Reset the robot."""
        pass


# Test the module.
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    a = Controller(None, asynchronous=True, timeout=20, offline=True, offline_address=('localhost',65432))
    r1 = a.set_motor_speed(100,100)
    r2 = a.get_motor_speed()
