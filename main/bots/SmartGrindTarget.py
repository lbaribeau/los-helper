class SmartGrindTarget(object):
	def __init__(self, name, locations):
		self.name = name
		self.locations = locations

	def to_string(self):
		return self.name #+ ", " + str(self.locations)