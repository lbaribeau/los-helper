
#import atexit 
import time
from CombatThread import *
from ThreadStopper import *
from misc_functions import *

class CastThread(CombatThread):
    """ This thread is used to keep time for casts and can send a cast  
    command every few seconds.  It reads Character to determine the attack 
    period """
    # TODO: Watch for failed casts and recast, especially for vigging.
    def __init__(self, Character, MudReaderHandler, telnet, spell, target):   # Constructor
        super(CastThread,self).__init__(Character, MudReaderHandler, telnet, target)
        self.spell = spell
        
        # Make some ThreadStoppers.  These are BotReactions that are given to 
        # MudReaderHandler so that we can be stopped based on Mud text.
        # Logic between me and MudReader...
        # All the regexes that cause the thread to stop are here.
        # There are a couple that also cause a change to character.
        # The ones that require both actions (cast-thread-stop and 
        # write to character.CAST_CLK,) will just be matched twice.
        # BotReactions will be called and used to stop the thread,
        # while character will be written with the usual manual method.
        # As such, the list of regexes causing caststop follows:
        self._reactions.append(ThreadStopper("That spell does not exist\.",self))
        self._reactions.append(ThreadStopper("You don't know that spell\.",self))
        self._reactions.append(ThreadStopper("You cannot meet the casting cost!",self))
        self._reactions.append(ThreadStopper("Spell name is not unique\.",self))    
        self._reactions.append(ThreadStopper("Cast what\?",self))  
        self._reactions.append(ThreadStopper("They are not here\.",self))  
        self._reactions.append(ThreadStopper("Cast at whom\?",self))  

        #atexit.register(self.stop)

    def set_spell(self, new_spell):
        # Used if spell is changed in combat
        self.spell = new_spell

    def run(self):
        # Called by start().  Need to add a parameter argv.  Didn't work.
        # Assumption is that it is constructed and started at the same time.
        self._stopping = False
        self._do_reactions()
        wait_for_cast_ready(self.Character)

        while not self._stopping:
            # TODO: Monitor current spell and current mana and stop if out
            # of mana.
            self.Character.CAST_CLK = time.time()
            #PREV_COMMAND = "cast " + self.spell + " " + self.target + "\n"
            #tn.write(PREV_COMMAND)
            #self.telnet.write("cast " + self.spell + " " + self.target + "\n")
            send_to_telnet(self.telnet, "cast " + self.spell + " " + self.target)
            wait_for_cast_ready(self.Character)

        self._undo_reactions()

    def _do_reactions(self):
        """ Makes and registers threadstoppers for a castthread """
        for reaction in self._reactions:
            self.MudReaderHandler.register_reaction(reaction)
    
    def _undo_reactions(self):
        for reaction in self._reactions:
            self.MudReaderHandler.unregister_reaction(reaction)


