
from command.Command import Command
import comm.RegexStore as R

class Get(Command):
    command = 'get'
    success_regexes = [R.you_get]
    failure_regexes = [R.cant_carry, R.loot_blocked]
    error_regexes = [R.isnt_here, R.nothing_here]

    # This one's different because it can succeed AND fail
    # Since the fail regex (cant carry) comes last, failure takes precedence

    @property
    def cant_carry(self):
        return self.result in R.cant_carry
