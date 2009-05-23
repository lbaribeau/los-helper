import sys

def newConsoleHandler():
	if sys.platform == 'win32':
		from WinConsoleHandler import *
		return WinConsoleHandler()
	else:
		from UnixConsoleHandler import *
		return UnixConsoleHandler()

