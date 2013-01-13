
class MyMudWaiterFlags:
	
	def __init__(self):
		self.waitflag = False
		self.returnval = False	
			# Returnval has to tell the poller something about what text came.
			# For example the killthread might wonder whether to stop itself or not, 
			# which depends on whether the monster died, and that information will 
			# be in the returnval.
			

