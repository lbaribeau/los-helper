
from command.Command import Command
from comm.RegexStore import RegexStore as R

class Repair(Command):
    command = 'repair'
    success_regexes = [R.repair]
    failure_regexes = [R.darnitall]
    error_regexes = [R.not_a_repair_shop, R.repair_what, R.dont_have, R.no_gold]
