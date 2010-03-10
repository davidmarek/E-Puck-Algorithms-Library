#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Low level control of E-Puck robot."""

import serial
import sys
import logging

class Controller:

    """Control E-Puck robot.

    Give commands to e-puck robot via bluetooth connection. Use BTcom 
    tool and its text protocol. 

    """

    def __init__(self, port):
        """Create new connection with e-puck robot. 

        Keyword arguments:
        port -- port where the robot is connected, e.g. /dev/rfcomm0.

        """
        # All messages are logged using the logging module.
        self.logger = logging.getLogger('EPuck.controller.Controller')

        # Creates serial connection, 
        try:
            self.serial_connection = serial.Serial(
                port=port,       # Port, where e-puck is connected.
                baudrate=115200, # E-puck baudrate.
                bytesize=8,      # E-puck bytesize.
                timeout=0        # readline won't block execution.
            )
        except serial.serialutil.SerialException:
            self.logger.error("E-Puck seems to be offline.")
            sys.exit(1)
        self.logger.info("E-Puck connected.")


