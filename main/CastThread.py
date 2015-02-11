
import time
from CombatThread import *
from misc_functions import *

class CastThread(CombatThread):
    """ This thread is used to keep time for casts and can send a cast  
    command every few seconds.  It reads Character to determine the attack 
    period """
    # TODO: Watch for failed casts and recast, especially for vigging.
    def __init__(self, character, mudReaderHandler, telnetHandler, spell, target):
        super(CastThread, self).__init__(character, mudReaderHandler, 
                                         telnetHandler, target)
        self.spell = spell
        self.regexes.extend(["That spell does not exist\.",
                             "You don't know that spell\.",
                             "You cannot meet the casting cost!",
                             "Spell name is not unique\.",
                             "Cast what\?",
                             "They are not here\.",
                             "Cast at whom\?"])  

    def set_spell(self, new_spell):
        self.spell = new_spell

    def run(self):
        self.stopping = False
        self.mudReaderHandler.register_reaction(self)
        wait_for_cast_ready(self.character)

        while not self.stopping:
            # TODO: Monitor current spell and current mana and stop if out
            # of mana.
            self.character.CAST_CLK = time.time()
            self.telnetHandler.write("cast " + self.spell + " " + self.target)
            wait_for_cast_ready(self.character)

        self.end_run()

