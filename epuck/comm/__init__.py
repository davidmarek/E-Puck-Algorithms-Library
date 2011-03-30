#!/usr/bin/python
# -*- coding: utf-8 -*-

__all__ = ['CommError']

import socket

from epuck import EPuckError

class CommError(EPuckError):
    """
    An error occured during the communication with E-Puck robot.

    """
    pass

from async import RequestHandler, AsyncCommError, AsyncComm
from sync import SyncCommError, SyncComm

