
# FEATURES of this program

#   timed attaking and casting (kk and cc commands)
#       These commands will continue until certain MUD output including 
#           mob being killed 
#           spell not known 
#           if you move to a new area
#   timed attacking includes change to hasted attack timing 
#   internal timers to eliminate "Please wait 1 second."
#   Keeps track of weapon so you can flee.
#   Guaranteed-to-work flee function available to user and keeps weapon(s). 
#       command is "fl"
#       will wait the exact right amount of time if you cannot yet flee
#       spams flee command 3 times to ensure you get out :)
#   Bot can be used to do selling and dropping at tip (put items you want to 
#       keep that aren't in KEEP_LIST into some bag that IS in KEEP_LIST)
#   ANSI color

import sys
import getpass
import threading
from threading import Thread
import atexit 
import re
import time
from misc_functions import *
from Character import *
from BotThread import *
from CrawlThread import *
from CommandHandler import *
from MudReaderHandler import *
from MudReaderThread import *
from MudListenerThread import *
from MyBuffer import *
from Inventory import *
from Cartography import *
from BotReactions import *
from TelnetHandler import *


class LosHelper(object):

    def __init__(self):
        ### DEPENDENCY INJECTION ###
        self.telnetHandler = TelnetHandler()
        self.consoleHandler = newConsoleHandler() 
        self.character = Character()
        self.MUDBuffer = MyBuffer()
        self.mudListenerThread = MudListenerThread(self.telnetHandler, self.MUDBuffer)
        self.mudReaderThread = MudReaderThread(self.MUDBuffer, self.character, self.consoleHandler)
        self.mudReaderHandler = MudReaderHandler(self.mudReaderThread, self.character)
        self.commandHandler = CommandHandler(self.character, self.mudReaderHandler, self.telnetHandler)
        self.inventory = Inventory(self.mudReaderHandler, self.commandHandler)
        self.cartography = Cartography(self.mudReaderHandler, self.commandHandler, self.character)
        self.botThread = None
        self.crawlThread = None


    def main(self):
        self.mudListenerThread.start()
        self.mudReaderThread.start()

        # With the MUDReaderThread going, we have the server's text and prompts now showing
        self.write_username_and_pass()
        self.set_up_auto_wield()
        self.check_inventory()
        self.watch_user_input()   
            
        # Quitting cleanly: The MUD_read thread quits if it hits
        # and EOF.  watch_user_input watches for
        # that and quits too.

        while(self.mudReaderThread.is_alive()): 
            self.mudReaderThread.join(3)  
            if (self.mudReaderThread.is_alive()):
                self.mudReaderThread.stop()  # Last resort.

        #Okay, clean exit!
        self.telnetHandler.close();
        print ("It should be safe to ctrl + c now")
        time.sleep(10) 


    def write_username_and_pass(self):

        if(len(sys.argv) >= 3):
            self.telnetHandler.write(sys.argv[1])
            self.telnetHandler.write(sys.argv[2])
        else:
            # With the MUD thread going already, there is no need to prompt here.
            self.telnetHandler.write(input())
            password = getpass.getpass("")
            self.telnetHandler.write(password)

        
    def set_up_auto_wield(self):
        self.mudReaderHandler.register_reaction(WieldReaction(self.character, self.commandHandler))


    def check_inventory(self):
        # This prints the inventory.  I like that.  
        # Inventory needs this to be up to date.
        self.inventory.getInventory()
        
        
    def watch_user_input(self):
        stopping = False;

        while not stopping:

            try:
                user_input = input(); 
            except (EOFError, KeyboardInterrupt) as e:
                magentaprint("Don't try to crash me!  Use 'quit'.")
                user_input = ""

            user_input = user_input.lstrip()

            if(not self.mudReaderThread.is_alive()):
                magentaprint("\nWhat happened to read thread?  Time to turf.\n")
                self.telnetHandler.write(user_input)
                stopping = True

                if(self.botThread != None and self.botThread.is_alive()):
                    self.botThread.stop()

                if(self.crawlThread != None and self.crawlThread.is_alive()):
                    self.crawlThread.stop()

            elif(user_input == "quit"):
                # TODO:  correct if MUD prints "Please wait x more seconds"
                # after quit was sent.
                self.telnetHandler.write(user_input)
                stopping = True

                if(self.botThread != None and self.botThread.is_alive()):
                    self.botThread.stop()

                if(self.crawlThread != None and self.crawlThread.is_alive()):
                    self.crawlThread.stop()

            elif(re.match("bot ?$|bot [0-9]+$", user_input)):
                self.start_bot(user_input)
            elif(re.match("crawl", user_input)):
                self.start_crawl()
            elif(re.match("stop$", user_input)):
                self.stop_bot()
                self.stop_crawl()
            elif(re.match("fle?$|flee$", user_input)):
                self.stop_bot()
                self.commandHandler.process(user_input)  
            else:
                self.commandHandler.process(user_input)


    def start_bot(self, user_input):
        M_obj = re.search("[0-9]+", user_input)

        if (M_obj):
            starting_path = int(M_obj.group(0))
        else:
            starting_path = 0

            if (self.botThread != None and self.botThread.is_alive()):
                magentaprint("It's already going, you'll have to stop it.  Use \"stop\".")
            else:
                self.botThread = BotThread(starting_path, 
                                           self.character, 
                                           self.commandHandler, 
                                           self.mudReaderHandler,
                                           self.inventory)
                self.botThread.start()

    def start_crawl(self):
        if (self.crawlThread != None and self.crawlThread.is_alive()):
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".")
        else:
            self.crawlThread = CrawlThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler)
            self.crawlThread.start()


    def stop_crawl(self):
        if (self.crawlThread != None and self.crawlThread.is_alive()):
            self.crawlThread.stop()
            #self.mudReaderHandler.unregister_reactions()

    def stop_bot(self):
        if (self.botThread != None and self.botThread.is_alive()):
            self.botThread.stop()
            #self.mudReaderHandler.unregister_reactions()

#if __name__ == '__main__':
LosHelper().main()
