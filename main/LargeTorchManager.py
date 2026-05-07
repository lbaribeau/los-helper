from misc_functions import magentaprint

class LargeTorchManager:
	""" This will become kind of a "Hold Manager" where it'll deal with any sorts of held items.
	The approach will be that we'll hold a torch if it gets dark and keep it held until we get to the tip.
	Then we'll remove it and drop it in the tip there.
	Large torches are much cheaper than glowing potions but, being held items, have to be managed."""
	def __init__(self, inventory, look_command, hold_command, remove_command, drop_command, buy_command, character):
		# self.holding=False
		self.inventory       = inventory
		self.look            = look_command
		self.hold            = hold_command
		self.remove          = remove_command
		self.eq              = self.hold.eq
		self.remove          = remove_command
		self.drop            = drop_command
		self.buy             = buy_command
		self.character       = character
		self.previous_item   = ''
		self.setup_done=False

	def setup(self):
		# Look at condition of torches in inventory
		for t in self.inventory.get_reference_for_each_one('large torch'):
			r=self.look.execute_and_wait(t)
			if self.look.broken:
				self.inventory.set_unusable(t)
		self.setup_done=True

	def can_handle_it(self):
		return self.setup_done and self.inventory.has_unbroken('large torch')

	def holding_torch(self):
		return self.hold.eq.dict['holding'] == 'large torch'
		# ideally run 'eq' but we can keep track or just recover if already holding

	def holding_something_else(self):
		return self.hold.eq.dict['holding'] and self.hold.eq.dict['holding'] != 'large torch'

	def get_torch_ref(self):
		return self.inventory.get_unbroken('large torch')

	def use_torch(self):
		if not self.inventory.has_unbroken('large torch'):
			magentaprint("We don't have a torch??!")
			return False

		self.previous_item = self.eq.dict['holding']
		if self.previous_item:
			# self.remove.execute(self.eq.get_ref_of_item_by_name(self.previous_item)) # Assume no name collisions??
			self.remove.execute_and_wait(self.eq.get_ref_of_item_by_slot('holding'))  # Yes, adds it to inventory
			# Note that that is an 'eq ref' so not valid for the inventory bag
			if self.previous_item != 'large torch':
				self.inventory.add_to_keep_list_by_name(self.previous_item)
			else:
				self.previous_item = ''

		hold = self.hold
		hold.execute_and_wait(self.inventory.get_unbroken('large torch')) # Already checked that we have one
		return hold.success # I guess we have to assume based on the condition of the torch that this worked

	def remove_torch(self):
		# Well I guess we implement a remove command...
		# We can have it edit inventory instead of having inventory do it itself?
		# Sure... Command is a good design pattern, right...
		self.setup_done = False # We won't know the condition of this torch
		if self.eq.dict['holding']=='large torch':
			self.remove.execute_and_wait(self.eq.get_ref_of_item_by_slot('holding'))  # Yes, adds it to inventory
		else:
			magentaprint("Ehrm someone called LargeTorchManager.remove_torch() when we weren't holding a torch")

	def reequip_held_item(self):
		if self.previous_item:
			self.hold.execute_and_wait(self.inventory.get_last_reference(self.previous_item)) # Just hoping that it's still the last in the stack
		self.previous_item = ''

	def drop_last_torch(self):
		self.drop.execute_and_wait(self.inventory.get_last_reference('large torch'))

	def at_tip_drop_held_torch(self):
		if not self.holding_torch():
			return

		self.remove_torch()
		self.reequip_held_item()
		self.drop_last_torch()

	def decrement_ref(self, ref_string):
		# Eh hopefully ref is "decrementable"
		ref_split = ref_string.split(' ')
		if len(ref_split) > 1:
			new_n = int(ref_split[1])-1 # Ehrm [1] is out of range if "l large 1"
			if new_n > 1:
				return ref_split[0]+' '+str(new_n)
			else:
				return ref_split[0]
		else:
			return -1

	# def at_tip_drop_bad_torches(self):
	# 	# Ok what if we logged out holding a torch and it went bad
	# 	# Or what if there is somehow a bad one

	# 	# if self.inventory.count_unusable('large torch') <= 0:
	# 	# 	return

	# 	ref = self.inventory.get_last_reference('large torch')
	# 	num_torches_remaining = self.inventory.count('large torch')
	# 	while num_torches_remaining:
	# 		item=self.inventory.get(ref)
	# 		if not hasattr(item, 'usable') or item.usable:
	# 			num_torches_remaining-=1
	# 			# if num_torches_remaining:
	# 			# 	# last_ref_split = ref.split(' ')
	# 			# 	# ref = last_ref.split[0]+' '+str(int(last_ref_split[1])-1)
	# 			# 	ref = self.decrement_ref(ref)
	# 			ref = self.decrement_ref(ref)
	# 		else:
	# 			if self.drop.execute_and_wait(ref):
	# 				magentaprint("Good, dropped a torch")
	# 			else:
	# 				magentaprint("What the $#&* happened, LargeTorchManager couldn't drop a torch")
	# 			ref = self.decrement_ref(ref)
	# 			num_torches_remaining-=1
	# Can invert that clause...

	def at_tip_drop_bad_torches(self):
		# Ok what if we logged out holding a torch and it went bad
		# Or what if there is somehow a bad one

		# if self.inventory.count_unusable('large torch') <= 0:
		# 	return

		ref = self.inventory.get_last_reference('large torch')
		num_torches_remaining = self.inventory.count('large torch')
		while num_torches_remaining:
			item = self.inventory.get(ref)
			if hasattr(item, 'usable') and not item.usable:
				if self.drop.execute_and_wait(ref):
					magentaprint("Good, dropped a torch")
				else:
					magentaprint("What the h$#&! happened, LargeTorchManager couldn't drop a torch")
			ref = self.decrement_ref(ref) # ie. large 2, large 1
				# Ok we do call decrement ref even though we're on the last one... 
			num_torches_remaining-=1

	def at_shop_buy_torch_if_needed(self):
		# Ok this will be O(n^3) or something like that and easilty fixed but it's fine
		# while self.inventory.count_usable('large torch') < 2 if self.character.level > 3 else 1:
		while self.inventory.count_usable('large torch') < (2 if self.character.level > 3 else 1):
			if self.buy.execute_and_wait('torch'):
				self.inventory.add('large torch') # Hopefully not too janky? I think this expects a string like from the MUD
				self.character.GOLD -= 12
			else:
				if self.character.GOLD < 12:
					magentaprint("LargeTorchManager couldn't buy a torch??!?") # Hmmm could be 'can't carry'
				else:
					raise Exception("LargeTorchManager couldn't buy a torch??!?")

	def check_torches(self):
		# Ok I realized when I remove a torch, it invalidates "setup_done"
		# So how do we make sure we are up to speed on the inventory
		# We could catch it right when we remove the torch
		# Or we could just say it's fine to check everything at the chapel?
		# How about whenever the bot removes a torch it also calls .setup_done = False
		# That's fair
		# We plan to drop it right away anyway
		pass
		# call setup before this to "look" at all the torches (not checking that)


		# if torch:
		# 	return torch
		# if self.inventory.has_unbroken('large torch')
		# 	last_torch = self.inventory.get
		# 	return self.inventory.get_last_
		# torch = self.inventory.get_unbroken('large torch')
		# if self.inventory.item_from_reference(torch).unusable: