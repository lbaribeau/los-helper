
import sys

def newConsoleHandler():
    if sys.platform == 'win32':
        from WinConsoleHandler import WinConsoleHandler
        return WinConsoleHandler()
    else:
        from UnixConsoleHandler import UnixConsoleHandler
        return UnixConsoleHandler()
