
from command.Command import Command
import comm.RegexStore as RegexStore

class Buy(Command):
    command = 'buy'
    cooldown_after_success = 0
    cooldown_after_failure = 0
    success_regexes = [RegexStore.bought]
    failure_regexes = [RegexStore.cant_carry]
    error_regexes = [RegexStore.buy_what, RegexStore.not_for_sale, RegexStore.not_a_shop]

    @property
    def cant_carry(self):
        return self.result in RegexStore.cant_carry
        # I'd like to have this sort of thing automated.  Would require cleaning up Command.py
        # It might be possible to automatically create a boolean for each regex in a command,
        # named the same as the regex.
