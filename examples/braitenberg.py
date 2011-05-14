#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import signal
import sys

from epuck import Controller, WrongCommand

logging.basicConfig(level=logging.WARNING)

c = Controller('/dev/rfcomm0', asynchronous=True)

bias = 200
too_close = 2000
max_speed = 1000
min_speed = -1000

# Signal handler to cleanup after shutdown
def handle_signal(signum, frame):
    r = c.set_speed(0,0)
    r.join()
    sys.exit(0)

# SIGINT is interrupt signal sent by CTRL+C
signal.signal(signal.SIGINT, handle_signal)

while True:
    # Read values from proximity sensors
    r = c.get_proximity_sensors()
    r = r.get_response()

    left_sensors = r['L10'] + r['L45'] + r['L90'] + bias
    right_sensors = r['R10'] + r['R45'] + r['R90'] + bias

    left_speed = left_sensors if right_sensors < too_close else -left_sensors
    right_speed = right_sensors if left_sensors < too_close else -right_sensors

    if left_speed > max_speed: left_speed = max_speed
    if left_speed < min_speed: left_speed = min_speed
    if right_speed > max_speed: right_speed = max_speed
    if right_speed < min_speed: right_speed = min_speed

    try:
        c.set_speed(left_speed, right_speed)
    except WrongCommand:
        pass

    time.sleep(0.1)

