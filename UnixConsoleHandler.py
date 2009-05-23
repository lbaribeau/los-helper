class UnixConsoleHandler:

	def set_color(self, color, handle='FIXME'):
		#not used in WinConsoleHandler anyway
		raise Exception('not implemented')
# set_color

# win_console.py

	def black(self):
		print "\033[30m"
		return
	def blue(self):
		print "\033[34m"
		return
	def green(self):
		print "\033[32m"
		return
	def cyan(self):
		print "\033[36m"
		return
	def red(self):
		print "\033[31m"
		return
	def magenta(self):
		print "\033[35m"
		return
	def yellow(self):
		print "\033[33m"
		return
	def white(self): 
		print "\033[37m"
		return    

	#TODO: we could use something like bold(\033[1m) for bright, but there's no
	#way to reset it without also resetting the color
	#we can get around this by having this class remember it's color and then reset it
	#but I'll leave that for later -kb
	def set_bright(self):                      
		pass
	def set_dark(self):
		pass

