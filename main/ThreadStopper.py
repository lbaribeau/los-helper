from BotReactions import *

class ThreadStopper(BotReaction):
    """ This class is a BotReaction (observer pattern object that implements 
    'notify' and is registered with the MudReader,) and when 'regex' gets 
    matched, the thread provided in the constructor gets stopped.  This'll 
    work for KillThread and CastThread."""
    def __init__(self, regex, thread):         
        super(ThreadStopper, self).__init__(regex) #*
        self.thread = thread
        
    def notify(self, M_obj):    
        self.thread.stop()
        # M_obj is an argument because we have to conform to BotReaction
        # MudReader expects to be able to give M_obj and BotReactions
        # have to be generic, so even though this BotReaction doesn't 
        # need it, we have to accept it.
        
#* http://stackoverflow.com/questions/1713038/super-fails-with-error-typeerror-argument-1-must-be-type-not-classobj