import logging
import time

from epuck.controller import Controller

logging.basicConfig(level=logging.ERROR)

c = Controller('/dev/rfcomm0', asynchronous=False, timeout=5, max_tries=10)
s = c.comm.serial_connection
