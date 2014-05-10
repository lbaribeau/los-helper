from BotThread import *
from misc_functions import *

class TelnetBotThread(BotThread):
    def __init__(self, character_in=None, commandHandler=None, mudReaderHandler_in=None,
                inventory_in=None, mud_map=None, telnet_handler=None):
    	super(TelnetBotThread, self).__init__(character_in, commandHandler, mudReaderHandler_in, inventory_in, mud_map)

    def decide_where_to_go(self): #each logic thread will have to implement this function
        raise NotImplementedError()

    def register_reaction(self, reaction):
        self.mudReaderHandler.register_reaction(reaction)

    def unregister_reaction(self, reaction):
        self.mudReaderHandler.unregister_reaction(reaction)