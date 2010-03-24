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

    def set_motor_speed(self, left, right):
        """Set speed of motors.
        
        The speed is measured in pulses per second, one pulse is 
        aproximately 0.13mm. The speed can be in range 
        (-MAX_SPEED, MAX_SPEED). 

        """
        # Check if the speeds are smaller than MAX_SPEED
        if (-self.MAX_SPEED <= left <= self.MAX_SPEED) and \
           (-self.MAX_SPEED <= right <= self.MAX_SPEED):

            # Send command to e-puck.
            self.logger.debug("Command: D,%d,%d" % (left, right))
            self.serial_connection.write("D,%d,%d\n" % (left, right))

            # Read response from e-puck.
            response = self.serial_connection.readline()
            self.logger.debug("Answer: "+response)

            # The response should be "d".
            if response.startswith("d"):
                self._left_motor_speed = left
                self._right_motor_speed = right

            elif "WELCOME" in response:
                # E-Puck apparently thought it's nice to greet us again. 
                # It did what we wanted, but sent us another line with help.
                self._left_motor_speed = left
                self._right_motor_speed = right

                # Log the rest of greeting.
                response = self.serial_connection.readline()
                self.logger.debug("Answer: "+response)

            else:
                self.logger.error("Wrong answer from e-puck")
                raise ControllerError("Wrong answer from e-puck")

        else:
            self.logger.error("Speed out of range.")
            raise ControllerError("Speed out of range.")

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

