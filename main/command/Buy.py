
from command.Command import Command
import comm.RegexStore as RegexStore

class Buy(Command):
    command = 'buy'
    cooldown_after_success = 0
    cooldown_after_failure = 0
    success_regexes = [RegexStore.bought]
    failure_regexes = [RegexStore.not_for_sale]
    error_regexes = [RegexStore.buy_what]
