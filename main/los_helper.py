
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

import sys, time, getpass, threading, atexit, re, os, socket

# from system.import_tools import *
# import_subdir("../system")
# import_subdir("../gamelogic")
# import_subdir("../misc")
# import_subdir("../data")
# import_subdir("../bots")
# import_subdir("../reactions")
# import_subdir("../threads")

from misc_functions import *
from comm.Character import Character
from comm.CharacterClass import CharacterClass
from comm.command_handler import CommandHandler
from comm.MudReaderHandler import MudReaderHandler
from comm.MudReaderThread import MudReaderThread
from comm.MudListenerThread import MudListenerThread
from comm.MyBuffer import MyBuffer
from command.Inventory import Inventory
from reactions.CombatReactions import CombatReactions
from reactions.Mobs import Mobs
from combat.SmartCombat import SmartCombat
from command.Info import Info
from command.Whois import Whois
from command.SpellsCommand import SpellsCommand
from reactions.Cartography import Cartography
from reactions.BotReactions import *
# from reactions.WieldReaction import WieldReaction
from comm.TelnetHandler import TelnetHandler
from fake.FakeTelnetHandler import FakeTelnetHandler
from db.Database import *
from db.MudMap import *
from reactions.Prompt import Prompt
from reactions.health_monitor import HealthMonitor
from comm.analyser import Analyser

class LosHelper(object):
    def __init__(self):
        magentaprint("LosHelper initializing...", False)

        # self.initializer = Initializer()
        self.character = Character()
        self.character.prompt = Prompt()
        sys.argv = [s.strip() for s in sys.argv]  # removes \r since git can add them to run.sh

        if '-fake' in sys.argv:
            self.telnetHandler = FakeTelnetHandler()
            # sys.argv.remove("-fake")
        else:
            self.telnetHandler = TelnetHandler()

        # if self.threaded_map_setup:
        #     self.mud_map_thread.start()  # Don't forget to uncomment .join()
        self.consoleHandler = newConsoleHandler()
        self.MUDBuffer = MyBuffer()
        self.mudListenerThread = MudListenerThread(self.telnetHandler, self.MUDBuffer)
        self.mudReaderThread = MudReaderThread(self.MUDBuffer, self.character, self.consoleHandler)
        self.mud_reader_handler = MudReaderHandler(self.mudReaderThread, self.character)
        self.inventory = Inventory(self.telnetHandler, self.character)
        self.character.inventory = self.inventory
        self.analyser = Analyser(self.mud_reader_handler, self.character)
        self.mud_reader_handler.add_subscriber(self.character.prompt)
        self.mud_reader_handler.add_subscriber(self.inventory)
        self.mud_reader_handler.add_subscriber(self.character.mobs)

        # self.mud_map_thread.start()  # Don't forget to uncomment .join()
        self.mudListenerThread.start()
        self.mudReaderThread.start()

        # With the MUDReaderThread going, we have the server's text and prompts now showing
        # if self.threaded_map_setup:
        #     magentaprint("LosHelper joining mud_map_thread.")  # Ha this print can cause the lock error
        #     self.mud_map_thread.join()
        self.write_username_and_pass()
        self.initialize_reactions()
        self.check_class_and_level()
        self.check_spells()
        self.check_info()

        self.commandHandler = CommandHandler(self.character, self.mud_reader_handler, self.telnetHandler)
        self.cartography = Cartography(self.mud_reader_handler, self.commandHandler, self.character)
        self.commandHandler.go.cartography = self.cartography
            # Cartography shouldn't need commandHandler to fix dependencies

        self.character.TRYING_TO_MOVE = True  # required for mapping (Hack - look into this - better init for Goto)
        self.telnetHandler.write('l')  # Sets area id for mapping
        self.commandHandler.go.wait_for_flag()
        self.check_inventory()

    def close(self):
        self.mudListenerThread.stop()
        self.mudReaderThread.stop()
        magentaprint("Joining mud map thread.")
        self.join_thread(self.commandHandler.mud_map_thread)
        magentaprint("Joining botThread.")
        self.join_thread(self.commandHandler.botThread)
        # if self.threaded_map_setup:
        #     self.commandHandler.mud_map_thread.join()
        magentaprint("Joining mudListenerThread")
        self.mudListenerThread.join(10)
        magentaprint("Joining mudReaderThread")
        self.mudReaderThread.join(10)
        self.telnetHandler.close()
        magentaprint("Closed telnet.")
        flush_input()
        try:
            # Maybe it's better to remove on startup.
            os.remove("no.db")
        except OSError as e:
            if hasattr(e, 'errno') and e.errno != 2:
                # errno 2 means the file's not there.
                magentaprint("LosHelper os.remove(\"no.db\") error: " + str(e))
        magentaprint("Threads remaining: " + str(threading.active_count()))

    def join_thread(self, thread):
        if thread and thread.is_alive():
            thread.join(10)

    def main(self):
        stopping = False

        while not stopping:
            try:
                user_input = input()
            except (EOFError, KeyboardInterrupt) as e:
                magentaprint("LosHelper: " + str(e))
                user_input = ""

            user_input = user_input.strip()
            # magentaprint("LosHelper user_input: " + str(user_input))

            if not self.mudReaderThread.is_alive():
                magentaprint("\nRead thread is dead, we're cooked.\n")
                self.telnetHandler.write("")
                self.telnetHandler.write("quit")
                # self.telnetHandler.write(user_input)
                stopping = True
                self.commandHandler.stop_bot()
            elif user_input == 'quit':
                magentaprint("LosHelper calling commandHandler.quit.")
                stopping = self.commandHandler.quit()
            else:
                try:
                    self.commandHandler.process(user_input)
                except socket.error as e:
                    # if hasattr(e, 'errno') and e.errno is 32: # Broken pipe
                    magentaprint("LosHelper caught telnet error and quitting: " + str(e))
                    stopping = True
                    if hasattr(e, 'errno'): # Broken pipe
                        magentaprint("Errno: " + str(e.errno))
                    # else:
                    #     raise e
                except:
                    self.stopping = True
                    raise

    def write_username_and_pass(self):
        args = [s for s in sys.argv[1:] if not s.startswith('-') and s is not '']
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
        # TODO: Handle wrong user name

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
        pass
        # self.mud_reader_handler.register_reaction(WieldReaction(self.character, self.telnetHandler))

    def check_inventory(self):
        # This prints the inventory.  I like that.
        # Inventory needs this to be up to date.
        self.character.inventory.get_inventory()
        # self.character.inventory.output_inventory()

    def check_class_and_level(self):
        whois = Whois(self.mud_reader_handler, self.telnetHandler, self.character)
        whois.execute(self.character.name)
        whois.wait_for_flag()
        self.character._class = CharacterClass(self.telnetHandler, self.character.class_string, self.character.level)
        # self.character.CAST_PERIOD = self.character._class.cast_wait
        # self.character.CAST_WAIT = self.character._class.cast_wait
        self.character.configure_health_and_mana_variables()
        self.character.set_monster_kill_list()
        # magentaprint("LosHelper ability list: " + str(self.character._class.abilities))
        for a in self.character._class.abilities.values():
            # self.mud_reader_handler.register_reaction(a)
            # magentaprint("Added subscriber " + str(a))
            self.mud_reader_handler.add_subscriber(a)

    def check_spells(self):
        # magentaprint("LosHelper.check_spells() sleeping 2 sec.")
        # time.sleep(2)
        spells = SpellsCommand(self.telnetHandler, self.character)
        self.mud_reader_handler.add_subscriber(spells)
        spells.execute()
        spells.wait_for_flag()

    def check_info(self):
        info = Info(self.mud_reader_handler, self.telnetHandler)
        info.execute()
        # magentaprint("LosHelper.check_info() calling character.process_info()")
        self.character.info = info
        self.character.process_info()

L = LosHelper()
L.main()
L.close()
