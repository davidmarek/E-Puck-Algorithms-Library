#!/usr/bin/python
# -*- coding: utf-8 -*-

import decorator
import logging
import random
import string

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


def command(func):
    """Decorator for commands in controller."""
    def _command(func, self, *args, **kwargs):
        self.command_index = (self.command_index + 1) % len(string.ascii_letters)
        self.command_i = ord(string.ascii_letters[self.command_index])
        try:
            return func(self, *args, **kwargs)
        except CommError as e:
            self.logger.error(e)
    return decorator.decorator(_command, func)

class Controller(object):
    """Control E-Puck robot.

    Give commands to e-puck robot via bluetooth connection. Uses modified BTcom
    tool.

    Atributes:
        MAX_SPEED -- Maximum speed of e-puck's motors measured in pulses per
                     second. -MAX_SPEED is maximum backward speed.

    """

    MAX_SPEED = 1000

    GREYSCALE_MODE = 0
    RGB565_MODE = 1

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
        self.command_index = random.randrange(len(string.printable))
        self.command_i = string.printable[self.command_index]

        self.motor_speed = [0, 0]
        self.body_led = False
        self.front_led = False
        self.leds = 8 * [False]

        self.logger = logging.getLogger('Controller')


    @command
    def set_speed(self, left, right):
        """Set the speed of the motors."""
        if (-self.MAX_SPEED <= left <= self.MAX_SPEED) \
        and (-self.MAX_SPEED <= right <= self.MAX_SPEED):
            command = "D%c,%d,%d\n" % (self.command_i, left, right)
            ret = self.comm.send_command(command, self.command_i, 'd')
            return ret
        else:
            raise WrongCommand("Speed is out of bounds.")

    @command
    def get_speed(self):
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

        command = "E%c\n" % self.command_i
        ret = self.comm.send_command(command, self.command_i, 'e', _parse_response)
        return ret


    @command
    def set_body_led(self, value):
        """Set the green body LED's status.

        Arguments:
            value - boolean, turn the led on.

        """
        command = "B%c,%d\n" % (self.command_i, 1 if value else 0)
        ret = self.comm.send_command(command, self.command_i, 'b')
        return ret


    @command
    def set_front_led(self, value):
        """Set the bright front LED's status.

        Arguments:
            value - boolean, turn the led on.

        """
        command = "F%c,%d\n" % (self.command_i, 1 if value else 0)
        ret = self.comm.send_command(command, self.command_i, 'f')
        return ret


    @command
    def set_leds(self, value):
        """Set the all LEDs with one command.

        Arguments:
            value - boolean, turn the leds on.

        """
        command = "L%c,9,%d\n" % (self.command_i, 1 if value else 0)
        ret = self.comm.send_command(command, self.command_i, 'l')
        return ret


    @command
    def set_led(self, led_no, value):
        """Set the LED's status.

        There are 8 LEDs on the e-puck robot. The LED number 0 is the frontal
        one, the LED numbering is increasing clockwise.

        Arguments:
            led_no - number of the led (0 - 7).
            value - boolean, turn the led on.

        """
        if (0 <= led_no <= 7):
            command = "L%c,%d,%d\n" % (self.command_i, led_no, 1 if value else 0)
            ret = self.comm.send_command(command, self.command_i, 'l')
            return ret
        else:
            raise WrongCommand("Led number is out of the bounds.")


    @command
    def get_turning_switch(self):
        """Get the position of the rotating 16 positions switch.

        Position 0 correspond to the arrow pointing on the right when looking
        in the same direction as the robot.

        """
        def _parse_response(response):
            try:
                value = response.strip()
                return int(value)
            except Exception as e:
                self.logger.error(e)

        command = "C%c\n" % self.command_i
        ret = self.comm.send_command(command, self.command_i, 'c', _parse_response)
        return ret


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
        def _parse_response(response):
            try:
                r = map(int, response.split(','))
                return dict(zip(['R10', 'R45', 'R90', 'RB', 'LB', 'L90', 'L45',
                                'L10'], r))
            except ValueError as e:
                self.logger.error(e)

        command = "N%c\n" % self.command_i
        ret = self.comm.send_command(command, self.command_i, 'n', _parse_response)
        return ret


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
        def _parse_response(response):
            try:
                r = map(int, response.split(','))
                return dict(zip(['R10', 'R45', 'R90', 'RB', 'LB', 'L90', 'L45',
                                'L10'], r))
            except ValueError as e:
                self.logger.error(e)

        command = "O%c\n" % self.command_i
        ret = self.comm.send_command(command, self.command_i, 'o', _parse_response)
        return ret


    @command
    def set_camera(self, mode, width, height, zoom):
        """Set the camera properties.

        If the common denominator of zoom factor is 4 or 2, part of the
        subsampling is done by the camera ( QQVGA = 4, QVGA = 2 ). This
        increase the framerate by respectively 4 or 2. Moreover greyscale is
        twice faster than color mode.

        Arguments:
            mode - GREYSCALE_MODE or RGB565_MODE
            width - image width
            height - image height
            zoom - zoom factor
        """
        if 0 < width <= 640 and 0 < height <= 480 and mode in (self.GREYSCALE_MODE, self.RGB565_MODE):
            command = "J%c,%d,%d,%d,%d\n" % (self.command_i, mode, width, height, zoom)
            ret = self.comm.send_command(command, self.command_i, 'j')
            return ret
        else:
            raise WrongCommand("Wrong camera properties.")

    @command
    def get_camera(self):
        """Get the camera properties.

        Returns a dictionary with camera properties. The properites are:
            mode - GREYSCALE_MODE or RGB565_MODE
            width - image width
            height - image height
            zoom - zoom factor

        """
        def _parse_response(response):
            try:
                r = map(int, response.strip().split(','))
                return dict(zip(['mode', 'width', 'height', 'zoom'], r))
            except ValueError as e:
                self.logger.error(e)

        command = "I%c\n" % self.command_i
        ret = self.comm.send_command(command, self.command_i, 'i', _parse_response)
        return ret

    @command
    def get_photo(self):
        """Take a photo."""
        def _parse_response(response):
            mode = ord(response[0])
            width = ord(response[1]) + (ord(response[2]) << 8);
            height = ord(response[3]) + (ord(response[4]) << 8);
            image = response[5:]
            print "%dx%d" % (width, height)

            if mode == self.RGB565_MODE:
                ret = ""
                data_struct = "<BBB"

                for (hi, lo) in zip(image[0::2], image[1::2]):
                    val = (ord(hi) << 8) + ord(lo)
                    b = int(((val >> 11) & 31) / 31. * 255)
                    g = int(((val >> 5) & 63) / 63. * 255)
                    r = int((val & 31) / 31. * 255)
                    ret += struct.pack(data_struct, b, g, r)
                return Image.fromstring('RGB', (width, height), ret).rotate(90)
            elif mode == self.GREYSCALE_MODE:
                return Image.fromstring('L', (width, height), image).rotate(90)

        c = chr(256 - ord("I"))
        command = "%c%c%c" % (c, self.command_i, chr(0))
        ret = self.comm.send_command(command, self.command_i, c, _parse_response)
        return ret


    @command
    def reset(self):
        """Reset the robot."""
        command = "R%c\n" % self.command_i
        ret = self.comm.send_command(command, self.command_i, 'r')
        return ret


    @command
    def set_motor_pos(self, left, right):
        """Set motor position.

        The robot has two step motors. It is possible to set initial positions
        of the motors (two numbers) and then every step of the motor increase
        or decrease the position.

        Note: This command doesn't alter the position of motors.

        Arguments:
            left - position of left motor
            right - position of right motor

        """
        command = "P%c,%d,%d\n" % (self.command_i, left, right)
        ret = self.comm.send_command(command, self.command_i, 'p')
        return ret

    @command
    def get_motor_pos(self):
        """Read motor position.

        Returns two values, position of left and right motor.
        """
        def _parse_response(response):
            try:
                r = map(int, response.strip().split(','))
                return r
            except ValueError as e:
                self.logger.error(e)

        command = "Q%c\n" % (self.command_i)
        ret = self.comm.send_command(command, self.command_i, 'q', _parse_response)
        return ret


# Test the module.
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    a = Controller(None, asynchronous=True, timeout=20, offline=True, offline_address=('localhost',65432))
    r1 = a.set_motor_speed(100,100)
    r2 = a.get_motor_speed()
