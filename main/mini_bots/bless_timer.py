
import re
import time

from comm import RegexStore as R
from misc_functions import magentaprint

class Timer:
	# Abstract class
	# Have children define on/off regexes
	# Well we don't have to have the abstract part
	timer = time.time()
	refresh = 480 # 8 minutes

	def __init__(self, use, inventory):
		self.use       = use
		self.inventory = inventory
		self.timer     = time.time()
		self.on        = None # TODO: set blessed boolean on startup

	def print_timer(self):
		magentaprint("Timer %s intending next one in %d seconds, \"on\" is %s." % (self.__class__.__name__, round(self.timer + self.refresh - time.time()), self.on))

	def check_timer(self):
		return time.time() > self.timer + self.refresh

class BlessTimer(Timer):
	# self.timer = time.time() # TODO: set bless timeframe on startup if possible
	def __init__(self, use, inventory):
		super().__init__(use, inventory)
		self.regex_cart=[R.bless, R.unbless]

	def notify(self, regex, M):
		# super().notify(regex, M_obj)
		magentaprint("BlessTimer notify, setting timer.")
		if regex in R.bless:
			self.timer = time.time()
			self.on=True
		elif regex in R.unbless:
			self.on=False

	def maybe_bless(self):
		self.print_timer()
		# if time() > (self.aura_timer + self.aura_refresh):
		# if time.time() > self.aura_timer + self.aura_refresh:
		if self.check_timer() and self.inventory.count(self.milky_potion) + self.inventory.count(self.silver_chalice) > 3 and not self.on:
			if self.inventory.has(self.milky_potion):
				self.use.execute(self.inventory.get_first_reference(self.milky_potion))
			elif self.inventory.has(self.silver_chalice):
				self.use.execute(self.inventory.get_first_reference(self.silver_chalice))
			# I figure the overflow will be silver chalices, not milky potions...
			# Probably need to rewrite later though...
			# Inventory is long if we always carry a milky...
			# But, sometimes, you gotta buy one, unless you want to farm it...
			# I guess maybe don't buy milky if you have silver chalice... that could work
			# Ok I fixed it all... use milky 1st... when buying count both... that way we could get a stack of silver chalices as ideal end state

	milky_potion = "milky potion"; 
	silver_chalice = "silver chalice";
	# When is the right time? Right before a fight - could be better than right before a track (travel time)
	# Best would be before the 1st fight of the track
	# How about when maxed and before a fight, and there's also the timer
	# Seems like a decent heuristic
	# Adam did something like that for berserk

class ProtTimer(Timer):
	# Was going to inherit some variables
	# And was wondering if I would get my own copy
	# Or if they'd be shared
	# Either way is fine
	def __init__(self, use, inventory):
		super().__init__(use, inventory)
		self.regex_cart=[R.prot, R.unprot]

	def notify(self, regex, M):
		# super().notify(regex, M_obj)
		magentaprint("Prot timer notify, setting timer.")
		if regex in R.prot: 
			self.timer = time.time()
			self.on = True
		elif regex in R.unprot:
			self.on = False

	steel_bottle = "steel bottle"; 
	green_potion = "green potion"; 

	def maybe_prot(self):
		# TODO:
		self.print_timer()
		# if time() > (self.aura_timer + self.aura_refresh):
		# if time.time() > self.aura_timer + self.aura_refresh:
		if self.check_timer() and self.inventory.count(self.steel_bottle) + self.inventory.count(self.green_potion) > 3 and not self.on:
			if self.inventory.has(self.green_potion):
				self.use.execute(self.inventory.get_first_reference(self.green_potion))
			elif self.inventory.has(self.steel_bottle):
				self.use.execute(self.inventory.get_first_reference(self.steel_bottle))


