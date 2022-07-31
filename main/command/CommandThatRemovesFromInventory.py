
from command.Command import Command
from comm import RegexStore as R
from misc_functions import magentaprint

class CommandThatRemovesFromInventory(Command):
    # Don't forget to make sure command handler calls the command object so that inventory gets updated
    def __init__(self, telnetHandler, inventory):
        # Sell needs inventory so we can remove the right item from the inventory
        super().__init__(telnetHandler)
        self.inventory = inventory   # Inventory will use that to stay up to date
        self.inventory_removal = True # Set to false to do a wear of something that didn't make it into inventory (ie. Bought.)
    
    def notify(self, regex, match):
        self.result = regex
        # magentaprint("CommandThatRemovesFromInventory notify: {0}".format(match.re.pattern))
        # magentaprint("CommandThatRemovesFromInventory {0} notify".format(self.__class__))
        if self.success:
            if self._sent_target == 'all':
                # magentaprint("CommandThatRemovesFromInventory notify: {0}".format(match.re.pattern))
                self.inventory.remove_many(match.group(1)) # Could be you wear, you get, any success
            else:
                # got = self.inventory.get(self._sent_target)
                # magentaprint('CommandThatRemovesFromInventory inventory sent {0} got {1}'.format(self._sent_target, got))
                # magentaprint('CommandThatRemovesFromInventory is got None: {0}'.format(got != None))
                # magentaprint('CommandThatRemovesFromInventory condition: {0}'.format(self.inventory_removal and got != None))
                # if self.inventory_removal and got != None:
                if self.inventory_removal and self._executing and self.inventory.get(self._sent_target) != None:
                    # After 'buy' the inventory isn't correct
                    # This could hit the wrong item though!
                    # Need to check inventory after buy, then wear
                    # Maybe shopping bot can add to inventory, so that inventory is correct
                    # magentaprint('*ComandThatRemovesFromInventory REMOVING: {0}'.format(self._sent_target))
                    self.inventory.remove_by_ref(self._sent_target)
                else:
                    magentaprint("Did not remove {0} from inventory (either not executing, or get didn't find.)".format(self._sent_target))
        self.inventory_removal = True
        super().notify(regex, match)

class Sell(CommandThatRemovesFromInventory):
    command = 'sell'
    success_regexes = [
        R.sold
    ]
    failure_regexes = [
        R.wont_buy, 
        R.wont_buy2, 
        R.not_a_pawn_shop,
        R.not_empty
    ]
    error_regexes = [
        R.dont_have, 
        R.sell_what
    ]

class Drop(CommandThatRemovesFromInventory):
    command = 'drop'
    success_regexes = [
        R.you_drop
    ]
    failure_regexes = [
        # Quest item? "Don't drop that?"
        # There is also putting (dropping) into a sack, which you can't do with a quest item
    ]
    error_regexes = [
        R.dont_have, 
        R.drop_what
    ]

# wield, second, wear, repair, give, hold, eat 

class Drink(CommandThatRemovesFromInventory):
    cooldown_after_success = 0.86  # .83 too fast
    # cooldown_after_failure = 0.86
    cooldown_after_failure = 0
    command = 'drin'
    success_regexes = [
        R.you_drink, 
        R.disintegrates
    ]
    failure_regexes = [
    ]
    error_regexes = [
        R.dont_have, 
        R.drop_what,
        R.cant_do
    ]

class Use(CommandThatRemovesFromInventory):
    cooldown_after_success = 0.86  # .83 too fast
    # cooldown_after_failure = 0.86
    cooldown_after_failure = 0
    command = 'use'
    success_regexes = [
        R.potion_drank,
        R.you_drink,
        R.disintegrates
    ]  
    # It's tempting to try to make Inventory smart enough to use healing items...
    # Yes lately I belive Inventory should "have" commands that affect it (No!)
    # But it's nice to have a division of labour (regex subscriptions)
    # Todo: add rods/buffs  (Might be made simpler with a different class, ie. UseRod)
    failure_regexes = []  # TODO: I believe flasks can fail
    # Try a potion in limbo, it evaporates, but that should still count as success I think
    # Often hard to say what is error and what is fail
    # I think fail is when you got the correct target?
    # I think fail is really you got the correct target and it usually/often works, like an RNG fail
    # Use root is just an error even though the target was right (let's say, not a fail)
    # (Can't use is an error then)
    # There is "Your spell fails" for rods
    error_regexes = [
        R.use_what, 
        R.cant_use
    ]
    # def __init__(self, telnetHandler, inventory):
    #     super().__init__(self, telnetHandler, inventory)

    def by_name(self, name):
        self.execute(self.inventory.get_reference(name))  # error checking...

# eat