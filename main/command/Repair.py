
from command.Command import Command
from comm import RegexStore as R

# class Repair(CommandThatRemovesFromInventory):
class Repair(Command):
    command = 'repair'
    success_regexes = [
        R.repair,
        R.not_broken # Weird if this happens but may as well act as if the thing got repaired
    ]
    failure_regexes = [
        R.darnitall
    ]
    error_regexes = [
        R.not_a_repair_shop, 
        R.repair_what, 
        R.dont_have, 
        R.no_gold,
        R.cant_repair
    ]

    def __init__(self, telnetHandler, inventory):
        self.inventory = inventory   
        super().__init__(telnetHandler)

    def notify(self, regex, match):
        self.result = regex
        if self.success and self._sent_target is not None:
                self.inventory.get(self._sent_target).usable = True
        if self.failure:
            self.inventory.remove_by_ref(self._sent_target)
        super().notify(regex, match)
