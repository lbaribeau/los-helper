
from command.Command import Command
import comm.RegexStore as R

class Prepare(Command):
    command = 'prepare'
    success_regexes = [
        R.prepare,
        R.already_prepared
    ]
    failure_regexes = [
    ]
    error_regexes = [
    ]

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)
        self.prepared = False

    def notify(self, regex, match):
        if regex in R.prepare or regex in R.already_prepared:
            self.prepared = True
            
        super().notify(regex, match)


