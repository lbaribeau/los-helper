
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

import sys, time, getpass, threading, atexit, re, os
from threading import Thread

# from system.import_tools import *
# import_subdir("../system")
# import_subdir("../gamelogic")
# import_subdir("../misc")
# import_subdir("../data")
# import_subdir("../bots")
# import_subdir("../reactions")
# import_subdir("../threads")

from misc_functions import *
from Character import Character
from CharacterClass import CharacterClass
from SmartGrindThread import SmartGrindThread
from SmartCrawlThread import SmartCrawlThread
from GotoThread import GotoThread
from MixThread import MixThread
from SlaveThread import SlaveThread
from CommandHandler import CommandHandler
from MudReaderHandler import MudReaderHandler 
from MudReaderThread import MudReaderThread 
from MudListenerThread import MudListenerThread 
from MyBuffer import MyBuffer 
from Inventory import Inventory 
from CombatReactions import CombatReactions
from SmartCombat import SmartCombat
from Info import Info 
from Whois import Whois
from Cartography import Cartography 
from BotReactions import *
from TelnetHandler import TelnetHandler 
from FakeTelnetHandler import FakeTelnetHandler 
from Quit import Quit

from Database import *
from MudMap import *

class LosHelper(object):

    def __init__(self):
        self.botThread = None
        magentaprint("LosHelper initializing...", False)
        self.mud_map_thread = threading.Thread(target=self.setup_mud_map)
        self.mud_map_thread.start()
        # self.mud_map_thread = threading.Thread(target=magentaprint, args=("setting up mud map in main thread",))
        # self.setup_mud_map()
        self.character = Character()
        
        if "-fake" in sys.argv:
            self.telnetHandler = FakeTelnetHandler()
            sys.argv.remove("-fake")
        else:
            self.telnetHandler = TelnetHandler()

        self.consoleHandler = newConsoleHandler() 
        self.MUDBuffer = MyBuffer()
        self.mudListenerThread = MudListenerThread(self.telnetHandler, self.MUDBuffer)
        self.mudReaderThread = MudReaderThread(self.MUDBuffer, self.character, self.consoleHandler)
        self.mudReaderHandler = MudReaderHandler(self.mudReaderThread, self.character)
        self.inventory = Inventory(self.mudReaderHandler, self.telnetHandler, self.character)
        self.character.inventory = self.inventory
        self.combat_reactions = CombatReactions(self.mudReaderHandler, self.character)

        self.bot_ready = False
        self.mud_map = None
        self.mudListenerThread.start()
        self.mudReaderThread.start()

        # With the MUDReaderThread going, we have the server's text and prompts now showing
        # magentaprint("LosHelper joining mud_map_thread.")  # Ha this print can cause the lock erroris
        self.mud_map_thread.join() 
        self.write_username_and_pass()
        self.initialize_reactions()
        self.check_inventory()
        self.check_class_and_level()
        self.check_info()

        self.commandHandler = CommandHandler(self.character, self.mudReaderHandler, self.telnetHandler)
        self.cartography = Cartography(self.mudReaderHandler, self.commandHandler, self.character)
    
    def close(self):
        self.mudListenerThread.stop()
        self.mudReaderThread.stop()
        self.mudListenerThread.join(10)
        self.mudReaderThread.join(10)
        self.telnetHandler.close();
        try:
            os.remove("no.db")
        except OSError:
            # pass
            magentaprint(str(OSError))
        magentaprint("Closed telnet.")

    def main(self):
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
                # self.telnetHandler.write(user_input)
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
            elif re.match("goto -?[0-9]+$", user_input):
                self.start_goto(user_input)
            elif re.match("showto -?[0-9]+$", user_input):
                self.start_goto(user_input, True)
            elif re.match("domix .+?", user_input):
                #domix 'tree root' berry 50 - first param must be exact match
                self.start_mix(user_input)
            elif re.match("slave", user_input):
                self.start_slave(user_input)
            elif re.match("bbuy (.+?)", user_input):
                try:
                    #bbuy item quant
                    M_obj = re.search("bbuy (.+?) ([\d]*)", user_input)
                    item = M_obj.group(1)
                    quantity = int(M_obj.group(2))

                    self.inventory.bulk_buy(item, quantity)
                except Exception as e:
                    magentaprint("Error in the bulk buy function" + str(M_obj.groups(0)), False)
                    raise e

            elif re.match("stop$", user_input):
                self.stop_bot()
            elif re.match("remap", user_input):
                self.mud_map.re_map()
            elif re.match("fle?$|flee$", user_input):
                self.stop_bot()
                self.commandHandler.process(user_input)  
            else:
                self.commandHandler.process(user_input)


    def setup_mud_map(self):
        magentaprint("Generating the mapfile....", False)
        self.mud_map = MudMap()
        magentaprint("Mapfile generated", False)
        self.bot_ready = True

    def write_username_and_pass(self):
        args = [s for s in sys.argv[1:] if not s.startswith('-')]
        magentaprint("LosHelper stripped args: " + str(args))

        if len(args) >= 1:
            self.character.name = args[0].title()
        else:
            self.character.name = input()

        self.telnetHandler.write(self.character.name)

        if len(args) >= 2:
            password = args[1]
        else:
            password = getpass.getpass("")

        self.telnetHandler.write(password)

        # if len(args) >= 2:
        #     self.character.name = args[1].title()
        #     self.telnetHandler.write(self.character.name)
        #     password = args[2]
        # else:
        #     # With the MUD thread going already, there is no need to prompt here.
        #     self.character.name = input()
        #     self.telnetHandler.write(self.character.name)
        #     password = getpass.getpass("")

        # self.telnetHandler.write(password)

    def initialize_reactions(self):
        self.mudReaderHandler.register_reaction(WieldReaction(self.character, self.telnetHandler))

    def check_inventory(self):
        # This prints the inventory.  I like that.  
        # Inventory needs this to be up to date.
        self.character.inventory.get_inventory()
        self.character.inventory.output_inventory()

    def check_class_and_level(self):
        whois = Whois(self.mudReaderHandler, self.telnetHandler, self.character)
        whois.execute(self.character.name)
        whois.wait_for_flag()
        self.character._class = CharacterClass(self.character.class_string, self.character.level, self.telnetHandler)
        # self.character.CAST_PERIOD = self.character._class.cast_wait
        # self.character.CAST_WAIT = self.character._class.cast_wait
        self.character.configure_health_and_mana_variables()
        self.character.set_monster_kill_list()
        for a in self.character._class.abilities:
            self.mudReaderHandler.register_reaction(a)

    def check_info(self):
        info = Info(self.mudReaderHandler, self.telnetHandler, self.character)
        info.execute()


    def start_grind(self, user_input):
        if not self.bot_ready:
            magentaprint("Please wait for the Mapfile before using this command", False)
            return False

        M_obj = re.search("[0-9]+", user_input)

        if M_obj:
            starting_path = int(M_obj.group(0))
        else:
            starting_path = 0

        if self.botThread != None and self.botThread.is_alive():
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        else:
            self.botThread = SmartGrindThread(self.character, 
                                              self.commandHandler, 
                                              self.mudReaderHandler,
                                              self.mud_map,
                                              starting_path)
            self.botThread.start()

    def start_crawl(self):
        if not self.bot_ready:
            magentaprint("Please wait for the Mapfile before using this command", False)
            return False

        if self.botThread != None and self.botThread.is_alive():
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        else:
            self.botThread = SmartCrawlThread(self.character, 
                                              self.commandHandler, 
                                              self.mudReaderHandler,
                                              self.mud_map)
            self.botThread.start()

    def start_goto(self, user_input, is_show_to=False):
        if not self.bot_ready:
            magentaprint("Please wait for the Mapfile before using this command", False)
            return False

        M_obj = re.search("-?[0-9]+", user_input)

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
                                        self.mud_map,
                                        starting_path,
                                        is_show_to)
            self.botThread.start()

    def start_slave(self, user_input):
        if not self.bot_ready:
            magentaprint("Please wait for the Mapfile before using this command", False)
            return False

        self.botThread = SlaveThread(self.character, 
                                     self.commandHandler, 
                                     self.mudReaderHandler,
                                     self.mud_map,
                                     "")
        self.botThread.start()

    def start_mix(self, user_input):
        if not self.bot_ready:
            magentaprint("Please wait for the Mapfile before using this command", False)
            return False

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

        if self.botThread != None and self.botThread.is_alive():
            magentaprint("It's already going, you'll have to stop it.  Use \"stop\".", False)
        elif can_mix:
            self.botThread = MixThread(self.character, 
                                       self.commandHandler, 
                                       self.mudReaderHandler,
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

L = LosHelper()
L.main()
L.close()
