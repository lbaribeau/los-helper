
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

print("Importing python modules...")

import sys
import getpass
import threading
from threading import Thread
import atexit 
import re
import time

print("Importing los-helper modules...")

from misc_functions import magentaprint
from Character import Character
from CharacterClass import CharacterClass
from GrindThread import GrindThread
from CrawlThread import CrawlThread
from GotoThread import GotoThread
from CommandHandler import CommandHandler
from MudReaderHandler import MudReaderHandler 
from MudReaderThread import MudReaderThread 
from MudListenerThread import MudListenerThread 
from MyBuffer import MyBuffer 
from Inventory import Inventory
from SmartCombat import SmartCombat
from Info import Info 
from Whois import Whois
from Cartography import Cartography 
from BotReactions import *
from TelnetHandler import TelnetHandler 
from Database import *
from MudMap import *
from Quit import Quit

class LosHelper(object):

    def __init__(self):
        self.botThread = None
        magentaprint("Connecting to database....", False)
        self.database_file = "maplos.db"
        self.database = SqliteDatabase(self.database_file, threadlocals=True, check_same_thread=False)
        db.initialize(self.database)

        magentaprint("Connecting to MUD and initializing....", False)
        self.character = Character()
        self.telnetHandler = TelnetHandler()
        self.consoleHandler = newConsoleHandler() 
        self.MUDBuffer = MyBuffer()
        self.mudListenerThread = MudListenerThread(self.telnetHandler, self.MUDBuffer)
        self.mudReaderThread = MudReaderThread(self.MUDBuffer, self.character, self.consoleHandler)
        self.mudReaderHandler = MudReaderHandler(self.mudReaderThread, self.character)
        self.character.inventory = Inventory(self.mudReaderHandler, self.telnetHandler)

        magentaprint("Generating the mapfile....", False)
        self.mud_map = MudMap() 
        # self.mud_map = None

        self.mudListenerThread.start()
        self.mudReaderThread.start()
        # With the MUDReaderThread going, we have the server's text and prompts now showing

        self.write_username_and_pass()
        self.initialize_reactions()
        self.check_inventory()
        self.check_class_and_level()
        self.check_info()

        self.commandHandler = CommandHandler(self.character, self.mudReaderHandler, self.telnetHandler, self.database_file, self.mud_map)
        # Maybe commandHandler can just 'have' SmartCombat (CombatLogic) which 'has' kill and cast
        # Same with the botThread... CombatLogic should own all the little objects so we don't have to pass them individually.
        self.cartography = Cartography(self.mudReaderHandler, self.commandHandler, self.character, self.database_file, self.mud_map)

    def main(self):

        self.watch_user_input()
        self.mudReaderThread.stop()
        # Wait a bit for server EOF (Doesn't seem to work)
        # while self.mudReaderThread.is_alive(): 
        #     self.mudReaderThread.join(10)  
        #     if self.mudReaderThread.is_alive():
        #         magentaprint("No server EOF")
        #         self.mudReaderThread.stop()  # No EOF

        self.mudListenerThread.stop()
        self.mudReaderThread.join(10)
        self.mudListenerThread.join(10)
        self.telnetHandler.close();
        magentaprint("Closed telnet.")

        # print("It should be safe to ctrl + c now")
        # time.sleep(10)   # This was so I could see error messages in the windows prompt...

    def write_username_and_pass(self):
        if len(sys.argv) >= 3:
            self.character.name = sys.argv[1].title()
            self.telnetHandler.write(self.character.name)
            self.telnetHandler.write(sys.argv[2])
        else:
            # With the MUD thread going already, there is no need to prompt here.
            self.character.name = input()
            self.telnetHandler.write(self.character.name)
            password = getpass.getpass("")
            self.telnetHandler.write(password)

    def initialize_reactions(self):
        self.mudReaderHandler.register_reaction(WieldReaction(self.character, self.telnetHandler))

    def check_inventory(self):
        # This prints the inventory.  I like that.  
        # Inventory needs this to be up to date.
        self.character.inventory.get_inventory()

    def check_class_and_level(self):
        whois = Whois(self.mudReaderHandler, self.telnetHandler)
        whois.execute(self.character.name)
        self.character._class = CharacterClass(whois.character_class, self.telnetHandler)
        self.character.gender = whois.gender
        self.character.level = whois.level
        self.character.title = whois.title
        self.character.race = whois.race
        self.character.configure_health_and_mana_variables()
        self.character.set_monster_kill_list()
        for a in self.character._class.abilities:
            self.mudReaderHandler.register_reaction(a)

    def check_info(self):
        info = Info(self.mudReaderHandler, self.telnetHandler, self.character)
        info.execute()

    def watch_user_input(self):
        stopping = False;

        while not stopping:

            try:
                user_input = input(); 
            except (EOFError, KeyboardInterrupt) as e:
                magentaprint("Don't try to crash me!  Use 'quit'.", False)
                user_input = ""

            user_input = user_input.lstrip()

            if not self.mudReaderThread.is_alive():
                magentaprint("\nWhat happened to read thread?  Time to turf.\n")
                self.telnetHandler.write("")
                self.telnetHandler.write("quit")
                stopping = True

                if self.botThread != None and self.botThread.is_alive():
                    self.botThread.stop()
            elif user_input == "quit":
                # TODO:  correct if MUD prints "Please wait x more seconds"
                # after quit was sent.
                # self.telnetHandler.write(user_input)
                quit = Quit(self.mudReaderHandler, self.telnetHandler)
                stopping = True if quit.result == 'success' else False

                if self.botThread != None and self.botThread.is_alive():
                    self.botThread.stop()
            elif re.match("bot ?$|bot [0-9]+$", user_input):
                self.start_grind(user_input)
            elif re.match("crawl", user_input):
                self.start_crawl()
            elif re.match("goto [0-9]+$", user_input):
                self.start_goto(user_input)
            elif re.match("showto [0-9]+$", user_input):
                self.start_goto(user_input, True)
            elif re.match("stop$", user_input):
                self.stop_bot()
            elif re.match("fle?$|flee$", user_input):
                self.stop_bot()
                self.commandHandler.process(user_input)  
            else:
                self.commandHandler.process(user_input)

    def start_grind(self, user_input):
        M_obj = re.search("[0-9]+", user_input)

        if M_obj:
            starting_path = int(M_obj.group(0))
        else:
            starting_path = 0

        if self.botThread != None and self.botThread.is_alive():
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        else:
            self.botThread = GrindThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler,
                                       self.database,
                                       self.mud_map,
                                       starting_path)
            self.botThread.start()

    def start_crawl(self):
        if (self.botThread != None and self.botThread.is_alive()):
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        else:
            self.botThread = CrawlThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler,
                                       self.database,
                                       self.mud_map)
            self.botThread.start()

    def start_goto(self, user_input, is_show_to=False):
        M_obj = re.search("[0-9]+", user_input)

        if M_obj:
            starting_path = int(M_obj.group(0))
        else:
            starting_path = None

        if self.botThread != None and self.botThread.is_alive():
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        else:
            self.botThread = GotoThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler,
                                       self.database,
                                       self.mud_map,
                                       starting_path,
                                       is_show_to)
            self.botThread.start()


    def stop_bot(self):
        if (self.botThread != None and self.botThread.is_alive()):
            self.botThread.stop()
            #self.mudReaderHandler.unregister_reactions()

LosHelper().main()
