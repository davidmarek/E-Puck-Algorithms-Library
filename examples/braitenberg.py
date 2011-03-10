#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import signal
import sys

from epuck.controller import Controller

logging.basicConfig(level=logging.DEBUG)

c = Controller('/dev/rfcomm2', asynchronous=True)

# The robot should move even when there are no obstacles
bias = 100
# Inputs larger than threshold means there is an obstacle
threshold = 300

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
    # Compute the speed of wheels based on proximity sensors
    left_speed = r['L10'] + r['L45'] + r['L90'] + bias
    right_speed = r['R10'] + r['R45'] + r['R90'] + bias

    # Correct too large values
    if left_speed > 1000: left_speed = 1000
    if right_speed > 1000: right_speed = 1000

    # Fix for obstacles right in front of the robot
    if (r['L10'] > threshold) and (r['R10'] > threshold):
        c.set_speed(-right_speed, right_speed)
    else:
        c.set_speed(left_speed, right_speed)

    time.sleep(0.1)

