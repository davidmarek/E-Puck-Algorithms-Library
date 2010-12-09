#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import Queue
import select
import serial
import socket                    
import threading
import time


class AsyncCommError(EPuckError): 
    """
    An error occured during the asynchronous communication with E-Puck robot.
    
    """
    pass


class RequestHandler(object):
    """Represent the request that was asynchronously called.

    The programmer can check if the request has been done.

    """

    def __init__(self, command, response_code):
        self.command = command
        self.response = None
        self.response_received = False
        self.response_code = response_code
        self.accomplished = threading.Condition()

    def get_command(self):
        """Return the command that was sent."""
        return command

    def own_response(self, code):
        return code == self.response_code

    def set_response(self, response):
        """Set the response to the sent request. 
        
        Also notify all waiting for the request.
        
        """
        self.response = response
        self.response_received = True
        self.accomplished.notify()

    def get_response(self):
        """Return the response."""
        return self.response

    def done(self):
        """Return whether a response have been received."""
        return self.response_received

    def join(self):
        """Wait until the response is received."""
        self.accomplished.wait()


class AsyncComm(threading.Thread):
    """Manage asynchronous communication with the robot.

    Save new commands to a queue and sends them to the robot as soon as
    possible. The programmer gets a handler, which he can use to access the
    results once the commands are executed.

    """

    def __init__(self, port, timeout=0.2, **kwargs):
        threading.Thread.__init__(self)

        # Create a connection to the robot.
        self.serial_connection = serial.Serial(port, **kwargs)

        # Create a pipe used to interrupt the select call.
        self.interrupt_fd_read, self.interrupt_fd_write = os.pipe()

        # Create queues for requests and responses.
        # Stored are only the requests.
        self.request_queue = Queue.Queue()
        # Stored are tuples (timestamp, request).
        self.response_queue = Queue.PriorityQueue()

        # Requests that are older than timeout seconds must be sent again.
        self.timeout = timeout

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
            input_sockets, _, _ = select.select(input_sockets, [], [], self.timeout)
            
            if len(input_sockets) == 0:
                # Timeout was reached. Check the requests.
                self._check_requests_timeout(self)

            for i in input_sockets:
                # The user wants to send a command.
                if i == self.interrupt_fd_read:
                    self._process_interrupt()
                # The robot is sending response.
                elif i == self.serial_connection:
                    self._read_response()

    def _process_interrupt(self):
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
        self._enqueue_request(request)

    def _write_request(self):
        """Write the request to the serial connection."""
        # Remove the request from queue.
        request = self.request_queue.get()
        # Send the request to the robot.
        self.serial_connection.write(request.get_command())
        # Add the request to another queue to wait for response.
        self.response_queue.put((time.time(), request))

    def _read_response(self):
        """Read the response from robot and remove the command from queue."""
        code = self.serial_connection.read(1)

        if ord(code) >= 127:
            response = self._read_binary_data()
        else:
            response = self._read_text_data()

        self._save_response(code, response)

    def _read_binary_data(self):
        lo, hi = self.serial_connection.read(2)
        size = hi << 8 + lo
        data = self.serial_connection.read(size)
        return data

    def _read_text_data(self):
        data = self.serial_connection.readline()
        return data

    def _save_response(self, code, response):
        request = self._get_request(code)
        request.set_response(response)

    def _get_request(self, code):
        while not self.response_queue.empty():
            sent_time, first_request = self.response_queue.get()

            if first_request.own_response(code):
                return first_request
            else:
                # E-puck process tasks synchronously, that means this request
                # hasn't been sent.
                self._enqueue_request(first_request)

        raise AsyncCommError("No request found for received response.")

    def _check_requests(self):
        old_requests = True
        while old_requests:
            sent_time, request = self.response_queue.get()
            if time.time() - sent_time > self.timeout:
                self._enqueue_request(request)
            else: 
                self.response_queue.put((sent_time, request))
                old_requests = False

    def _enqueue_request(self, request):
        self.request_queue.put(request)
        os.write(self.interrupt_fd_write, "NEW")
        

