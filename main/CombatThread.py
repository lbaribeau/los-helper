
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
        
    def __init__(self, character, mudReaderHandler, telnetHandler, target):   
        Thread.__init__(self)
        self._stopping = False
        self.character = character
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.target = target      
        self._reactions = []
        _s_numbered = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?"        
        self._reactions.append(ThreadStopper("Your attack overwhelms (the" + _s_numbered + ")? (.+?) and (s?he|it) collapses!",self))  
        self._reactions.append(ThreadStopper("(The" + _s_numbered + " )?(.+?) flees to the (.+?)\.",self)) 
        atexit.register(self.stop)
        
    def _do_reactions(self):
        """ Makes and registers threadstoppers for a killthread """
        for reaction in self._reactions:
            self.mudReaderHandler.register_reaction(reaction)
    
    def _undo_reactions(self):
        for reaction in self._reactions:
            self.mudReaderHandler.unregister_reaction(reaction)

    def stop(self):
        self._stopping = True
        self._undo_reactions()         
        
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

