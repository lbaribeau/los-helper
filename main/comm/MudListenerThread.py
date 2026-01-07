
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
        # First get the file descriptor (number) of the internal telnet socket object,
        # so we can watch for input.
        socket_number = self.telnetHandler.get_socket()
        # socket_number
        fragment = ""
        # magentaprint("MudListenerThread sys.argv " + str(sys.argv))
        select_timeout = 10.0 if not self.fake_version() else 0.1
        # magentaprint("MudListenerThread select timeout is " + str(select_timeout))
        # So fake just works by timing out the select call
        # Better would be to actually use the socket, but this is working
        # Loop forever, just do stuff when the socket says its ready.
        while not self.stopping:
            try:
                select_triple = select.select([socket_number], [], [], select_timeout)  # A 1 second timeout makes quitting fast
            except ValueError as e:
                # Hmmm, this can get SPAMMED BIGTIME on exit...  (Do not print here)
                if not self.airbag:
                    self.airbag = True
                    magentaprint("MudListenerThread select raised ValueError:" + str(e))
                else:
                    magentaprint("MudListenerThread seems like infinite loop: sleep(2), error is " + str(e))
                    sleep(1)
                continue

            if select_triple == ([], [], []):
                magentaprint("MudListenerThread select timeout reached.")

            # if select_triple != ([], [], []) or socket_number == 1: (old way of doing fake socket - hardcoded socket number as 1)
            # if select_triple != ([], [], []) or self.fake_version:
            if select_triple[0] != [] or self.fake_version():
                # The "triple" is (rlist, wlist, xlist)
                # You can give select a list of sockets
                # It'll fire whenever any of them are ready for reading or writing
                # But we are only interested in reading here
                try:
                    # magentaprint("MudListenerThread calling read_some().")  # Can print a LOT
                    # magentaprint("MudListener select came true!: "+ str(select_triple[0]))
                    print("")
                    magentaprint("MudListenerThread getting something!")
                    # magentaprint("MudListener (fake_version is "+str(self.fake_version())+")")
                    new_bit = self.telnetHandler.read_some() # Make sure you read TelnetHandler
                    # new_bit = self.telnetHandler.read_very_eager()
                    fragment = fragment + new_bit.decode('ascii', errors='ignore')
                    # Should we be ignoring errors
                    # String object has no attribute decode
                    # This occurs when the computer went to sleep
                    # Also telnet handler read_some() error - existing connection forcibly closed by remote
                    # (Understandable it likely timed out)
                # except (OSError, EOFError) as e:
                #     magentaprint("MudListenerThread is exiting because of "+e.__class__.__name__+"(could be dead socket), error says: \""+str(e)+"\"")
                    # break
                except OSError as e:
                    magentaprint("MudListenerThread is exiting because of OSError (could be dead socket); error says: \""+str(e)+"\"")
                    break
                except EOFError as e:
                    magentaprint("MudListenerThread is exiting because server sent EOF; error says: \""+str(e)+"\"") # "Telnet connection closed" (ie. Timed out.)
                    break
                except AttributeError as e:
                    magentaprint("Lag spikes happen like this (new_bit has no attribute decode)")
                    print("\a")
                    raise e

                #magentaprint("MudListener: got a fragment size %d time %.1f last chars %s." % (len(fragment), round(time.time()-self.Character_inst.START_TIME, 1), fragment[len(fragment)-8:]))

                #while(self.MUDBuffer.access_flag == True):
                    #time.sleep(0.05)
                # if self.MUDBuffer.access_flag == True:

                # if not self.MUDBuffer.is_set():
                #     magentaprint("MudListenerThread couldn't access buffer, will try again after next socket fragment.")
                #     continue
                #     # This may cause strings to be matched late (if the buffer was being accessed,)
                #     # We'll see if that happens, even at all.  Worst case that I can imagine is that 
                #     # the bot may pause at one node for several seconds until an ambient event happens,
                #     # but I'm not sure if that's even possible.

                # # self.MUDBuffer.access_flag = True
                # self.MUDBuffer.clear()

                # Ok we probably don't even NEED the fricken flag to protect the buffer
                if fragment != "":
                    magentaprint("MudListener got text!:" + fragment[0:50])
                    self.MUDBuffer.buffer = self.MUDBuffer.buffer + fragment
                    self.MUDBuffer.set()
                    fragment = ""
                    # magentaprint("MudListener done putting text!")
            elif select_triple[1] != [] or self.fake_version():
                magentaprint("MudListenerThread: Note: socket says it's ready for writing!")
            else:
                magentaprint("Select timeout reached, looping: "+str(select_triple))
                self.MUDBuffer.set()
                pass    # just keep waiting.
                        # if stopping was set it will exit the loop
                # Hmmm..... is there any way to tell if the server's ignoring us... "Timed out."
                # other than that text.
        self.MUDBuffer.set()
        magentaprint("MudListenerThread finished run()!")

        # los-helper closes the socket

        # Maybe on_exit "set" the MudBuffer because MRT ends up waiting (just did that with los_helper though)
