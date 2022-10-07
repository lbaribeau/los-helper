
from command.CommandThatRemovesFromInventory import CommandThatRemovesFromInventory
from comm import RegexStore as R

class Mix(CommandThatRemovesFromInventory):
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
        super().__init__(telnetHandler, inventory)
        # mixing can take quite a while
        self.good_MUD_timeout = 15.0

    def notify(self, r, m):
        if r in R.mix_fail:
            item = self.inventory.get(self._sent_target)
            if item:
                item.usable = False

        super().notify(r, m)

