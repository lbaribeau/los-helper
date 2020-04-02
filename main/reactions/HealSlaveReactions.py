
from reactions.BotReactions import BotReaction
from misc_functions import *

class HealSlaveReactions(BotReaction):
    def __init__(self, mudReaderHandler, commandHandler, master):
        #[Group] Twerp took 4 combat damage
        self.group_damage = "\[Group\] {0} took ([\d]*) combat damage".format(master)
        self.regexes = [self.group_damage]
        self.master = master
        self.dmg = 0

        self.mudReaderHandler = mudReaderHandler
        self.commandHandler = commandHandler
        
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex == self.group_damage:
            self.dmg += int(M_obj.group(1))

            magentaprint("{0} {1}".format(self.dmg, self.master), False)
            if (self.dmg >= 10):
                self.dmg = 0
                magentaprint("Notified <" + self.master + ">", False)
                self.commandHandler.process('c vig ' + self.master)
