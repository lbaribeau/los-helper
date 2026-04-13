
from comm import RegexStore as R
from command import Inventory
from command.Command import Command
import itertools
from misc_functions import magentaprint

class Remove(Command):
	command = 'rm'

	success_regexes = [
		R.you_remove
	]

	failure_regexes = [
		# Let's define 'failure' as something you might reasonably try and find out info about
		# - try remove all, ok, not wearing anything, is not an error
		# R.cant_in_combat, # I think you can remove things in combat
		R.nothing_to_remove # You aren't wearing anything that can be removed
	]

	error_regexes = [
		# Error is like, there's no reason you should have tried that
		R.not_worn,    # bad target ("You aren't using that") (Also applies to weapons like long sword)
		R.remove_what  # empty command
	]

	def __init__(self, telnetHandler, inventory, eq):
		super().__init__(telnetHandler)
		self.inventory=inventory
		self.eq=eq # Equipment command stores worn items like armour, weapon, held, in a dict

		# regex cart doesn't seem needed

	def notify(self, regex, match):
		# Ok... self.success does not work ackckckckck because it needs super.notify() but that also implements the event wait...
		if regex in itertools.chain.from_iterable(self.success_regexes):
			self.inventory.add(match.group(1)) 

			# Should we check 'eq'??? I guess we could. Remove from eq
			# match group 1 is R.items, it's got all the comma-separate items as one group
			# .add can handle that list
			# removed_gear = Inventory.parse_item_list(match.group(1)) # Can handle "hammer" and "a hammer"
				# This is a module function call
			# eq=self.eq
			# for i in items:
				# if i in eq.dict.items():
				# eq.dict.pop(i) # Why bother checking, they should be in there
				# del eq.dict[
				# eq.dict = {slot: item for slot, item in eq.dict.items() if item != i}
			# self.eq.dict = {slot: item_name for slot, item_name in eq.dict.items() if item_name not in items} # Doesn't handle neck1, neck2, fingers...

			# Quick and dirty way...
			# self.eq.clear()
			# self.telnetHandler.write('eq')
			# self.eq.wait_for_flag() # Reinitialized 'eq'

			# Ok suppose "You remove a plate mail collar, a plate mail collar, a copper ring, a steel ring"
			# No idea which gotta use command that was sent
			# Also the DICT is KEYED by SLOT
			# Wrong data structure...
			# It's fine we can loop through key/value pairs...
			removed_gear = Inventory.parse_item_list(match.group(1))
			# key_value_pair_to_remove = []
			magentaprint(f"Remove command needs to remove: {removed_gear}...")
			magentaprint(f"Going to loop over {self.eq.dict.copy().items()}")
			for slot, eq_armour_name in self.eq.dict.copy().items():
				# For some reason... these are the terms
				# keys, values are obvious
				# "items" in Python refers to key/value pairs...
				if eq_armour_name in removed_gear:
					# del self.eq.dict[slot] # I think we keep the keys in eq.dict so we can check eq['holding'] try just making it None
					self.eq.dict[slot]=None
					removed_gear.remove(eq_armour_name) # This'll help the 2nd plate mail collar to also get removed
					# However there's a problem... did we remove them in the right order??
					# Do we care?
					# Not yet, probably not ever, because, they are both perfectly good plate mail collars, pretty equivalent, 
					# maybe not for condition... 
					# also, maybe neck 1, neck 2, could get a collision? Well we are operating on the return text
					# key_value_pair_to_remove.append((slot,eq_armour_name))

			# Avoiding RuntimeError: dictionary changed size during iteration
			# for slot, eq_armour_name in key_value_pair_to_remove:
			# 	del self.eq.dict[x
			# magentaprint(f"Remove: Equipment dict eq.dict is {self.eq.dict}")
			self.eq.print()
			# Okay we are gonna be loose on this one, wear doesn't add to the dict
			# Hold does though

		super().notify(regex, match) # implements execute, wait for server text
