#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import Queue
import select
import serial
import socket                    
import threading

class RequestHandler(object):
    """Represent the request that was asynchronously called.

    The programmer can check if the request has been done.

    """

    def __init__(self, command):
        self.command = command
        self.response = None
        self.request_sent = False
        self.accomplished = threading.Condition()

    def get_command(self):
        """Return the command that was sent."""
        return command

    def set_response(self, response):
        """Set the response to the sent request. 
        
        Also notify all waiting for the request.
        
        """
        self.response = response
        self.request_sent = True
        self.accomplished.notify()

    def get_response(self):
        """Return the response."""
        return self.response

    def sent(self):
        """Return whether a response have been received."""
        return self.request_sent

    def join(self):
        """Wait until the response is received."""
        self.accomplished.wait()

class AsyncComm(threading.Thread):
    """Manage asynchronous communication with the robot.

    Save new commands to a queue and sends them to the robot as soon as
    possible. The programmer gets a handler, which he can use to access the
    results once the commands are executed.

    """

    def __init__(self, port, **kwargs):
        threading.Thread.__init__(self)

        # Create a connection to the robot.
        self.serial_connection = serial.Serial(port, **kwargs)

        # Create a pipe used to interrupt the select call.
        self.interrupt_fd_read, self.interrupt_fd_write = os.pipe()

        # Create queues for requests and responses.
        self.request_queue = Queue.Queue()
        self.response_queue = Queue.Queue()

    def start(self):
        """Start the manager as new thread."""
        self.running = True
        threading.Thread.start(self)

    def stop(self):
        """Stop the main loop."""
        os.write(self.interrupt_fd_write, "STOP")

    def run(self):
        """The main loop of the communication manager.

        Call select and wait till the robot send something or the user has some
        commands to send to the robot.

        """
        while self.running:
            input_sockets = [self.serial_connection, self.interrupt_fd_read]
            input_sockets, _, _ = select.select(input_sockets, [], [])
            for i in input_sockets:
                # The user wants to send a command.
                if i == self.interrupt_fd_read:
                    self.process_interrupt()
                # The robot is sending response.
                elif i == self.serial_connection:
                    self._read_response()

    def process_interrupt(self):
        """Process the interrupt from main loop.

        The interrupt can be sending new command or terminating the main loop.

        """
        # Read the command.
        command = os.read(self.interrupt_fd_read, 0xff)
        command_handlers = {
            'NEW': self._write_request,
            'STOP': self._stop_main_loop,
        }
        command_handlers[command]()

    def send_command(self, command):
        """Create new request and notify the main loop.
        
        The main loop called select on a pipe. To notify the main loop write
        something to the pipe. The sent data are not parsed.
        
        """
        request = RequestHandler(command)
        self.request_queue.put(request)
        os.write(self.interrupt_fd_write, "NEW")

    def _write_request(self):
        """Write the request to the serial connection."""
        # Remove the request from queue.
        request = self.request_queue.get()
        # Send the request to the robot.
        self.serial_connection.write(request.get_command())
        # Add the request to another queue to wait for response.
        self.response_queue.put(request)

    def _read_response(self):
        pass



