
from command.CommandThatRemovesFromInventory import CommandThatRemovesFromInventory
from comm import RegexStore as R

class Hold(CommandThatRemovesFromInventory):
    command = 'hold'
    success_regexes = [
        R.you_hold
    ]
    failure_regexes = [
        R.already_holding
    ]
    error_regexes = [
        R.dont_have
    ]
