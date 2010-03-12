#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low level control of E-Puck robot."""

import serial
import sys
import logging

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
                timeout=0        # readline won't block execution.
            )
        except serial.serialutil.SerialException:
            self.logger.error("E-Puck seems to be offline.")
            raise ControllerError("E-Puck seems to be offline.")
        self.logger.info("E-Puck connected.")

    @property
    def left_motor_speed(self):
        """The speed of left motor. 
        
        The speed is measured in pulses per second, one pulse is 
        aproximately 0.13mm. The speed can be in range 
        (-MAX_SPEED, MAX_SPEED). 
        
        It could have been saved only when changed and this method could
        just return internal representation, but it's more reliable to 
        actually read the speed from e-puck's memory.

        """
        self.logger.debug("Command: E.")
        # Send command to e-puck.
        self.serial_connection.write("E\n")
        # Read response from e-puck.
        response = self.serial_connection.readline() 
        self.logger.debug("Answer: "+response)
        # The response should be in format: "e,left_speed,right_speed".
        # Check the response and set the internal representation.
        resp_token = response.split(",")
        if len(resp_token) == 3 and resp_token[0] == "e":
            self._left_motor_speed = int(resp_token[1])
            return self._left_motor_speed
        else:
            self.logger.error("Wrong answer from e-puck")
            raise ControllerError("Wrong answer from e-puck.")

    @left_motor_speed.setter
    def left_motor_speed(self, new_speed):
        self.logger.debug("Command: D,%d,%d" % (new_speed, _right_motor_speed))
        # Send command to e-puck.
        self.serial_connection.write("D,%d,%d\n" % 
            (new_speed, _right_motor_speed))
        # Read response from e-puck.
        response = self.serial_connection.readline()
        self.logger.debug("Answer: "+response)
        # The response should be "d".
        if response.startswith("d"):
            self._left_motor_speed = new_speed
        else:
            self.logger.error("Wrong answer from e-puck")
            raise ControllerException("Wrong answer from e-puck")

