
from command.Command import Command
from comm import RegexStore as R

class Drop(Command):
    command = 'drop'
    success_regexes = [R.you_drop]
    failure_regexes = [R.dont_have]
    error_regexes = [R.drop_what]