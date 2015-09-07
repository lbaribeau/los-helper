
# The solution
#  1) Check terminal options to ensure that sound can be played
#  2) print('\a')

import sys

class SoundHandler(object):
	def __init__(self):
		if sys.platform == 'win32':
			return WinSoundHandler()
		else:
			return UnixSoundHandler()

class WinSoundHandler(SoundHandler):
	def alert(self):
		import winsound
		winsound.Beep(500,100)

class UnixSoundHandler(SoundHandler):
	def alert(self):



