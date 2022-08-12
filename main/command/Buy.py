
from command.Command import Command
import comm.RegexStore as R
from misc_functions import magentaprint

class Buy(Command):
    command = 'buy'
    cooldown_after_success = 0
    cooldown_after_failure = 0
    success_regexes = [
        R.bought
    ]
    failure_regexes = [
        R.cant_carry
    ]
    error_regexes = [
        R.buy_what, 
        R.not_for_sale, 
        R.not_a_shop
    ]
    @property
    def cant_carry(self):
        return self.result in RegexStore.cant_carry
        # I'd like to have this sort of thing automated.  Would require cleaning up Command.py
        # It might be possible to automatically create a boolean for each regex in a command,
        # named the same as the regex.

    def __init__(self, telnetHandler, inventory):
        super().__init__(telnetHandler)
        self.inventory = inventory

    def notify(self, regex, match):
        self.result = regex # self.success needs result to be set
        magentaprint("Buy notify success: {0}".format(self.success)) 
        # if self.success: # Success isn't set yet
        super().notify(regex, match)
        # if regex in R.bought:
        if self.success:
            # self.inventory.execute() 
            # Will get_inventory slow down notify... yes... only on buy though
            # That is actually to correct inventory when the PLAYER buys
            # When the bot buys (shopping bot,) it adds to inventory
            # Not sure that's how I'd do it if I were doing it again, but it's done
            # What I would do is write buy.execute_and_wait, and wait for inventory to come back
            # Well... this would CLOBBER inventory, especially item.usable
            # So it's not acceptable... we can assume that someone will wear what they buy...
            # But what if the wear command hits something else
            # Ok let's turn off the wear command
            # self.inventory.add(self._sent_target.split(' ')[0]) # Ahhhh this is SUPER cheeky
            # So wear/wield will try to remove this item in inventory...
            # And succeed if it used the same 'word'
            # (We just added single word "maul" to the inventory, or "chain")
            # Ehh it didn't work, remove needs it to be 'maul hammer'
            # So why not clobber the inventory, it's supposed to work anyway
            
            # Human buys: inventory.execute updates inventory
            # Bot buys: inventory.execute finds that the bot has already updated the inventory (usable isn't clobbered)
            # Dang as a human I don't like that that I can't use "!" to buy multiple things!
            # So... maybe just print...
            magentaprint("---Please check inventory now to update the list!---")
            # So... this clobbers the inventory
            # I suppose we can live with that... 

    # That's too much waiting for fake telnet (waiting for a reply in a notify())
    # Buy could use the db...

