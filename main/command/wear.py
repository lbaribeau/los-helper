
from command.Command import Command
from comm import RegexStore as R

class Wear(Command):
    command = 'wear'
    success_regexes = [R.you_wear]
    failure_regexes = [R.broken, R.doesnt_fit, R.no_room]
    error_regexes = [R.wear_what, R.in_combat, R.dont_have]
