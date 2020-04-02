
from reactions.BotReactions import BotReaction
from misc_functions import *

class KillSlaveReactions(BotReaction):
    def __init__(self, mudReaderHandler, commandHandler, master):
        #[Group] Twerp took 4 combat damage
        self.master_attacks = "{0} (attacks|kicks|punches|thumps|tries to grab) the (.+).".format(master)
        magentaprint(self.master_attacks, False)
        self.regexes = [self.master_attacks]

        self.mudReaderHandler = mudReaderHandler
        self.commandHandler = commandHandler
        
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex == self.master_attacks:
            target_name = str(M_obj.group(2))
            magentaprint("Notified <" + target_name + ">", False)
            self.commandHandler.user_kk(target_name)
