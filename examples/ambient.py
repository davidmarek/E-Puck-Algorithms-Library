import logging
import time
import sys
import signal

from epuck.controller import Controller

logging.basicConfig(level=logging.WARNING)

c = Controller('/dev/rfcomm0', asynchronous=True, timeout=5, max_tries=1)

# Signal handler to cleanup after shutdown
def handle_signal(signum, frame):
    r = c.stop()
    r.join()
    sys.exit(0)

# SIGINT is interrupt signal sent by CTRL+C
signal.signal(signal.SIGINT, handle_signal)


while True:
    # Read ambient light sensors
    r = c.get_ambient_sensors().get_response()

    front_side = r['L10'] + r['R10']
    left_side = r['L45'] + r['L90']
    right_side = r['R45'] + r['R90']

    # The light source is straight ahead
    if front_side < left_side and front_side < right_side:
        c.set_speed(500, 500)
    # Turn left
    elif left_side < right_side:
        c.set_speed(-500, 500)
    # Turn right
    else:
        c.set_speed(500, -500)

    time.sleep(0.1)

