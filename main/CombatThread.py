
import threading
from threading import Thread
import atexit 
from ThreadStopper import *

class CombatThread(threading.Thread):
    """ Parent to KillThread and CastThread.
    Implements common functions (init, stop, keep_going, set_target, 
    _do_reactions, _undo_reactions)
    """
    def abstract():
        import inspect
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        raise NotImplementedError(caller + ' must be implemented in subclass')
        
    def __init__(self, Character, MudReaderHandler, telnet, target):   # Constructor
        Thread.__init__(self)
        self._stopping = False
        self.Character = Character
        self.MudReaderHandler = MudReaderHandler
        self.telnet = telnet
        self.target = target      # the string argument indicating the target.
        self._reactions = []
        _s_numbered = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?"        
        self._reactions.append(ThreadStopper("Your attack overwhelms (the" + _s_numbered + ")? (.+?) and (s?he|it) collapses!",self))  
        self._reactions.append(ThreadStopper("(The" + _s_numbered + " )?(.+?) flees to the (.+?)\.",self)) 
        atexit.register(self.stop)
        
    def _do_reactions(self):
        """ Makes and registers threadstoppers for a killthread """
        for reaction in self._reactions:
            self.MudReaderHandler.register_reaction(reaction)
    
    def _undo_reactions(self):
        for reaction in self._reactions:
            self.MudReaderHandler.unregister_reaction(reaction)
            #pass # Getting "You don't see that here." and needing to manually kill the threads ('sk' and 'sc')
            # Threads aren't getting stopped.  Well... it seems to mostly work, must have been an oddity?

    def stop(self):
        #magentaprint("CombatThread: stopping self.")
        self._stopping = True
        self._undo_reactions() #!!! TODO: current bug (lots of prints, and lots of extra thread object accumulating)

        # Commented: Causes a bug... MudReader is going through its list of reactions, 
        # and calls notify, which calls stop, which calls this _undo_reactions, and 
        # so we are changing the list WHILE MudReader is still going through it.
        # Ideal would be a way to never change the list... then each kill thread 
        # would have to be given to the ThreadStoppers each time... the ThreadStoppers
        # shouldn't be remade in __init__ but owned by CommandHandler.  If I wanted 
        # I could try just moving the removal to the point as the thread dies (after 
        # the while(not self._stopping) loop... the chances of that causing a conflict 
        # are slim because it would have to happen while MudReader is in the loop.
        # I could also protect the list, use some kind of flag so it's not edited 
        # while the loop is going.  That seems like a good idea except that I wanted 
        # to get away from doing flags.  I think I will not make the flag, I'll just 
        # write a TODO for it.  For now, move _under_reactions to the end of run().

        # Maybe the better answer is to use a smarter iterator on MudReaderThread's end.
        # Recheck the list contents each iteration.

        # ... fixed the loop problem, now just getting 'You don't see that here and 
        # They are not here.  So.  I believe that one thread gets stopped (perhaps kill 
        # and then the cast thread gets removed,) but _stopping doesn't get set on both.  
        # So... Notify must be sure to do that... Does notify get called on both threads?
        
        
    def keep_going(self):
        if(self._stopping == True):
            self._stopping = False
            self._do_reactions()

    def get_stopping(self):
        return self._stopping

    def set_target(self, new_target):
        # Used if target is changed in combat
        self.target = new_target
        
    def run(self):
        abstract()

