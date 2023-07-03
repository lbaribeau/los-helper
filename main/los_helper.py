#!python3

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

print("Lands of Stone Helper loading code...")

import sys, time, getpass, threading, atexit, re, os, socket

# from system.import_tools import *
# import_subdir("../system")
# import_subdir("../gamelogic")
# import_subdir("../misc")
# import_subdir("../data")
# import_subdir("../bots")
# import_subdir("../reactions")
# import_subdir("../threads")

from misc_functions            import *
from comm.Character            import Character
from comm.CharacterClass       import CharacterClass
from comm.command_handler      import CommandHandler
from comm.MudReaderHandler     import MudReaderHandler
from comm.MudReaderThread      import MudReaderThread
from comm.MudListenerThread    import MudListenerThread
from comm.MyBuffer             import MyBuffer
from command.Inventory         import Inventory
from reactions.CombatReactions import CombatReactions
from reactions.Mobs            import Mobs
from combat.SmartCombat        import SmartCombat
from command.Info              import Info
from command.Whois             import Whois
from command.SpellsCommand     import SpellsCommand
from reactions.Cartography     import Cartography
from reactions.BotReactions    import *
# from reactions.WieldReaction import WieldReaction
from comm.TelnetHandler import TelnetHandler
from fake.FakeTelnetHandler import FakeTelnetHandler
from db.Database import *
from db.MudMap import *
from reactions.Prompt import Prompt
from reactions.server_reaction import ServerReaction
from reactions.health_monitor import HealthMonitor
from comm.analyser import Analyser
from Exceptions import *
from reactions.ring_reaction import RingWearingReaction

class LosHelper(object):
    def __init__(self):
        magentaprint("LosHelper instantiation...", False)

        # self.initializer = Initializer()
        self.character = Character()
        self.character.prompt = Prompt()
        self.character.server = ServerReaction()

        sys.argv = [s.strip() for s in sys.argv]  # removes \r since git can add them to run.sh

        # if name and password are not given, prompt for them and add them to sys.argv
        if len(sys.argv) < 2:
            sys.argv.append(input("Enter your character name: "))
        if len(sys.argv) < 3:
            sys.argv.append(getpass.getpass("Enter your password: "))

        if '-fake' in sys.argv:
            self.telnetHandler = FakeTelnetHandler()
            # sys.argv.remove("-fake")
        else:
            self.telnetHandler = TelnetHandler()

        self.do_login()

    def do_login(self):
        self.character.is_sleepy = False
        self.character.is_sleeping = False
        self.character.server.is_rebooting = False

        # if self.threaded_map_setup:
        #     self.mud_map_thread.start()  # Don't forget to uncomment .join()
        self.consoleHandler      = newConsoleHandler()
        self.MUDBuffer           = MyBuffer()
        self.mudListenerThread   = MudListenerThread(self.telnetHandler, self.MUDBuffer)
        self.mudReaderThread     = MudReaderThread(self.MUDBuffer, self.character, self.consoleHandler)
        self.mud_reader_handler  = MudReaderHandler(self.mudReaderThread, self.character)
        self.inventory           = Inventory(self.telnetHandler, self.character)
        self.character.inventory = self.inventory
        self.analyser            = Analyser(self.mud_reader_handler, self.character)
        self.mud_reader_handler.add_subscriber(self.character.prompt)
        self.mud_reader_handler.add_subscriber(self.character.server)
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

        self.do_login_actions()

    def do_login_actions(self):
        if '-headless' in sys.argv:
            self.character.is_headless = True

        self.check_info()

        self.command_handler = CommandHandler(self.character, self.mud_reader_handler, self.telnetHandler)
        self.cartography = Cartography(self.mud_reader_handler, self.command_handler, self.character)
        self.command_handler.go.cartography = self.cartography
            # Cartography shouldn't need command_handler to fix dependencies

        self.character.TRYING_TO_MOVE = True  # required for mapping (Hack - look into this - better init for Goto)
        self.telnetHandler.write('l')  # Sets area id for mapping
        self.command_handler.go.wait_for_flag()
        self.check_inventory()

        if '-grind' in sys.argv:
            self.command_handler.start_grind("grind")

        if '-noobgrind' in sys.argv:
            self.command_handler.start_noob_grind()

        if '-campslave' in sys.argv:
            self.command_handler.start_campslave()

        if '-fast' in sys.argv:
            self.character.MANA_TO_ENGAGE = 0
            self.character.NEEDS_MAGIC = False
            self.character.PREFER_BM = True

        # force to a lower level
        if '-level' in sys.argv:
            # get index of -level in sys.argv and then get the property in +1 position to set the level
            level_index = sys.argv.index('-level')
            level_to_set = sys.argv[level_index+1]
            if level_to_set.isdigit() and int(level_to_set) < self.character.info.level:
                self.character.info.level = int(level_to_set)
                self.character.level = int(level_to_set)
                magentaprint("Level rewrite set to " + str(level_to_set), False)
            else:
                magentaprint("Level rewrite not configured properly, ignoring arg", False)

        if '-weapon' in sys.argv:
            weapon_index = sys.argv.index('-weapon')
            weapon_type_to_set = sys.argv[weapon_index+1]
            
            # we expect weapon to be an index of 1 through 5 corresponding to the weapon type in info
            self.set_preferred_weapon_proficiency(weapon_type_to_set)
            self.character.process_info()

        
        if self.character._class.id != "Mon" and self.character._class.id != "Alc": #Alc's have a class ring
            # self.mud_reader_handler.register_reaction(RingWearingReaction(self.character.inventory, self.commandHandler))
            self.mud_reader_handler.register_reaction(RingWearingReaction(self.command_handler.wear, self.character.inventory))

    def set_preferred_weapon_proficiency(self, profficiency):
        try:
            # get info class property matching profficiency string
            preferred_proficiency_rank = self.character.weapon_proficiencies[profficiency]

            if preferred_proficiency_rank == 0:
                preferred_proficiency_rank = 1

            self.character.weapon_proficiencies = {
                'Sharp'   : 0, 
                'Thrust'  : 0, 
                'Blunt'   : 0,
                'Pole'    : 0, 
                'Missile' : 0
            }
            self.character.info.sharp = 0
            self.character.info.thrust = 0
            self.character.info.blunt = 0
            self.character.info.pole = 0
            self.character.info.missile = 0

            if profficiency == "Pole" and self.character._class.id == "Mon":
                # monks can't use t2 pole weapons so let's pretend our proficiency is 39
                magentaprint("LosHelper: Monk can't use t2 pole weapons, setting preferred weapon proficiency to 39", False)
                preferred_proficiency_rank = 39

            self.character.weapon_proficiencies[profficiency] = preferred_proficiency_rank
            setattr(self.character.info, profficiency.lower(), preferred_proficiency_rank)
            magentaprint("LosHelper: Set preferred weapon proficiency to " + profficiency, False)
            magentaprint("LosHelper: Weapon proficiencies: " + str(self.character.weapon_proficiencies), False)

            magentaprint("LosHelper: Info: " + str(self.character.info), False)
        except Exception as e:
            magentaprint("LosHelper: Invalid weapon proficiency: " + profficiency, False)
            return

    def close(self):
        self.mudListenerThread.stop()
        self.mudReaderThread.stop()
        magentaprint("Joining mud map thread.")
        self.join_thread(self.command_handler.mud_map_thread)
        magentaprint("Joining bot_thread.")
        self.join_thread(self.command_handler.bot_thread)
        # if self.threaded_map_setup:
        #     self.command_handler.mud_map_thread.join()
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
        a=threading.active_count()
        magentaprint(str(a) + ' thread' + ('s' if a > 1 else '') + ' remaining: ' + str(threading.enumerate()))

    def join_thread(self, thread):
        if thread and thread.is_alive():
            thread.join(10)

    def main(self):
        magentaprint("LosHelper main()", False)
        stopping = False

        while not stopping:
            try:
                user_input = input()
            except (EOFError, KeyboardInterrupt) as e:
                magentaprint("LosHelper: " + str(e))
                user_input = ""

            user_input = user_input.strip()
            # magentaprint("LosHelper user_input: " + str(user_input))

            if self.character.is_sleeping: #server reboot ready
                try:
                    stopping = self.command_handler.quit()
                    self.close()
                except Exception as e:
                    magentaprint(e.format("Error duringreboot {}"))

                magentaprint("LosHelper shutdown", False)
                time.sleep(5)
                magentaprint("LosHelper restarting", False)
                self.do_login()

            if not self.mudReaderThread.is_alive():
                magentaprint("\nRead thread is dead, we're cooked.\n")
                self.telnetHandler.write("")
                self.telnetHandler.write("quit")
                # self.telnetHandler.write(user_input)
                stopping = True
                self.command_handler.stop_bot()
            elif user_input == 'quit':
                magentaprint("LosHelper calling command_handler.quit.")
                stopping = self.command_handler.quit()
            else:
                try:
                    self.command_handler.process(user_input)
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
        args = [s for s in sys.argv[1:] if not s.startswith('-') and s != '']
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

# Timer limit?
# https://stackoverflow.com/questions/2933399/how-to-set-time-limit-on-raw-input/2933423#2933423

def do_startup():
    try:
        L = LosHelper()
        L.main()
        L.close()
    except Reboot:
        do_startup()
    return L

L = do_startup()
