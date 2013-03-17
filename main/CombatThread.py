
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
        atexit.register(self.stop)
        
    def _do_reactions(self):
        """ Makes and registers threadstoppers for a killthread """
        for reaction in self._reactions:
            self.MudReaderHandler.register_reaction(reaction)
    
    def _undo_reactions(self):
        for reaction in self._reactions:
            self.MudReaderHandler.unregister_reaction(reaction)
            
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

