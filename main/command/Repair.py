
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
        if self.success:
            self.inventory.get(self._sent_target).usable = True
        if self.failure:
            self.inventory.remove_by_ref(self._sent_target)
        super().notify(regex, match)

        
# [96 H 42 M]: repair Arrum's
# 20:23:38.91   | "repair Arrum's"
# You don't have that.
# [96 H 42 M]: 20:23:39.08   | <command.repair.Repair object at 0x000001C66C604910> clearing timer... wf is Falseregex is You don't ...
# repair Arrum
# 20:23:44.42   | "repair Arrum"
# The smithy cannot repair that.
