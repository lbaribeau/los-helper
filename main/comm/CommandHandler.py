
import threading
from threading import Thread
import atexit 
import time
import re
import sys

import misc_functions
from misc_functions import magentaprint
from combat.SmartCombat import SmartCombat
from db.Database import *
from db.MudMap import *
from command.Go import Go
from comm import RegexStore
from bots.TrackGrindThread import TrackGrindThread
from bots.SmartGrindThread import SmartGrindThread
from bots.CrawlThread import CrawlThread
from bots.SmartCrawlThread import SmartCrawlThread
from bots.GotoThread import GotoThread
from bots.MixThread import MixThread
from bots.SlaveThread import SlaveThread
from command.Quit import Quit
from command.Command import Command
from reactions.CombatReactions import CombatReactions
from command.Buy import Buy
from command.Drop import Drop
from command.Get import Get
from comm.Spells import *

class CommandHandler(object):
    def __init__(self, character, mudReaderHandler, telnetHandler):
        self.threaded_map_setup = True

        self.character = character
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.inventory = character.inventory

        # mudReaderHandler.register_reaction(self.smartCombat.kill)
        # mudReaderHandler.register_reaction(self.smartCombat.cast)
        # mudReaderHandler.register_reaction(self.smartCombat)
        # self.smartCombat = SmartCombat(self.telnetHandler, self.character, Kill(telnetHandler), Cast(telnetHandler), Prompt(character))
        self.smartCombat = SmartCombat(self.telnetHandler, self.character)
        self.kill = self.smartCombat.kill
        self.cast = self.smartCombat.cast
        mudReaderHandler.add_subscriber(self.kill)
        mudReaderHandler.add_subscriber(self.cast)
        self.go = Go(telnetHandler, character)
        mudReaderHandler.add_subscriber(self.go)
        mudReaderHandler.add_subscriber(self.go.open)
        mudReaderHandler.add_subscriber(self.smartCombat.prompt)  
        mudReaderHandler.add_subscriber(self.smartCombat.wield)
        mudReaderHandler.add_subscriber(self.smartCombat.wield.second)
        mudReaderHandler.add_subscriber(self.smartCombat)
        mudReaderHandler.add_subscriber(self.smartCombat.use)
        self.combat_reactions = CombatReactions(self.character)
        mudReaderHandler.add_subscriber(self.combat_reactions)
        self.buy = Buy(telnetHandler)
        mudReaderHandler.add_subscriber(self.buy)
        self.drop = Drop(telnetHandler)
        mudReaderHandler.add_subscriber(self.drop)
        self.get = Get(telnetHandler)
        mudReaderHandler.add_subscriber(self.get)
        self.use = self.smartCombat.use

        if '-fake' in sys.argv:
            Go.good_mud_timeout = 2.0
            Command.good_mud_timeout = 2.0

        self.botThread = None
        self.mud_map = None
        self.mud_map_thread = None
        if self.threaded_map_setup:
            # Threading the db setup causes a locking error if the starting area needs to be saved
            self.mud_map_thread = threading.Thread(target=self.setup_mud_map)
            self.mud_map_thread.start()  # Don't forget to uncomment .join()
        else:
            # # self.mud_map = MudMap()
            # # self.bot_ready = self.mud_map.ready  # True
            # self.mud_map_thread = threading.Thread(target=magentaprint, args=("setting up mud map in main thread",))
            self.setup_mud_map()

    def setup_mud_map(self):
        # magentaprint("CommandHandler generating the mapfile....", False)
        self.mud_map = MudMap()
        magentaprint("CommandHandler: Mapfile completed.", False)

    def join_mud_map_thread(self):
        if self.threaded_map_setup:
            self.mud_map_thread.join(20)
            return not self.mud_map_thread.is_alive()
        else:
            return True

    # def process(self, user_input):
    #     try:
    #         self.handle_command(user_input)
    #     except socket.error as e:  # Broken pipe(?)
    #         # if hasattr(e, 'errno') and e.errno is 32: # Broken pipe
    #         magentaprint("CommandHandler caught telnet error and quitting: " + str(e))
    #         self.stopping = True
    #         if hasattr(e, 'errno'):
    #             magentaprint("Errno: " + str(e.errno)) 
    #         # else:
    #         #     raise e

    # def handle_command(self, user_input):
    def process(self, user_input):
        """ This CommandHandler function is the filter for user input that
        does some matching and calls functions based on that input.  The only
        commands that don't make it this far are 'quit', 'bot' and 'stop'.
        The reason for that is I didn't want CommandHandler to have to know
        at all about the bot, so the upper layer intercepts the relevant
        commands.  Also, when the bot is stopped on a flee, the calling layer
        handles stopping the bot."""

        the_split = user_input.split(' ')
        # user_input = the_split[0]
        arg1 = the_split[1] if len(the_split) >= 2 else None
        arg2 = the_split[2] if len(the_split) >= 3 else None
        # for a in [user_input.startswith(self.character._class.abilities.values()) for test in user_input.startswith)
        # elif any([user_input.startswith(a.command) for a in self.character._class.abilities.values()]):
        # for a in [a for a in self.character._class.abilities.values() if user_input().startswith(a.command)]
        for a in self.character._class.abilities.values():
            # Commands to start a thread trying to use an ability: 'hastec, searc, prayc...'
            if the_split[0].startswith(a.command):
                if the_split[0].endswith('c'):
                    a.spam(arg1)
                else:
                    magentaprint("CommandHandler executed " + str(a))
                    a.execute(arg1)
                return
        if user_input == 'ss':
            # Stops threads from abilities
            for a in self.character._class.abilities.values():
                a.stop()
            self.telnetHandler.write('')
        elif re.match('^ki? |^kill?', user_input):
            self.kill.execute(arg1)
        elif user_input.startswith('kk '):
            self.kill.start_thread(user_input.partition(' ')[2].strip())
        elif user_input == 'sk' or user_input == 'skc':
            self.kill.stop()
            self.smartCombat.stop()
            self.telnetHandler.write('')
        elif re.match('ca? |cast?', user_input):
            self.cast.cast(arg1, arg2)
        elif user_input.startswith('cc '):
            self.cast.start_thread(arg1, arg2)
        elif user_input == 'sc':
            self.cast.stop()
            self.smartCombat.stop_casting()
            self.telnetHandler.write('')
        elif user_input.startswith('kkc '):
            self.user_kkc(user_input.partition(' ')[2].strip())
        elif user_input.startswith('kk2 '):
            self.user_kk2(user_input.partition(' ')[2].strip())
        elif re.match('dro? ', user_input):
            self.user_dr(user_input)
        elif user_input.startswith('sellable'):
            magentaprint(str(self.inventory.sellable()))
        elif user_input.startswith('droppable'):
            magentaprint(str(self.inventory.droppable()))
        elif user_input.startswith('Sel'):
            self.inventory.sell_stuff()
        elif user_input.startswith('Dr'):
            self.inventory.drop_stuff()
        elif user_input == 'ga':
            # self.telnetHandler.write('get all')
            self.get.execute('all')
        elif user_input.startswith('go ') or re.match(str(self.character.EXIT_REGEX), user_input):
            if not user_input.startswith('go '):
                magentaprint("User input matched " + str(self.character.EXIT_REGEX) + ", going.")
            # TODO: Could this make a false positive?
            # self.go.persistent_execute(user_input)
            self.user_move(user_input)
        # elif self.go.is_direction(user_input) or re.match(str(self.character.EXIT_REGEX), user_input):
        elif self.go.is_direction(user_input):
            # self.go.persistent_execute(user_input)
            self.user_move(user_input)
            # routine which does appropriate waiting,
            # printing, and finally sending command.
        elif re.match('door?', user_input):
            # Hmph, I shouldn't have blocking calls here
            self.go.persistent_execute('door')
        elif re.match("find (.+)", user_input):
            self.find(user_input)
        elif re.match("wie?2 +[a-zA-Z]+( +\d+)?", user_input):
            self.user_wie2(user_input[4:].lstrip())
        elif re.match("fle?$|flee$", user_input):
            self.stop_bot()
            self.user_flee()
        elif user_input == 'use soup':
            self.smartCombat.use.healing_potion() 
        elif re.match("usec$", user_input):  # 'use c' following my pet syntax: end a command with 'c' to start a thread
            self.smartCombat.use.spam_pots()
        elif re.match("usec2$", user_input):
            self.smartCombat.use.spam_pots(prefer_big=True)
        elif re.match("su$", user_input):
            self.smartCombat.use.stop()
        elif re.match("bot ?$|bot [0-9]+$", user_input):
            self.start_track_grind(user_input)
        elif re.match("grind$", user_input):
            self.start_grind(user_input)
        elif re.match("crawl$", user_input):
            self.start_crawl()
        elif re.match("crawl2", user_input):
            self.start_smart_crawl()
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
            self.bbuy(user_input)
        elif re.match("stop$", user_input):
            self.stop_bot()
        elif re.match("remap", user_input):
            self.mud_map.re_map()            
        elif re.match("HASTING", user_input):
            magentaprint(str(self.character.HASTING), False)
        elif re.match("weapon1", user_input):
            magentaprint(self.character.weapon1, False)
        elif re.match("weapon2", user_input):
            magentaprint(self.character.weapon2, False)
        elif re.match("MONSTER_CHECK_FLAG", user_input):
            magentaprint(str(self.character.MONSTER_CHECK_FLAG), False)
        elif re.match("ml", user_input): #Monster List
            magentaprint(str(self.character.MONSTER_LIST), False)
            if self.KillThread != None:
                magentaprint("Cur KT Target: " + str(self.KillThread.target), False)
            magentaprint("Mobs Attacking " + str(self.character.MOBS_ATTACKING), False)
        elif re.match("aid", user_input): #Area ID
            magentaprint("CommandHandler character.AREA_ID: " + str(self.character.AREA_ID), False)
            magentaprint("CommandHandler character.MUD_AREA: " + str(self.character.MUD_AREA), False)
        elif re.match("(?i)last_dir", user_input):
            magentaprint("CommandHandler character.LAST_DIRECTION: " + str(self.character.LAST_DIRECTION), False)
        elif re.match("(?i)area_title", user_input):
            magentaprint("CommandHandler character.AREA_TITLE: " + str(self.character.AREA_TITLE), False)
        elif re.match("(?i)exit_list", user_input):
            magentaprint(str(self.character.EXIT_LIST), False)
        elif re.match("hp", user_input):
            magentaprint(str(self.character.HEALTH), False)
        elif re.match("(?i)experience", user_input):
            exp = self.character.EXPERIENCE
            expm = str(misc_functions.calculate_vpm(exp))
            magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, False)
            #magentaprint(str(exp), False)
        elif re.match("(?i)gold", user_input):
            #gold = self.character.GOLD  #Calculating GMP would require us to store gold differently
            #gpm = str(misc_functions.calculate_vpm(gold))
            #magentaprint("Gold this Session: " + str(gold) + " | Gold / MIN: " + gpm, False)
            magentaprint(str(self.character.GOLD), False)
        elif re.match("(?i)kills", user_input):
            kills = self.character.MOBS_KILLED
            magentaprint("Kills this Session: " + str(kills), False)
        elif re.match("(?i)dump", user_input):
            for attr in self.character.__dict__:
                magentaprint(str(attr) + " : " + str(self.character.__dict__[attr]), False)
        elif re.match("(?i)cecho", user_input):
            self.telnetHandler.echoing = not self.telnetHandler.echoing
        elif re.match("(?i)version", user_input):
            magentaprint("Version: " + str(misc_functions.VERSION), False)
            magentaprint(self.character.__dict__, False)
        elif re.match("(?i)report", user_input):
            self.combat_reactions.report()
        elif re.match("(?i)mobs_joined_in", user_input):
            magentaprint(self.character.MOBS_JOINED_IN, False)
        elif re.match("(?i)aura", user_input):
            magentaprint(str(self.character.AURA), False)        
        elif re.match("(?i)mobs_attacking", user_input):
            magentaprint(self.character.MOBS_ATTACKING, False)
        elif re.match("(?i)monster_kill_list", user_input):
            magentaprint(str(self.character.MONSTER_KILL_LIST), False)
        elif re.match("(?i)reactionlist", user_input):
            for r in self.mudReaderHandler.MudReaderThread.BotReactionList:
                magentaprint('    ' + str(r), False)
        elif re.match("cackle", user_input):
            misc_functions.verboseMode = not misc_functions.verboseMode
            magentaprint("Verbose mode changed", False)
        elif re.match("defecate", user_input):
            misc_functions.debugMode = not misc_functions.debugMode
            magentaprint("Debug Mode changed", False)
        elif re.match(str(self.character.EXIT_REGEX), user_input):
            self.user_move("go " + self.character.LAST_DIRECTION)
            magentaprint("Running go on EXIT_REGEX: " + str(self.character.EXIT_REGEX), False)
        elif user_input.startswith('item '):
            magentaprint('get_item_name_from_ref: ' + str(self.character.inventory.get_item_name_from_reference(user_input.partition(' ')[2])))
        else: # Doesn't match any command we are looking for
            self.telnetHandler.write(user_input) # Just shovel to telnet.

    def user_move(self, user_input):
        # if user_input.startswith("go "):
        #     exit = user_input.split(" ")[1]
        #     if exit == "nw":
        #         user_input = "nw"
        #     elif exit == "sw":
        #         user_input = "sw"
        #     elif exit == "ne":
        #         user_input = "ne"
        #     elif exit == "se":
        #         user_input = "se"

        # self.character.TRYING_TO_MOVE = True
        self.character.LAST_DIRECTION = user_input.replace('go ', '')
        self.kill.stop()
        self.cast.stop()
        now = time.time()
        # wait_from_move = self.character.MOVE_WAIT - (now - self.character.MOVE_CLK)
        wait_from_move = self.go.wait_time()
        # time_remaining = max(wait_from_move, self.kill.wait_time(), self.cast.wait_time(), 0);
        time_remaining = max(self.go.wait_time(), self.kill.wait_time(), self.cast.wait_time(), 0);
        # magentaprint("user_move: MOVE wait time: %.2f" % round(wait_from_move, 2))
        # magentaprint("user_move: kill.wait_time(): " + str(self.kill.wait_time()))
        # magentaprint("user_move: cast.wait_time(): " + str(self.cast.wait_time()))
        magentaprint("CommandHandler.user_move waiting %.1f" % round(time_remaining, 1))

        if time_remaining < 3.0:
            time.sleep(time_remaining)
            # self.character.MOVE_CLK = now
            # self.telnetHandler.write(user_input)
            self.go.persistent_execute(self.character.LAST_DIRECTION)   # Todo:  shouldn't use a hanging go call for human user
            # self.go.execute(self.character.LAST_DIRECTION)
        else:
            magentaprint("Wait %.1f more seconds." % time_remaining)

        # elif time_remaining < 1.0:
        #     magentaprint("(Python) Delaying by %.1f sec ..." % time_remaining)
        #     time.sleep(time_remaining)
        #     magentaprint("Sent.")
        #     self.character.MOVE_CLK = now
        #     self.telnetHandler.write(user_input)
        # else:
        
    def user_dr(self, user_input):
        [command, item] = user_input.split(" ", 1)
        user_input = "drop " + item
        self.telnetHandler.write(user_input)
    
    # Commented: user_kk is deprecated and this code also doesn't work
    def user_kk(self, monster):
        magentaprint("CommandHandler.telnetHandler: " + str(self.telnetHandler))
        # self.kill.engage(self.telnetHandler, argv[3:].lstrip())
        # self.kill.engage(self.telnetHandler, monster)
        self.kill.start_thread(monster)

        # if self.KillThread != None and self.KillThread.is_alive():
        #     self.KillThread.set_target(argv)
        #     self.KillThread.keep_going()
        # else:
        #     self.KillThread = KillThread(self.character, self.mudReaderHandler, self.telnetHandler, argv)
        #     self.KillThread.start()
    
    def user_sk(self):
        self.kill.stop()
        self.smartCombat.stop()
        # self.telnetHandler.write("")

    def user_cc(self, argv):
        # TODO: Bug for user input "cc "
        if argv == "":
            magentaprint("Usage:  cc <spell> [<target> [<number>]]")
            self.telnetHandler.write("") # TODO: Keep a prompt up to date so we can print
                                    # immediately instead of sending to mud.
            return        
        elif re.search(argv, " "):
            [spell, target] = argv.split(" ",1)
        else:
            spell = argv
            target = ""
        
        if self.CastThread != None and self.CastThread.is_alive():
            magentaprint("Updating existing cast thread.")
            self.CastThread.set_spell(spell)
            self.CastThread.set_target(target)
            self.CastThread.keep_going()
        else:
            self.CastThread = CastThread(self.character, self.mudReaderHandler, self.telnetHandler, spell, target)
            self.CastThread.start()      

    def user_kkc(self, argv):
        theSplit = argv.split(" ")
        n = len(theSplit)

        if argv == None or n == 1 and theSplit[0] == "":
            magentaprint("Usage:  kkc [<spell>] <target> [<number>]")
            self.telnetHandler.write("")  # TODO: Keep a prompt up to date so we can print
                                          # immediately instead of sending to mud.
        # elif n == 1 and theSplit[0] not == "":
        elif n == 1:
            spell = None
            target = theSplit[0]
        elif n == 2 and re.match("^\d+$", theSplit[1]):
            spell = None
            target = theSplit[0] + " " + theSplit[1]
        elif n == 2:
            spell = theSplit[0]
            target = theSplit[1]
        else:
            spell = theSplit[0]
            target = theSplit[1] + " " + " ".join(theSplit[2:])

        self.smartCombat.start_thread(target, spell)

    def user_kk2(self, argv):
        # Usage: "kk2 target"
        # Uses smart combat with level 2 spell
        teh_split = argv.split(" ")
        self.user_kkc(" ".join(teh_split))
        if self.smartCombat.favourite_spell is burn:
            teh_split.insert(0, fireball)
        elif self.smartCombat.favourite_spell is hurt:
            teh_split.insert(0, dustgust)
        elif self.smartCombat.favourite_spell is blister:
            teh_split.insert(0, waterbolt)
        elif self.smartCombat.favourite_spell is rumble:
            teh_split.insert(0, crush)
        self.user_kkc(" ".join(teh_split))

    def user_sc(self):
        self.cast.stop()
        self.smartCombat.stop_casting()
        self.telnetHandler.write("")

    def user_wie2(self, argv):
        self.telnetHandler.write("wield %s\n" % (argv))
        self.telnetHandler.write("second %s\n" % (argv))

    def user_flee(self):
        self.smartCombat.stop()
        self.cast.stop()
        # self.smartCombat.flee()
        now = time.time()
        # time_remaining = max(self.character.MOVE_WAIT - (now - self.character.MOVE_CLK),
        #                      self.kill.wait_time(), self.cast.wait_time())
        time_remaining = max(self.go.wait_time(), self.kill.wait_time(), self.cast.wait_time())
        self.cast.stop()
        self.smartCombat.stop_casting()
        # self.kill.start_thread(self.smartCombat.target)  # if smartCombat.thread.is_alive()
        magentaprint("Fleeing in %.1f sec ..." % time_remaining)
        first_sleep = max(time_remaining - self.kill.cooldown_after_success - 0.2, 0)
        second_sleep = time_remaining - first_sleep 
        time.sleep(first_sleep)

        # This sleep will allow KillThread to get one more swing in if there is time for it.
        # So we wait until time_remaining is 3 before stopping KillThread
        self.smartCombat.stop()
        self.kill.stop()
        magentaprint("KillThread is stopped, %.1f until escape." % time_remaining, False)

        if self.character.weapon1 != '':
            self.telnetHandler.write("rm " + self.character.weapon1)
        if self.character.weapon2 != '':
            self.telnetHandler.write("rm " + self.character.weapon2)

        if second_sleep < 0.1:
            second_sleep = 0.1

        time.sleep(second_sleep)
        
        now = time.time()
        # time_remaining = max(self.character.MOVE_WAIT - (now - self.character.MOVE_CLK),
        #                      self.kill.wait_time(), self.cast.wait_time())
        time_remaining = max(self.go.wait_time(), self.kill.wait_time(), self.cast.wait_time())
        self.character.MOVE_CLK = now
            
        # Note: in very few rare cases it may be better to flee once.  
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")
        self.telnetHandler.write("fl")
        magentaprint("Sent.", False)

        time.sleep(0.1)  

        if self.character.weapon1 != "":
            self.telnetHandler.write("wie " + self.character.weapon1)
        if self.character.weapon2 != "":
            self.telnetHandler.write("seco " + self.character.weapon2)

    def get_directions_from_where_we_are_to_area_id(self, to_area_id):
        directions = []
        try:
            if self.character.AREA_ID is not None:
                directions = self.mud_map.get_path(int(self.character.AREA_ID), int(to_area_id))
            else:
                magentaprint("I'm not sure where I am (CurAreaID: " + str(self.character.AREA_ID) + ")", False)
        except Exception:
            magentaprint("I couldn't find a way there (" + str(self.character.AREA_ID) + ") to (" + str(to_area_id) + ")",False)
        return directions

    # Bots
    # def start_bot(self, )
    def bot_check(self):
        if not self.mud_map:
            magentaprint("Joining mud map thread.")
            return self.join_mud_map_thread()
        elif self.botThread and self.botThread.is_alive():
            if self.botThread.stopping:
                magentaprint("BotThread continuing.")
                # self.botThread.stopping = False
            else:
                magentaprint("Bot already going.")
                # self.botThread.stop()
                # self.botThread.join()
            return False
        else:
            return True

    def start_track_grind(self, user_input):
        magentaprint("CommandHandler start_track_grind()")
        if not self.bot_check():
            return 

        M_obj = re.search("[0-9]+", user_input)

        if M_obj:
            starting_path = int(M_obj.group(0))
        else:
            starting_path = 0

        self.botThread = TrackGrindThread(self.character, self, self.mudReaderHandler, self.mud_map, starting_path)
        self.botThread.start()
  
    def start_grind(self, user_input):
        if not self.bot_check():
            return

        self.botThread = SmartGrindThread(self.character, self, self.mudReaderHandler, self.mud_map)
        self.botThread.start()

    def start_crawl(self):
        if not self.bot_check():
            return
        self.botThread = CrawlThread(self.character, self, self.mudReaderHandler, self.mud_map)
        self.botThread.start()

    def start_smart_crawl(self):
        if not self.bot_check:
            return
        self.botThread = SmartCrawlThread(self.character, self, self.mudReaderHandler, self.mud_map)
        self.botThread.start()

    def start_goto(self, user_input, is_show_to=False):
        if not self.bot_check():
            return

        M_obj = re.search("-?[0-9]+", user_input)

        if M_obj:
            area_to = int(M_obj.group(0))
        else:
            area_to = None

        self.botThread = GotoThread(self.character, self, self.mudReaderHandler, self.mud_map, area_to, is_show_to)
        self.botThread.start()

    def start_slave(self, user_input):
        if not self.bot_check():
            return
        self.botThread = SlaveThread(self.character, self, self.mudReaderHandler, self.mud_map, "")
        self.botThread.start()

    def start_mix(self, user_input):
        if not self.bot_check():
            return

        M_obj = re.search(r"domix (?P<target>[A-Za-z]+) (?P<mix_target>[A-Za-z]+)(?P<qty> \d+)?$", user_input)
        can_mix = True

        try:
            target = M_obj.group('target')
            mix_target = M_obj.group('mix_target')

            try:
                quantity = int(M_obj.group('qty').strip())
            except Exception:
                magentaprint(str(M_obj.groups()),False)
                quantity = 1
        except Exception:
            if M_obj:
                magentaprint(str(M_obj.groups()),False)
            else:
                magentaprint('start_mix(): cannot parse command (use held item as 1st argument and target as 2nd, held item gets worked.)')
            can_mix = False

        if can_mix:
            self.botThread = MixThread(self.character, self, self.mudReaderHandler, self.mud_map, self.telnetHandler, 
                                       target, mix_target, quantity)
            self.botThread.start()
        else:
            magentaprint("Input not recognized - cannot start the mixer!", False)

    def stop_bot(self):
        if self.botThread and self.botThread.is_alive():
            self.botThread.stop()

    def bbuy(self, user_input):
        try:
            #bbuy item quant
            M_obj = re.search("bbuy (.+?) ([\d]*)", user_input)
            item = M_obj.group(1)
            quantity = int(M_obj.group(2))

            self.inventory.bulk_buy(item, quantity)
        except Exception as e:
            magentaprint("Error in the bulk buy function" + str(M_obj.groups(0)), False)
            raise e

    def find(self, user_input):           
        M_obj = re.search("find (.+)", user_input)
        magentaprint("Finding: " + str(M_obj.group(1)))
        [areas, mob_locations] = MudMap.find(str(M_obj.group(1)))

        magentaprint("Areas found:", False)
        for area in areas:
            magentaprint("<" + str(area.id) + "> - " + area.name, False)

        magentaprint("Mobs found:", False)
        for mob_location in mob_locations:
            magentaprint("<" + str(mob_location.area.id) + "> - " + mob_location.mob.name, False)

    def quit(self):
        # Undesireable waiting for command response (hangs user input for a bit)
        # self.telnetHandler.write(user_input)
        magentaprint("CommandHandler quit")
        quit = Quit(self.mudReaderHandler, self.telnetHandler)
        magentaprint("CommandHandler quit returned " + str(quit.success))
        if quit.success:
            self.stop_bot()
        return quit.success
    
