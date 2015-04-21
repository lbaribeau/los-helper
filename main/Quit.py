
from Command import Command
from misc_functions import magentaprint
import RegexStore

class Quit(Command):
    command = "quit"
    success_regexes = [RegexStore.goodbye]
    failure_regexes = []
    regexes = []

    def __init__(self, mudReaderHandler, telnetHandler):
        super().__init__(telnetHandler)
        mudReaderHandler.register_reaction(self)
        self.execute()
        self.wait_for_flag()
        mudReaderHandler.unregister_reaction(self)

