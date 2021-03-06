
import threading
from threading import Thread
import atexit 
import time
import re
import select
import sys

from misc_functions import *

class MudListenerThread(threading.Thread):
    ''' This thread watches the the MUD output and appends it
    to the buffer for the MudReaderThread to read it.'''

    def __init__(self, telnetHandler, MUDBuffer):
        Thread.__init__(self)
        self.telnetHandler = telnetHandler
        self.MUDBuffer = MUDBuffer
        atexit.register(self.stop)
        self.stopping = False
        self.airbag = False

    def stop(self):
        self.stopping = True

    def run (self):
        # First get the file descriptor (no) of the internal telnet socket object
        # so we can watch for input.
        socket_number = self.telnetHandler.get_socket()
        fragment=""
        # magentaprint("MudListenerThread sys.argv " + str(sys.argv))
        select_timeout = 2.0 if '-fake' not in sys.argv else 0.1
        # magentaprint("MudListenerThread select timeout is " + str(select_timeout))

        # Loop forever, just do stuff when the socket says its ready.
        while not self.stopping:
            try:
                sel_out_triple = select.select([socket_number], [], [], select_timeout)  # A 1 second timeout makes quitting fast
            except ValueError:
                # TODO:  Hmmm, this can get SPAMMED BIGTIME on exit...  (Do not print here)
                if not self.airbag:
                    self.airbag = True
                    magentaprint("MudListenerThread:" + str(ValueError))
                continue

            if (sel_out_triple != ([], [], []) or socket_number == 1):
                try:
                    # magentaprint("MudListenerThread calling read_some().")  # Can print a LOT
                    fragment = fragment + self.telnetHandler.read_some().decode('ascii', errors='ignore')
                except (EOFError, OSError) as e:
                    # I think that the server doesn't send these.
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
                # Hmmm..... is there any way to tell if the server's ignoring us... "Timed out."
                # other than that text.

        # los-helper closes the socket

