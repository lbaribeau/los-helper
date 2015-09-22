
from bots.BotThread import BotThread
from misc_functions import *

class TelnetBotThread(BotThread):
    def __init__(self, character_in=None, command_handler=None, mud_reader_handler=None,
                mud_map=None, telnet_handler=None):
        super().__init__(character, command_handler, mud_reader_handler, mud_map)

    def decide_where_to_go(self): #each logic thread will have to implement this function
        raise NotImplementedError()

    def register_reaction(self, reaction):
        self.mudReaderHandler.register_reaction(reaction)

    def unregister_reaction(self, reaction):
        self.mudReaderHandler.unregister_reaction(reaction)