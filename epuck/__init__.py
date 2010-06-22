__all__ = ["controller"]

class EPuckError(Exception):
    """Base class exception for this library."""

    def __init__(self, message):
        """Create E-Puck exception.

        Arguments:
            message -- Description of what went wrong.

        """
        self.message = message

    def __str__(self):
        return self.message

