
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

import sys, time, getpass, threading, atexit, re
from threading import Thread

from import_tools import *
import_subdir("data")
import_subdir("bots")
import_subdir("reactions")

from misc_functions import *
from Character import Character
from CharacterClass import CharacterClass
from SmartGrindThread import SmartGrindThread
from SmartCrawlThread import SmartCrawlThread
from GotoThread import GotoThread
from MixThread import MixThread
from CommandHandler import CommandHandler
from MudReaderHandler import MudReaderHandler 
from MudReaderThread import MudReaderThread 
from MudListenerThread import MudListenerThread 
from MyBuffer import MyBuffer 
from Inventory import Inventory 
from CombatReactions import CombatReactions
from Info import Info 
from Whois import Whois
from Cartography import Cartography 
from BotReactions import *
from TelnetHandler import TelnetHandler 

from Database import *
from MudMap import *


class LosHelper(object):

    def __init__(self):
        magentaprint("Connecting to MUD and initializing....", False)
        self.character = Character()
        self.telnetHandler = TelnetHandler()
        self.consoleHandler = newConsoleHandler() 
        self.MUDBuffer = MyBuffer()
        self.mudListenerThread = MudListenerThread(self.telnetHandler, self.MUDBuffer)
        self.mudReaderThread = MudReaderThread(self.MUDBuffer, self.character, self.consoleHandler)
        self.mudReaderHandler = MudReaderHandler(self.mudReaderThread, self.character)
        self.inventory = Inventory(self.mudReaderHandler, self.telnetHandler)
        self.combat_reactions = CombatReactions(self.mudReaderHandler, self.character)

        magentaprint("Generating the mapfile....", False)
        self.mud_map = MudMap()
        self.commandHandler = CommandHandler(self.character, self.mudReaderHandler, self.telnetHandler)
        self.cartography = Cartography(self.mudReaderHandler, self.commandHandler, self.character)
        self.botThread = None

    def main(self):
        self.mudListenerThread.start()
        self.mudReaderThread.start()

        # With the MUDReaderThread going, we have the server's text and prompts now showing
        self.write_username_and_pass()
        self.set_up_auto_wield()
        self.check_inventory()
        self.check_class_and_level()
        self.check_info()
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

    def set_up_auto_wield(self):
        self.mudReaderHandler.register_reaction(WieldReaction(self.character, self.commandHandler))

    def check_inventory(self):
        # This prints the inventory.  I like that.  
        # Inventory needs this to be up to date.
        self.inventory.get_inventory()
        self.inventory.output_inventory()

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

            if(not self.mudReaderThread.is_alive()):
                magentaprint("\nWhat happened to read thread?  Time to turf.\n")
                self.telnetHandler.write(user_input)
                stopping = True

                if(self.botThread != None and self.botThread.is_alive()):
                    self.botThread.stop()

            elif(user_input == "quit"):
                # TODO:  correct if MUD prints "Please wait x more seconds"
                # after quit was sent.
                self.telnetHandler.write(user_input)
                stopping = True

                if(self.botThread != None and self.botThread.is_alive()):
                    self.botThread.stop()

            elif(re.match("bot ?$|bot [0-9]+$", user_input)):
                self.start_bot(user_input)
            elif(re.match("crawl", user_input)):
                self.start_crawl()
            elif(re.match("goto -?[0-9]+$", user_input)):
                self.start_goto(user_input)
            elif(re.match("showto [0-9]+$", user_input)):
                self.start_goto(user_input, True)
            elif(re.match("domix .+?", user_input)):
                self.start_mix(user_input)
            elif(re.match("bbuy (.+?)", user_input)):
                try:
                    M_obj = re.search("bbuy (.+?) ([\d]*)", user_input)
                    item = M_obj.group(1)
                    quantity = int(M_obj.group(2))

                    self.inventory.bulk_buy(item, quantity)
                except Exception as e:
                    magentaprint("Error in the bulk buy function" + str(M_obj.groups(0)), False)
                    raise e

            elif(re.match("stop$", user_input)):
                self.stop_bot()
            elif(re.match("remap", user_input)):
                self.mud_map = MudMap()
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
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        else:
            self.botThread = SmartGrindThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler,
                                       self.inventory,
                                       self.mud_map,
                                       starting_path)
            self.botThread.start()

    def start_crawl(self):
        if (self.botThread != None and self.botThread.is_alive()):
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        else:
            self.botThread = SmartCrawlThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler,
                                       self.inventory,
                                       self.mud_map)
            self.botThread.start()

    def start_goto(self, user_input, is_show_to=False):
        M_obj = re.search("-?[0-9]+", user_input)

        if (M_obj):
            starting_path = int(M_obj.group(0))
        else:
            starting_path = None

        if (self.botThread != None and self.botThread.is_alive()):
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        else:
            self.botThread = GotoThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler,
                                       self.inventory,
                                       self.mud_map,
                                       starting_path,
                                       is_show_to)
            self.botThread.start()

    def start_mix(self, user_input):
        M_obj = re.search("domix '(.+?)' (.+?)( [\d]*)?$", user_input)

        can_mix = True

        try:
            target = M_obj.group(1)
            mix_target = M_obj.group(2)

            try:
                quantity = int(M_obj.group(3).strip())
            except Exception:
                magentaprint(str(M_obj.groups()),False)
                quantity = 1
        except Exception:
            magentaprint(str(M_obj.groups()),False)
            can_mix = False

        if (self.botThread != None and self.botThread.is_alive()):
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        elif can_mix:
            self.botThread = MixThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler,
                                       self.inventory,
                                       self.mud_map,
                                       self.telnetHandler,
                                       target,
                                       mix_target,
                                       quantity)
            self.botThread.start()
        else:
            magentaprint("Input not recognized - cannot start the mixer!", False)


    def stop_bot(self):
        if (self.botThread != None and self.botThread.is_alive()):
            self.botThread.stop()
            #self.mudReaderHandler.unregister_reactions()

LosHelper().main()
