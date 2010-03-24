#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low level control of E-Puck robot."""

import re
import serial
import sys
import logging
import time
import datetime

class EPuckError(Exception):
    """Base class exception for this library."""

    def __init__(self, message):
        """Create E-Puck exception.

        Arguments:
            message -- Description of what went wrong.

        """
        self.message = message

    def __str__(self):
        return self.message

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
        #Initialize atributes
        self._left_motor_speed = 0  # Speed of left wheel
        self._right_motor_speed = 0 # Speed of right wheel

        # All messages are logged using the logging module.
        self.logger = logging.getLogger('epuck.controller.Controller')

        # Create serial connection to e-puck. 
        try:
            self.serial_connection = serial.Serial(
                port=port,       # Port, where e-puck is connected.
                baudrate=115200, # E-puck baudrate.
                bytesize=8,      # E-puck bytesize.
                timeout=0.1      # readline won't block execution.
            )
        except serial.serialutil.SerialException:
            self.logger.error("E-Puck seems to be offline.")
            raise ControllerError("E-Puck seems to be offline.")
        self.logger.info("E-Puck connected.")

    def _send_command(self, command, expected_prefix):
        """Send command and return response.
        
        """
        # Send the command to e-puck.
        self.logger.debug("Command:" + command)
        self.serial_connection.write(command)

        # Read the response from e-puck.
        # This code was added when e-puck with low battery didn't listen.
        # Most probably such tests aren't needed, but BEWARE OF LOW BATTERY!!!
        response = ""
        start = datetime.datetime.now()
        while not response.startswith(expected_prefix):
            response = self.serial_connection.readline() 
            if ("WELCOME" in response) or (datetime.datetime.now() - start).seconds > 1:
                self.serial_connection.write(command)
                start = datetime.datetime.now()
            self.logger.debug("Answer: " + response)

        return response



    def set_motor_speed(self, left, right):
        """Set speed of motors.
        
        """
        # Check if the speeds are smaller than MAX_SPEED
        if (-self.MAX_SPEED <= left <= self.MAX_SPEED) and \
           (-self.MAX_SPEED <= right <= self.MAX_SPEED):

            response = self._send_command("D,%d,%d\r" % (left, right), "d")

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

        """
        response = self._send_command("E\r", "e")

        # The response should be "e,left_speed,right_speed"
        regexp = re.compile(r'^e,(-?\d+),(-?\d+)')
        match = regexp.match(response)
        if match:
            _left_motor_speed = match.groups()[0]
            _right_motor_speed = match.groups()[1]
        else:
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

if __name__ == '__main__':
    import logging
    
    logging.basicConfig(level=logging.DEBUG)
    
    r = Controller('/dev/rfcomm0')
