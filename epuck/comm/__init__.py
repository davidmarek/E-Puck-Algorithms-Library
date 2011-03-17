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


class TestConnection(socket.socket):
    """
    Socket acting like a serial connection for testing purposes.

    """

    def read(self, buffer_size):
        return self.recv(buffer_size)

    def readline(self):
        return self.recv(65536)

    def write(self, msg):
        self.send(msg)

from async import RequestHandler, AsyncCommError, AsyncComm
from sync import SyncCommError, SyncComm

