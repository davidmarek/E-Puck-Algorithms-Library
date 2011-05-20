__all__ = ['Controller', 'EPuckError', 'ControllerError', 'WrongCommand']

class EPuckError(Exception):
    """Base class exception for this library."""

    def __init__(self, message):
        """Create E-Puck exception.

        Arguments:
            message -- Description of what went wrong.

        """
        if isinstance(message, EPuckError):
            self.message = message.message
        else:
            self.message = message

    def __str__(self):
        return repr(self.message)

from controller import ControllerError, WrongCommand, Controller

