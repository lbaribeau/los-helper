
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
    
    def __init__(self, tn_in, MUD_buffer_in):
        Thread.__init__(self)        
        self.tn = tn_in
        
        self.MUD_buffer = MUD_buffer_in
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
        fragment=""
        
        # Loop forever, just do stuff when the socket says its ready.
        while (not self.__stopping):
            sel_out_triple = select.select([tn_sno], [], [], 2)
            if(sel_out_triple != ([], [], [])):
                # Read some characters.  
                try:
                    fragment = fragment + self.tn.read_some() # read_eager misses characters
                except EOFError:
                    print("MudListenerThread: Exiting (saw EOF)")
                    self.stop()
                    break
                #magentaprint("MudListener: got a fragment size %d time %f last chars %s." % (len(fragment), time.time()-self.Character_inst.START_TIME, fragment[len(fragment)-8:]))

                #while(self.MUD_buffer.access_flag == True):
                    #time.sleep(0.05)
                if(self.MUD_buffer.access_flag == True):
                    magentaprint("MudListenerThread couldn't access buffer, will try again after next socket fragment.")
                    continue 
                    # This may cause strings to be matched late (if the buffer was being accessed,)
                    # We'll see if that happens, even at all.  Worst case that I can imagine is that 
                    # the bot may pause at one node for several seconds until an ambient event happens,
                    # but I'm not sure if that's even possible.
                    
                self.MUD_buffer.access_flag = True
                self.MUD_buffer.buffer = self.MUD_buffer.buffer + fragment
                self.MUD_buffer.access_flag = False
                fragment = ""
            else:
                # Socket timed out.
                pass    # just keep waiting.
                        # if stopping was set it will exit the loop
            # end loop
    # end MudListenerThread.run
# end MudListenerThread
                