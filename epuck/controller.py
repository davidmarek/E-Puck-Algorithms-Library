import serial

class Controller:

    def __init__(self, com):
        """Creates new connection with e-puck robot. 
            com - port where the robot is connected."""
        # Serial connection
        self.serial_connection = serial.Serial(port=com, baudrate=115200, timeout=0)

