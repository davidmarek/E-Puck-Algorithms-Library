#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from comm.async import AsyncComm
from comm.sync import SyncComm
from epuck import EPuckError


class ControllerError(EPuckError):
    """
    E-Puck robot is not responding as it should.

    """
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

    def __init__(self, port, asynchronous=False, **kwargs):
        """Create new controller.

        Arguments:
            port -- The device where e-puck robot is connected (e.g. /dev/rfcomm0).
            asynchronous -- Use asynchronous or synchronous communication.

        """

        if asynchronous:
            self.comm = comm.async.AsyncComm(port, **kwargs)
        else:
            self.comm = comm.sync.SyncComm(port, **kwargs)

        self.motor_speed = [0, 0]
        self.body_led = False
        self.front_led = False
        self.leds = 8 * [False]



