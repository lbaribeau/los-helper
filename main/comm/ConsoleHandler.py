
import sys

def newConsoleHandler():
    if sys.platform == 'win32':
        from comm.WinConsoleHandler import WinConsoleHandler
        return WinConsoleHandler()
    else:
        from comm.UnixConsoleHandler import UnixConsoleHandler
        return UnixConsoleHandler()
