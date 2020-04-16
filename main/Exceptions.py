
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class Reboot(Exception):
    def __init__(self):
        return

    def __str__(self):
        print("server must have rebooted")
        return

class TimeoutError(Error):
    def __init__(self):
        return

    def __str__(self):
        print("Something timed out!")
        return