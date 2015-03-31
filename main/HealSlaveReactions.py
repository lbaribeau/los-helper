from BotReactions import *
from misc_functions import *

class HealSlaveReactions(BotReaction):
    def __init__(self, mudReaderHandler, commandHandler):
        #[Group] Twerp took 4 combat damage
        self.group_damage = "\[Group\] (.+?) took [\d]* combat damage"
        self.regexes = [self.group_damage]

        self.mudReaderHandler = mudReaderHandler
        self.commandHandler = commandHandler
        self.good_MUD_timeout = 1.5
        
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex == self.group_damage:
            target_name = str(M_obj.group(1))
            magentaprint("Notified <" + target_name + ">", False)
            self.commandHandler.process('c vig ' + target_name)
