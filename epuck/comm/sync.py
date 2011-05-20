#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import serial

from epuck.comm import CommError


class SyncCommError(CommError):
    """An error occured during the synchronous communication."""
    pass


class SyncComm(object):
    """Manage asynchronous communication with the robot.

    Simple and transparent layer between the controller and the robot.

    """

    def __init__(self, port, timeout=0.5, **kwargs):
        # Create a connection to the robot.
        # It is possible to test this class without robot using sockets.
        try:
            self.serial_connection = serial.Serial(port, timeout=timeout, **kwargs)
            self.serial_connection.write('\r')
            self.serial_connection.readline()
        except serial.SerialException as e:
            raise SyncCommError(e.message)

        self.logger = logging.getLogger('SyncComm')

    def send_command(self, command, timestamp, command_code, callback=lambda x:x):
        """Send new command and return the response.

        Will block the execution until the robot returns something or timeout
        occurs.

        """
        self.logger.debug('Sending new command. Command: "%s", code: "%s", timestamp: "%s".' % (command, command_code, timestamp))

        self.serial_connection.write(command)

        response = None
        while response is None:
            response = self._read_response(timestamp, command_code)

        return callback(response)

    def _read_response(self, timestamp, command_code):
        """Read a response."""
        code = self.serial_connection.read(1)

        try:
            # Binary data
            if ord(code) >= 127:
                ts = ord(self.serial_connection.read(1))
                response = self._read_binary_data()
            # Text data
            else:
                ts = ord(self.serial_connection.read(1))
                response = self._read_text_data().split(",", 1)
                try:
                    response = response[1]
                except IndexError:
                    response = ''
        except TypeError:
            raise SyncCommError("No response received")

        self.logger.debug('Received response. Code: "%s", timestamp: "%s", response: "%s".' % (code, ts, response))

        if ts == timestamp and command_code == code:
            return response
        else:
            return None

    def _read_binary_data(self):
        """Read binary data from the robot.

        Some responses are binary. The robot first sends 2 bytes containing the
        size of the data. The data then follows.

        """
        lo, hi = self.serial_connection.read(2)
        size = (ord(hi) << 8) + ord(lo)
        data = self.serial_connection.read(size)
        return data

    def _read_text_data(self):
        """Read a text response from the robot.

        Some responses are text terminated by newline character.

        """
        data = self.serial_connection.readline()
        return data

