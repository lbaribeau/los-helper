
from command.CommandThatRemovesFromInventory import CommandThatRemovesFromInventory
from comm import RegexStore as R
from command.Command import Command

class Mix(Command):
    command = 'mix'
    success_regexes = [
        R.mix_success
    ]
    failure_regexes = [
        R.mix_fail
    ]
    error_regexes = [
        R.dont_have
    ]

    def __init__(self, telnetHandler, inventory):
        super().__init__(telnetHandler)
        self.inventory = inventory

    def notify(self, r, m):
        if r in R.mix_fail:
            item = self.inventory.get(self._sent_target)
            if item:
                item.usable = False

        super().notify(r, m)

