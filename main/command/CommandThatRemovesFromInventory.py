
from command.Command import Command
from comm import RegexStore as R
from misc_functions import magentaprint

class CommandThatRemovesFromInventory(Command):
    def __init__(self, telnetHandler, inventory):
        # Sell needs inventory so we can remove the right item from the inventory
        super().__init__(telnetHandler)
        self.inventory=inventory   # Inventory will use that to stay up to date
    
    def notify(self, regex, match):
        self.result = regex
        magentaprint("CommandThatRemovesFromInventory notify: {0}".format(match.re.pattern))
        if self.success:
            self.inventory.remove_by_ref(self._sent_target)
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

# wield, second, wear, repair, give, hold
