
import sys

def newConsoleHandler():
    if sys.platform == 'win32':
        from main.comm.WinConsoleHandler import WinConsoleHandler
        return WinConsoleHandler()
    else:
        from main.comm.UnixConsoleHandler import UnixConsoleHandler
        return UnixConsoleHandler()
