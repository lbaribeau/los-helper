
import threading
import atexit 
import time
import select
import sys

from misc_functions import magentaprint

class MudListenerThread(threading.Thread):
    ''' This thread watches the the MUD output and appends it
    to the buffer for the MudReaderThread to read it.'''

    def __init__(self, telnetHandler, MUDBuffer):
        super().__init__(name='MudListener')
        self.telnetHandler = telnetHandler
        self.MUDBuffer     = MUDBuffer
        self.stopping      = False
        self.airbag        = False
        atexit.register(self.stop)

    def stop(self):
        self.stopping = True

    def fake_version(self):
        return '-fake' in sys.argv

    def run(self):
        # First get the file descriptor (no) of the internal telnet socket object
        # so we can watch for input.
        socket_number = self.telnetHandler.get_socket()
        fragment=""
        # magentaprint("MudListenerThread sys.argv " + str(sys.argv))
        select_timeout = 2.0 if not self.fake_version() else 0.1
        # magentaprint("MudListenerThread select timeout is " + str(select_timeout))
        # So fake just works by timing out the select call
        # Better would be to actually use the socket, but this is working


        # Loop forever, just do stuff when the socket says its ready.
        while not self.stopping:
            try:
                select_triple = select.select([socket_number], [], [], select_timeout)  # A 1 second timeout makes quitting fast
            except ValueError:
                # TODO:  Hmmm, this can get SPAMMED BIGTIME on exit...  (Do not print here)
                if not self.airbag:
                    self.airbag = True
                    magentaprint("MudListenerThread select ValueError:" + str(ValueError))
                continue

            # if select_triple != ([], [], []) or socket_number == 1:
            if select_triple != ([], [], []) or self.fake_version:
                try:
                    # magentaprint("MudListenerThread calling read_some().")  # Can print a LOT
                    new_bit = self.telnetHandler.read_some()
                    fragment = fragment + new_bit.decode('ascii', errors='ignore')
                    # Should we be ignoring errors
                    # String object has no attribute decode
                    # This occurs when the computer went to sleep
                    # Also telnet handler read_some() error - existing connection forcibly closed by remote
                    # (Understandable it likely timed out)
                except (EOFError, OSError) as e:
                    # I think that the server doesn't send these.
                    magentaprint("MudListenerThread: Exiting (saw EOF) or Socket is dead:")
                    magentaprint(str(e))
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

