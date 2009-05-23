
import threading
from threading import Thread
import atexit 
import time
import re
import select


from MyBuffer import *
from misc_functions import *





class MudListenerThread ( threading.Thread ):
    # This thread watches the the MUD output and appends it 
    # to the buffer for the MudReaderThread to read it.
    
    def __init__(self, tn_in, MUD_buffer_in, Character_inst_in):
        Thread.__init__(self)        
        self.tn = tn_in
        
        self.MUD_buffer = MUD_buffer_in
        self.Character_inst = Character_inst_in
        self.__stopping = False
                                    
        atexit.register(self.stop)
    # end __init__

    def stop(self):
        self.__stopping = True
    # end stop        

    def run (self):        
        # First get the file descriptor (no) of the internal telnet socket object
        # so we can watch for input.        
        tn_sno = self.tn.get_socket()
        
        # Loop forever, just do stuff when the socket says its ready.
        while (not self.__stopping):
            sel_out_triple = select.select([tn_sno], [], [], 2)
            if(sel_out_triple != ([], [], [])):
                # Read some characters.  
                try:
                    fragment = self.tn.read_some() # read_eager misses characters
                except EOFError:
                    print("MudListenerThread: Exiting (saw EOF)")
                    self.stop()
                    break
                #magentaprint("MudListener: got a fragment size %d time %f last chars %s." % (len(fragment), time.time()-self.Character_inst.START_TIME, fragment[len(fragment)-8:]))
                # Tack it on to the buffer.
                # Wait for the access flag to go down
                # Hmmm, I hate to have to wait and not watch the socket,
                # maybe this semaphore could be done better.  However I 
                # also don't want to interrupt if its used.
                while(self.MUD_buffer.access_flag == True):
                    time.sleep(0.05)
                    
                self.MUD_buffer.access_flag = True
                self.MUD_buffer.buffer = self.MUD_buffer.buffer + fragment
                self.MUD_buffer.access_flag = False
            else:
                # Socket timed out.
                pass    # just keep waiting.
                        # if stopping was set it will exit the loop
            # end loop
     # end MudListenerThread.run
# end MudListenerThread
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                