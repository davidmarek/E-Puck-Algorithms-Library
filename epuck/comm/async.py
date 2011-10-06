#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import Queue
import select
import serial
import threading
import time

from epuck.comm import CommError, create_socket_pair


class AsyncCommError(CommError):
    """An error occured during the asynchronous communication."""
    pass


class RequestHandler(object):
    """Represent the request that was asynchronously called.

    The programmer can check if the request has been done.

    """

    def __init__(self, command, response_code, timestamp, callback):
        self.command = command
        self.timestamp = timestamp
        self.response_code = response_code
        self.callback = callback
        self.tries = 0
        self.error = None

        self.response = None
        self.accomplished = threading.Condition()
        self.logger = logging.getLogger('RequestHandler')

    def get_command(self):
        """Return the command that was sent."""
        return self.command

    def own_response(self, code, timestamp):
        """Decide whether the code belongs to this request."""
        return code == self.response_code and self.timestamp == timestamp

    def set_response(self, response):
        """Set the response to the sent request.

        Also notify all waiting for the request.

        """
        self.response = self.callback(response)

        self.accomplished.acquire()
        self.accomplished.notify()
        self.accomplished.release()

    def set_error(self, error):
        """Save the exception that occured during communication."""
        self.error = error

        self.accomplished.acquire()
        self.accomplished.notify()
        self.accomplished.release()

    def get_response(self):
        """Return the response."""
        if not self.response_received():
            self.join()

        if self.error is not None:
            raise self.error

        return self.response

    def response_received(self):
        """Return whether a response has been received."""
        return self.response is not None

    def error_raised(self):
        """Return whether an exception occured."""
        return self.error is not None

    def join(self):
        """Wait until the response is received."""
        self.accomplished.acquire()
        self.accomplished.wait()
        self.accomplished.release()

        if self.error is not None:
            raise self.error


class AsyncComm(threading.Thread):
    """Manage asynchronous communication with the robot.

    Save new commands to a queue and sends them to the robot as soon as
    possible. The programmer gets a handler, which he can use to access the
    results once the commands are executed.

    """

    def __init__(self, port, timeout=0.5, max_tries=10, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = True

        try:
            self.serial_connection = serial.Serial(port, **kwargs)
            self.serial_connection.write('\r')
        except serial.SerialException as e:
            raise AsyncCommError(e.message)

        # Create a socket pair used to interrupt the select call.
        self.interrupt_fd_read, self.interrupt_fd_write = create_socket_pair()

        # Create queues for requests and responses.
        # Stored are only the requests.
        self.request_queue = Queue.Queue(100)
        # Stored are tuples (time of insertion, request).
        self.response_queue = Queue.PriorityQueue(100)

        # Requests that are older than timeout seconds must be sent again.
        self.timeout = timeout

        # Set the max limit of retries.
        self.max_tries = max_tries

        self.logger = logging.getLogger('AsyncComm')

    def start(self):
        """Start the manager as new thread."""
        self.running = True
        threading.Thread.start(self)

    def stop(self):
        """Stop the main loop."""
        self.interrupt_fd_write.send("STOP\n")

    def run(self):
        """The main loop of the communication manager.

        Call select and wait till the robot sends something or the user has
        some commands to send to the robot.

        """
        self.logger.debug('Starting main loop.')

        while self.running:
            input_sockets = [self.serial_connection, self.interrupt_fd_read]
            input_sockets, _, _ = select.select(input_sockets, [], [], self.timeout)

            if len(input_sockets) == 0:
                # Timeout was reached. Check the requests.
                self._check_requests_timeout()

            for i in input_sockets:
                # The user wants to send a command.
                if i == self.interrupt_fd_read:
                    self._process_interrupt()

                # The robot is sending response.
                elif i == self.serial_connection:
                    self._read_response()

    def _stop_main_loop(self):
        """Stop the main loop."""
        self.running = False

    def _process_interrupt(self):
        """Process the interrupt from the main loop.

        The interrupt can be:
            'NEW' = send new command
            'STOP' = terminate the main loop

        """
        # Read the command.
        commands = self.interrupt_fd_read.recv(65536).strip().split('\n')

        command_handlers = {
            'NEW': self._write_request,
            'STOP': self._stop_main_loop,
        }
        # Run correct handler.
        for c in commands:
            command_handlers[c]()

    def send_command(self, command, timestamp, command_code, callback=lambda x: x):
        """Create new request and notify the main loop."""
        self.logger.debug('Sending new command. Command: "%s", code: "%s", timestamp: "%s".' % (command, command_code, timestamp))
        request = RequestHandler(command, command_code, timestamp, callback)
        self._enqueue_request(request)
        return request

    def _write_request(self):
        """Write the request to the serial connection."""
        # Remove the request from queue.
        request = self.request_queue.get()

        # Send the request to the robot.
        command = request.get_command()
        self.serial_connection.write(command)

        # Add the request to another queue to wait for response.
        try:
            self.response_queue.put((time.time(), request), False)
        except Queue.Full:
            raise AsyncCommError("Too many requests.")

    def _read_response(self):
        """Read a response and save it."""
        code = self.serial_connection.read(1)

        try:
            # Binary data
            if ord(code) >= 127:
                timestamp = ord(self.serial_connection.read(1))
                response = self._read_binary_data()
            # Text data
            else:
                response = self._read_text_data().split(',', 1)
                timestamp = ord(response[0][0])
                try:
                    response = response[1]
                except IndexError:
                    response = ''
        except TypeError as e:
            raise AsyncCommError("No response received: "+str(e))

        if code == 'z':
            # Command not found
            return


        self.logger.debug('Received response. Code: "%s", timestamp: "%s", response: "%s".' % (code, timestamp, response))

        self._save_response(code, timestamp, response)


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

    def _save_response(self, code, timestamp, response):
        """Find the right request and give it the response."""
        request = self._get_request(code, timestamp)
        if request is not None:
            request.set_response(response)

    def _get_request(self, code, timestamp):
        """Find the right request for given response code."""
        while not self.response_queue.empty():
            sent_time, first_request = self.response_queue.get()

            if first_request.own_response(code, timestamp):
                return first_request
            else:
                # E-puck process tasks synchronously, that means this request
                # hasn't been sent.
                self._enqueue_request(first_request)

        return None

    def _check_requests_timeout(self):
        """Check if requests are not waiting too long.

        If there is a request waiting longer than the timeout limit, assume the
        message was lost and send it again.

        """
        old_requests = True
        while old_requests and not self.response_queue.empty():
            sent_time, request = self.response_queue.get()
            if time.time() - sent_time > self.timeout:
                if request.tries < self.max_tries:
                    request.tries += 1
                    self._enqueue_request(request)
                    self.logger.debug("Timeout exceeded: Sending command again: %s" % request.command)
                else:
                    self.logger.error("Max limit exceeded.")
                    request.set_error(AsyncCommError("Max limit exceeded."))
            else:
                try:
                    self.response_queue.put((sent_time, request), False)
                except Queue.Full:
                    self.logger.error("Too many requests.")
                    request.error = AsyncCommError("Too many requests.")
                old_requests = False

    def _enqueue_request(self, request):
        "Put the request into the request_queue and notify the main loop."""
        try:
            self.request_queue.put(request, False)
        except Queue.Full:
            raise AsyncCommError("Too many requests.")
        self.interrupt_fd_write.send("NEW\n")


# Test the module.
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    a = AsyncComm(None, timeout=20, offline=True, offline_address=('localhost',65432))
    a.start()
    while True:
        command = raw_input('> ')
        a.send_command(command, int(command.split(',', 1)[0][1:]), command[0])
        print

