from command.Command import Command
import comm.RegexStore as R
from misc_functions import magentaprint
from db.MobMessage import MobMessage
from db.Mob import Mob

class Ask(Command):
    command = 'ask'
    cooldown_after_success = 0
    cooldown_after_failure = 0
    success_regexes = [
        R.ask_success
    ]
    failure_regexes = [
        R.ask_fail
    ]
    error_regexes = [
        R.i_no_see
    ]

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)

    def execute(self, target=None):
        magentaprint("Ask execute, target is " + target, False)
        super().execute(target)

    def log_result(self, mob_name, request, statement):
        mob = Mob(name=mob_name)
        mob.map()

        # replace all newlines with spaces
        statement = statement.replace('\n', ' ')
        statement = statement.replace('\r', ' ')
        statement = statement.replace('  ', ' ')

        mobMessage = MobMessage(mob=mob, keyword=request, message=statement)
        mobMessage.map()
        # magentaprint("Mapped mob message: " + str(mobMessage), False)


    def notify(self, regex, match):
        self.result = regex # self.success needs result to be set
        # if self.success: # Success isn't set yet
        super().notify(regex, match)
        # if regex in R.bought:

        if self.success:
            params = self._sent_target.split(' ')
            request = ""
            if len(params) > 1:
                request = params[1]
            mob_name = match.group(1).strip().replace("The ", "")
            statement = match.group('statement')
            # request = self._sent_target.split(' ', 1)[1]
            magentaprint("" + mob_name + " responds to " + request, False)
            self.log_result(mob_name, request, statement)
        elif self.failure:
            params = self._sent_target.split(' ')
            request = ""
            if len(params) > 1:
                request = params[1]
            statement = ""
            mob_name = match.group(1).replace("The ", "")
            magentaprint("" + mob_name + " doesn't respond to " + request, False)
            self.log_result(mob_name, request, statement)