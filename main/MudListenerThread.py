
import threading
from threading import Thread
import atexit 
import time
import re
import select

from MyBuffer import *
from misc_functions import *


class MudListenerThread(threading.Thread):
    ''' This thread watches the the MUD output and appends it 
    to the buffer for the MudReaderThread to read it.'''
    
    __stopping = False

    def __init__(self, telnetHandler, MUDBuffer):
        Thread.__init__(self)        
        self.telnetHandler = telnetHandler
        self.MUDBuffer = MUDBuffer
        atexit.register(self.stop)

    def stop(self):
        self.__stopping = True

    def run (self):        
        # First get the file descriptor (no) of the internal telnet socket object
        # so we can watch for input.        
        socket_number = self.telnetHandler.get_socket()
        fragment=""
        
        # Loop forever, just do stuff when the socket says its ready.
        while not self.__stopping:
            try:
                sel_out_triple = select.select([socket_number], [], [], 2)
            except ValueError:
                #Eat the error
                # TODO:  Hmmm, this gets SPAMMED BIGTIME on exit...  (Do not print here)
                continue

            if sel_out_triple != ([], [], []):
                try:
                    fragment = fragment + self.telnetHandler.read_some().decode('ascii', errors='ignore')
                except (EOFError, OSError) as e:
                    # These can be thrown by read_some()
                    magentaprint("MudListenerThread: Exiting (saw EOF) or Socket is dead")
                    self.stop()
                    break

                #magentaprint("MudListener: got a fragment size %d time %.1f last chars %s." % (len(fragment), round(time.time()-self.Character_inst.START_TIME, 1), fragment[len(fragment)-8:]))

                #while(self.MUDBuffer.access_flag == True):
                    #time.sleep(0.05)
                if self.MUDBuffer.access_flag == True:
                    magentaprint("MudListenerThread couldn't access buffer, will try again after next socket fragment.")
                    continue 
                    # This may cause strings to be matched late (if the buffer was being accessed,)
                    # We'll see if that happens, even at all.  Worst case that I can imagine is that 
                    # the bot may pause at one node for several seconds until an ambient event happens,
                    # but I'm not sure if that's even possible.
                    
                self.MUDBuffer.access_flag = True
                self.MUDBuffer.buffer = self.MUDBuffer.buffer + fragment
                self.MUDBuffer.access_flag = False
                fragment = ""
            else:
                # Socket timed out.
                pass    # just keep waiting.
                        # if stopping was set it will exit the loop
                