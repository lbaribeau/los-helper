
from command.CommandThatRemovesFromInventory import CommandThatRemovesFromInventory
from comm import RegexStore as R
from command.Command import Command

class Remove(Command):
    command = 'remove'
    success_regexes = [
        R.you_remove
    ]
    failure_regexes = [
        R.nothing_to_remove
    ]
    error_regexes = [
        R.dont_have
    ]

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)

