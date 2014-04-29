
import time
from CombatThread import *
from misc_functions import *

class KillThread(CombatThread):
    """ This thread is used to keep time for attacks and can send an attack 
    command every few seconds.  It reads Character to determine the attack 
    period """
    
    def __init__(self, character, mudReaderHandler, telnetHandler, target):
        super(KillThread, self).__init__(character, mudReaderHandler, 
                                         telnetHandler, target)
        self.regexes.extend(["You don't see that here\.",
                             "Attack what\?"])

    def run(self):
        self.stopping = False
        self.mudReaderHandler.register_reaction(self)
        wait_for_attack_ready(self.character)

        while not self.stopping:
            self.character.ATTACK_CLK = time.time()
            self.telnetHandler.write("k " + self.target)
            wait_for_attack_ready(self.character)

        # This code is really similar to castThread, there's likely a way 
        # to put it in CombatThread 