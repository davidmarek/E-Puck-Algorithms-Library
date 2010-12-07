#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low level control of E-Puck robot."""

import serial
import logging
import time

from epuck import EPuckError
class ControllerError(EPuckError):
    """Controller exception, E-puck robot probably not responding."""
    pass

class Controller(object):
    """Control E-Puck robot.

    Give commands to e-puck robot via bluetooth connection. Use BTcom 
    tool and its text protocol. 

    Atributes:
        MAX_SPEED -- Maximum speed of e-puck's motors measured in 
                     pulses per second. -MAX_SPEED is maximum backward 
                     speed.

    """

    MAX_SPEED = 1000 

    def __init__(self, port):
        """Create new connection with e-puck robot. 

        Arguments:
            port -- port where the robot is connected, e.g. /dev/rfcomm0.

        """
        # Initialize atributes

        # Initialize motor speed
        self._left_motor_speed = 0  # Speed of left wheel
        self._right_motor_speed = 0 # Speed of right wheel

        # Initialize body led
        self._body_led = False

        # All messages are logged using the logging module.
        self.logger = logging.getLogger('epuck.controller.Controller')

        # Create serial connection to e-puck. 
        try:
            self.serial_connection = serial.Serial(
                port=port,       # Port, where e-puck is connected.
                baudrate=115200, # E-puck baudrate.
                bytesize=8,      # E-puck bytesize.
                timeout=0      # readline won't block execution.
            )
        except serial.serialutil.SerialException:
            self.logger.error("E-Puck seems to be offline.")
            raise ControllerError("E-Puck seems to be offline.")
        self.logger.info("E-Puck connected.")

    def _send_command(self, command):
        """Send command and return response.
        
        """
        # Send the command to e-puck.
        self.logger.debug("Command: " + str(command))
        self.serial_connection.write(command)

        response = self.serial_connection.readline() 
        self.logger.info("Response: " + str(response))

        return response

    def _check_response(self, response, expected):
        """Check if the response is what is expected.

        The e-puck robot's response always starts with the same letter
        (lowercase) as the sent command.

        """
        if not response.startswith(expected):
            self.logger.error("Wrong response.")
            raise EPuckError("Wrong response.")

################################################################################
# Speed                                                                        
################################################################################

    def set_motor_speed(self, left, right):
        """Set speed of motors.
        
        """
        # Check if the speeds are smaller than MAX_SPEED
        if (-self.MAX_SPEED <= left <= self.MAX_SPEED) and \
           (-self.MAX_SPEED <= right <= self.MAX_SPEED):

            response = self._send_command("D,%d,%d\r" % (left, right))
            self._check_response(response, 'd')

            self._left_motor_speed = left
            self._right_motor_speed = right

        else:
            self.logger.error("Speed out of range.")
            raise ControllerError("Speed out of range.")

    def get_motor_speed(self):
        """Get speed of motors.

        The speed is measured in pulses per second, one pulse is 
        aproximately 0.13mm. The speed can be in range 
        (-MAX_SPEED, MAX_SPEED). 

        Returns tuple (left motor speed, right motor speed).

        """
        response = self._send_command("E\r")
        self._check_response(response, 'e')

        try:
            _, left, right = response.split(',')

            return (int(left), int(right))

        except ValueError:
            self.logger.error("Wrong answer from e-puck.")
            raise ControllerError("Wrong answer from e-puck.")

    @property
    def left_motor_speed(self):
        """The speed of left motor. 

        The returned speed is obtained from internal representation.
        These values may be incorrect if you are not using only functions from
        this library to control E-Puck Robot.

        """
        return self._left_motor_speed


    @left_motor_speed.setter
    def left_motor_speed(self, new_speed):
        """Set only left motor's speed.

        The right motor's speed is not changed, it's used from internal
        representation.
        
        """
        self.set_motor_speed(new_speed, self.right_motor_speed)

    @property
    def right_motor_speed(self):
        """The speed of right motor. 
        
        The returned speed is obtained from internal representation.
        These values may be incorrect if you are not using only functions from
        this library to control E-Puck Robot.

        """
        return self._right_motor_speed


    @right_motor_speed.setter
    def right_motor_speed(self, new_speed):
        """Set only right motor's speed.

        The left motor's speed is not changed, it's used from internal
        representation.
        
        """
        self.set_motor_speed(self.left_motor_speed, new_speed)

################################################################################
# LEDs
################################################################################

    @property
    def body_led(self):
        """The green body LED's status.
        
        """
        return self._body_led

    @body_led.setter
    def body_led(self, turn_on):
        """Set the green body LED's status.

        Arguments:
            turn_on - whether turn on or off the body LED.

        """
        response = self._send_command('B,%d\r' % int(turn_on))
        self._check_response(response, 'b')

        self._body_led = turn_on


    @property
    def front_led(self):
        """The red front LED's status.

        """
        return self._front_led

    @front_led.setter
    def front_led(self, turn_on):
        """Set the red front LED's status.

        Arguments:
            turn_on - whether turn on or off the body LED.

        """
        response = self._send_command('F,%d\r' % int(turn_on))
        self._check_response(response, 'f')

        self._front_led = turn_on


    def set_led_state(self, led_no, turn_on):
        """Set the LED's status.

        There are 8 LEDs on the e-puck robot. The LED number 0 is the frontal
        one, the LED numbering is increasing clockwise.

        Arguments:
            led_no - the number of the affected LED.
            turn_on - whether turn on or off the chosen LED.

        """
        if 0 <= led_no <= 8:
            response = self._send_command('L,%d,%d\r' % (led_no, int(turn_on)))
            self._check_response(response, 'l')

        else:
            self.logger.error('LED number out of range.')
            raise ControllerError('LED number out of range.')

################################################################################
# Turning switch
################################################################################

    @property
    def turning_switch(self):
        """The position of the rotating 16 positions switch.

        Position 0 correspond to the arrow pointing on the right when looking
        in the same direction as the robot.

        """
        response = self._send_command('C\r')
        self._check_response(response, 'c')

        try:
            c, position = response.split(',')

            return int(position)

        except ValueError:
            self.logger.error('Wrong response.')
            raise ControllerError('Wrong response.')

################################################################################
# Proximity sensors
################################################################################

    @property
    def proximity_sensors(self):
        """The values of the 8 proximity sensors.

        The 12 bit values of the 8 proximity sensors. For left and right side
        there is one sensor situated 10 degrees from the front, others are 45
        degrees and 90 degrees from the front. For each side there is also one
        sensor on the back side.

        The keys for sensor values are following: L10, L45, L90, LB, R10, R45,
        R90, RB.

        The values are in range [0, 4095].
        
        """
        response = self._send_command('N\r')
        self._check_response(response, 'n')

        try:
            r = response.split(',')

            return dict(zip(['R10', 'R45', 'R90', 'RB', 'LB', 'L90', 'L45',
                             'L10'], r[1:]))

        except ValueError:
            self.logger.error('Wrong response.')
            raise ControllerError('Wrong response.')

################################################################################
# Ambient light sensors
################################################################################

    @property
    def ambient_light_sensors(self):
        """The values of the 8 ambient light sensors.

        The 12 bit values of the 8 ambient light sensors. For left and right
        side there is one sensor situated 10 degrees from the front, others are
        45 degrees and 90 degrees from the front. For each side there is also
        one sensor on the back side.

        The keys for sensor values are following: L10, L45, L90, LB, R10, R45,
        R90, RB.

        The values are in range [0, 4095].

        """
        response = self._send_command('N\r')
        self._check_response(response, 'n')

        try:
            r = response.split(',')

            return dict(zip(['R10', 'R45', 'R90', 'RB', 'LB', 'L90', 'L45',
                             'L10'], r[1:]))

        except ValueError:
            self.logger.error('Wrong response.')
            raise ControllerError('Wrong response.')

    
################################################################################
# Camera
################################################################################

    def get_image(self):
        self.serial_connection.write(chr(183)+chr(0))
        x = self.serial_connection.read(3)
        print x
        size = ord(x[1]) * ord(x[2]) * 2
        with open('image', 'w') as f:
            f.write(self.serial_connection.read(size))

if __name__ == '__main__':
    import logging
    
    logging.basicConfig(level=logging.DEBUG)
    
    r = Controller('/dev/rfcomm0')
