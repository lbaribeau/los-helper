
from command.Command import Command
from comm import RegexStore as R

class Wear(Command):
    command = 'wear'
    success_regexes = [R.you_wear]
    failure_regexes = [R.equipment_broken, R.doesnt_fit]
    error_regexes = [R.wear_what, R.in_combat, R.dont_have]
