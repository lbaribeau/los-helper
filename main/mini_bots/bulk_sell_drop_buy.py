
# Inventory.py has gotten too complicated

# inventory will have sell, drop, buy commands - could pass in inventory
# Let's do it like... with different objects
# We can keep objects small that way
# And there's an obvious division between these things

class BulkSell(MiniBot):
	def __init__(self, sell_command):
		self.sell_command=sell_command

# class BulkGive_using_command(MiniBot):
# 	# Note: call inventory functions
# 	# So inventory can maintain itself
# 	# It can't do so if we use the command objects
# 	# Well, we do have singleton command objects...
# 	# Maybe we need a link from commands to inventory?
# 	# "Need" is too strong a word - use inventory
# 	def __init__(self, give_command):
# 		self.give_command=give_command
# 	def give_dont_wait(self, item_string):
# 		self.give_command.send(item_string)
# 	def give_and_wait(self, item_string):
# 		return self.give_command.execute_and_wait(item_string)
# 	def give(self, item_string):
# 		return self.give_and_wait(item_string)
# 	def bulk_give(self, item_string, quantity):
#     	for i in range(0, quantity):
#     		self.give_and_wait(item_string)

# Ehhh feels like the command should know about the inventory???
# They will both get notified
# Inventory could just look at the command
# That assumes that the polling loop thread will be slow enough for 
# all the notifications to get done.

# If the command doesn't help inventory, inventory will have to write wrappers for all this.
# I think that's correct though, right
# Does the command know it has to keep inventory maintained or does the inventory???
# And users of these objects, do they know they can't use the command???
# What direction do things go in??????

class BulkGive(MiniBot):
	def __init__(self, inventory):
		self.i=inventory
	def give_dont_wait(self, item_string):
		self.i.give.send(item_string)
	def give_and_wait(self, item_string):
		return self.i.give.execute_and_wait(item_string)
	def give(self, item_string):
		return self.i.give_and_wait(item_string)
	def bulk_give(self, item_string, quantity):
    	for i in range(0, quantity):
    		self.i.give_and_wait(item_string)

class BulkDrop(MiniBot):
	def __init__(self, drop_command):
		self.drop_command=drop_command
	def drop_dont_wait(self, item_string):
		self.drop_command.send(item_string)
	def drop_and_wait(self, item_string):
		return self.drop_command.execute_and_wait(item_string)
	def drop(self, item_string):
		return self.drop_and_wait(item_string)
	def bulk_drop(self, item_string, quantity):
    	for i in range(0, quantity):
    		self.drop_and_wait(item_string)

class BulkBuy(MiniBot):
	def __init__(self, buy_command):
		self.buy_command=buy_command

    def buy_dont_wait(self, item_string):
        # self.telnetHandler.write("buy " + item_string)
        # self.wait_for_flag()
        # self.add(item_string)
        self.buy_command.execute(item_string)

	def buy_and_wait(self, item_string):
        return self.buy_command.execute_and_wait(item_string)
    def buy(self, item_string):
    	return self.buy_and_wait(item_string)

    def bulk_buy(self, item_string, quantity):
        self.is_bulk_vendoring = True
    	for i in range(0, quantity):
    		self.buy_and_wait(item_string)
        self.is_bulk_vendoring = False

    # def sell_fast(self):

