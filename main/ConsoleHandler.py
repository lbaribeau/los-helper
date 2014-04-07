import sys
from UnixConsoleHandler import *
from WinConsoleHandler import *

def newConsoleHandler():
    if sys.platform == 'win32':
        return WinConsoleHandler()
    else:
        return UnixConsoleHandler()

