
import threading
from threading import Thread
import atexit
import time
import re
import sys
import json

import misc_functions
from misc_functions import magentaprint
from db.Database import *
from db.MudMap import *
from db.ExitType import *
import comm.Spells
from combat.SmartCombat         import SmartCombat
from command.Go                 import Go
from comm                       import RegexStore
from bots.TrackGrindThread      import TrackGrindThread
from bots.SmartGrindThread      import SmartGrindThread
from bots.CrawlThread           import CrawlThread
from bots.SmartCrawlThread      import SmartCrawlThread
from bots.GotoThread            import GotoThread
from bots.MixThread             import MixThread
from bots.SlaveThread           import SlaveThread
from bots.TopDownGrind          import TopDownGrind
from bots.NoobGrindThread          import NoobGrindThread
from bots.TalkGrindThread import TalkGrindThread
from bots.CampGrindThread          import CampGrindThread
from command.Quit               import Quit
from command.Command            import Command
from reactions.CombatReactions  import CombatReactions
from command.Who                import Who
from combat.Kill                import Kill
from combat.Cast                import Cast
from command.Wield              import Wield
from command.Wield              import Second
from command.Buy                import Buy
from command.Ask                import Ask
# from command.Talk               import Talk
#from command.Drop               import Drop
from command.Get                import Get
from Aura                       import Aura
from comm.thread_maker          import ThreadMaker
from command.Repair             import Repair
from command.Mix                import Mix
from command.wear               import Wear
from command.hold               import Hold
from command.Remove               import Remove
from mini_bots.armour_bot       import ArmourBot
from command.equipment          import Equipment
from mini_bots.smithy_bot       import SmithyBot
# from mini_bots.weapon_bot     import WeaponBot
from mini_bots.weapon_bot2      import MainhandWeaponBot
# from mini_bots.simple_weapon_bot import SimpleWeaponBot
from mini_bots.travel_bot       import TravelBot
from reactions.referencing_list import ReferencingList
from mini_bots.sell_bot         import SellBot
from mini_bots.mix_bot         import MixBot
from command.CommandThatRemovesFromInventory import Sell, Drop, Drink, Use, Eat
from command.potion_thread import PotionThreadHandler, Consume
from command.Look               import Look

class CommandHandler(object):
    def init_map_and_bots(self):
        # magentaprint("CommandHandler generating the mapfile....", False)
        self.mud_map = MudMap() # Takes a few seconds
        # Initialize things that NEED the map
        # (The map takes a few seconds)
        self.armour_bot = ArmourBot(self.character, self, self.mud_map)
        self.mudReaderHandler.add_subscriber(self.armour_bot)
        self.weapon_bot.add_in_map(self.mud_map)
        self.travel_bot = TravelBot(self.character, self, self.mud_map)
        magentaprint("CommandHandler: Mapfile completed.", False)

    def __init__(self, character, mudReaderHandler, telnetHandler):
        # It's ok to have a "dependency injection container" that instantirates everything in one spot
        # Also, lately I'm ok with something like SmartCombat needing a long list of arguments
        # They are good arguments... it's a list of the commands it needs... it makes sense
        self.threaded_map_setup = True

        self.character        = character
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler    = telnetHandler
        self.inventory        = character.inventory

        # mudReaderHandler.register_reaction(self.smartCombat.kill)
        # mudReaderHandler.register_reaction(self.smartCombat.cast)
        # mudReaderHandler.register_reaction(self.smartCombat)
        # self.smartCombat = SmartCombat(self.telnetHandler, self.character, Kill(telnetHandler), Cast(telnetHandler), Prompt(character))
        self.combat_reactions = CombatReactions(self.character)
        mudReaderHandler.add_subscriber(self.combat_reactions)

        self.who = Who(self.telnetHandler, self.character)
        mudReaderHandler.add_subscriber(self.who)
        self.who.execute()
        # self.simple_weapon_bot = SimpleWeaponBot(self.telnetHandler, self.character)
        # mudReaderHandler.add_subscriber(self.simple_weapon_bot)
        # self.weapon_bot = WeaponBot(self.character, self) # This guy takes the map after it's available... seems like his functions should be made thread safe
        self.weapon_bot = MainhandWeaponBot(self.character, self) # This guy takes the map after it's available... seems like his functions should be made thread safe
        self.mudReaderHandler.add_subscriber(self.weapon_bot)

        self.kill = Kill(telnetHandler)
        mudReaderHandler.add_subscriber(self.kill)
        self.drink = Drink(telnetHandler, self.inventory)
        mudReaderHandler.add_subscriber(self.drink)
        self.use = Use(telnetHandler, self.inventory)
        mudReaderHandler.add_subscriber(self.use)
        self.drink = Drink(telnetHandler, self.inventory)
        mudReaderHandler.add_subscriber(self.drink)
        self.eat = Eat(telnetHandler, self.inventory)
        mudReaderHandler.add_subscriber(self.eat)
        self.cast = Cast(telnetHandler, self.use)
        mudReaderHandler.add_subscriber(self.cast)
        self.wield = Wield(character, telnetHandler, self.inventory)
        mudReaderHandler.add_subscriber(self.wield)
        self.second = Second(character, telnetHandler, self.inventory)
        mudReaderHandler.add_subscriber(self.second)
        # self.potion_thread_handler = PotionThreadHandler(Consume(self.use, self.drink, self.eat))
        self.potion_thread_handler = PotionThreadHandler(Consume(self.use, self.drink, self.eat))
        self.smartCombat = SmartCombat(self.kill,self.cast,self.potion_thread_handler,self.wield,self.telnetHandler,self.character,self.weapon_bot)
        mudReaderHandler.add_subscriber(self.smartCombat)

        self.go = Go(self.kill, self.cast, telnetHandler, character)
        mudReaderHandler.add_subscriber(self.go)
        mudReaderHandler.add_subscriber(self.go.open)
        self.buy = Buy(telnetHandler, character.inventory)
        mudReaderHandler.add_subscriber(self.buy)
        self.ask = Ask(telnetHandler)
        mudReaderHandler.add_subscriber(self.ask)
        # self.talk = Talk(telnetHandler)
        # mudReaderHandler.add_subscriber(self.talk)
        # self.drop = Drop(telnetHandler)
        # mudReaderHandler.add_subscriber(self.drop)
        self.get = Get(telnetHandler, character.inventory)
        mudReaderHandler.add_subscriber(self.get)
        self.repair = Repair(telnetHandler, character.inventory)
        mudReaderHandler.add_subscriber(self.repair)
        self.mix = Mix(telnetHandler, character.inventory)
        mudReaderHandler.add_subscriber(self.mix)
        # self.wear = Wear(telnetHandler)
        self.wear = Wear(telnetHandler, character.inventory)
        mudReaderHandler.add_subscriber(self.wear)
        self.hold = Hold(telnetHandler, character.inventory)
        mudReaderHandler.add_subscriber(self.hold)
        self.remove = Remove(telnetHandler)
        mudReaderHandler.add_subscriber(self.remove)
        # magentaprint(str(Equipment))
        self.equipment = Equipment(telnetHandler, character.is_headless)
        # self.eq_bot = EquipmentBot(character, self, self.mudReaderHandler, self.mud_map)
        mudReaderHandler.add_subscriber(self.equipment)
        mudReaderHandler.add_buffer_completion_subscriber(self.equipment)
        self.sell = Sell(telnetHandler, self.inventory)
        mudReaderHandler.add_subscriber(self.sell)
        self.drop = Drop(telnetHandler, self.inventory)
        mudReaderHandler.add_subscriber(self.drop)
        self.sell_bot = SellBot(self.character.inventory, self.sell, self.drop)
        self.mix_bot = MixBot(self.character, self.hold, self.mix, self.remove, self.drop)
        # Use will have to keep inventory up to date, right
        # That is if items support usable (small inhaler, white amulet, rods)
        self.look = Look(self.character.inventory, telnetHandler)
        mudReaderHandler.add_subscriber(self.look)

        if '-fake' in sys.argv:
            Go.good_mud_timeout = 2.0
            Command.good_mud_timeout = 2.0
            Go.cooldown_after_success = 0.2

        self.bot_thread = None
        self.mud_map = None
        self.mud_map_thread = None
        if self.threaded_map_setup:
            # Threading the db setup causes a locking error if the starting area needs to be saved
            self.mud_map_thread = threading.Thread(target=self.init_map_and_bots)
            self.mud_map_thread.start()  # Don't forget to uncomment .join()
        else:
            # # self.mud_map = MudMap()
            # # self.bot_ready = self.mud_map.ready  # True
            # self.mud_map_thread = threading.Thread(target=magentaprint, args=("setting up mud map in main thread",))
            self.init_map_and_bots()
        self.quick_directions = ['q']

        self.actions = {
            'go_smithy' : self.go_smithy,
            # 'go_pawn' : self.go_to_nearest_pawn_shop,
            'suit_up': self.suit_up,
            'bdrop' : self.bulk_drop,
            'domix' : self.do_mix,
            'lookup_armour' : lambda a : magentaprint(self.mud_map.lookup_armour_type(a)),
            'print_reactions' : lambda a : self.mudReaderHandler.print_reactions(),
            'weapon' : lambda a : self.start_weapon_bot()
            # re.compile('equ?|equip?|equipme?|equipment?') : lambda a : self.eq_bot.execute_eq_command()
            # re.compile('equ?|equip?|equipme?|equipment?') : lambda a : self.eq.execute()
        }

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

    def stop_abilities(self):
        for a in self.character._class.abilities.values():
            a.stop()
            self.telnetHandler.write("")

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
        args = user_input.partition(' ')[2] if len(the_split) >= 2 else None
        # for a in [user_input.startswith(self.character._class.abilities.values()) for test in user_input.startswith)
        # elif any([user_input.startswith(a.command) for a in self.character._class.abilities.values()]):
        # for a in [a for a in self.character._class.abilities.values() if user_input().startswith(a.command)]

        # Try making a data structure that we can loop through for this command business
        # >>> Problem: then the thing that we do has constraints...
        # command_iterator = [
        #     (lambda uinput : uinput == 'ss', self.stop_abilities()),
        #     (lambda uinput : re.match('^ki? |^kill?', uinput), self.kill.execute(arg1)),
        #     (lambda uinput : uinput.startswith('kk '), self.kill.start_thread(uinput.partition(' ')[2].strip())),
        #     (lambda uinput : any(uinput.split(' ')[0].startswith(a.command) for a in self.character._class.abilities.values())
        # ]
        # for a in self.character._class.abilities.values():
        #     command_iterator.extend([
        #         (lambda uinput: uinput.split(' ')[0].startswith(a.command) + 'c', a.spam(arg1)),
        #         (lambda uinput: uinput.split(' ')[0].startswith(a.command), a.execute(arg1))
        #     ])
        # actions = {
        # }
        # for a in self.character._class.abilities.values():
        #     actions[a.command] = lambda : a.execute()
        #     actions[a.command + 'c']
        # >>> Another: the ability commands have many compositions
        # Answer: do both

        # for action in self.actions.keys():
        if the_split[0] in self.actions.keys():
            magentaprint("Calling command handler action " + str(the_split[0]))
            self.actions[the_split[0]](args)
            return

        for ability in self.character._class.abilities.values():
            # Commands to start a thread trying to use an ability: 'hastec, searc, prayc...'
            if the_split[0].startswith(ability.command):
                if the_split[0].endswith('c'):
                    ability.spam(arg1)
                else:
                    magentaprint("CommandHandler executed " + str(ability))
                    ability.execute(arg1)
                return

        if user_input == 'ss':
            # Stops threads from abilities
            for a in self.character._class.abilities.values():
                a.stop()
            self.telnetHandler.write('')
        elif user_input == 'invdebug':
            # self.inventory.output_inventory()
            self.inventory.debug()
        elif re.match('chain (.+?;.+?)', user_input):
            # chain a series of commands together with a semicolon
            M_obj = re.search('^chain (.+?;.+?)$', user_input)
            commands = M_obj.group(1).split(';')
            for command in commands:
                self.process(command)

        elif re.match('^ki? |^kill?', user_input):
            self.kill.execute(arg1)
        elif user_input.startswith('kk '):
            self.smartCombat.stop()
            self.kill.start_thread(user_input.partition(' ')[2].strip())
        elif user_input == 'sk' or user_input == 'skc':
            self.kill.stop()
            self.smartCombat.stop()
            self.telnetHandler.write('')
        elif re.match('ca? |cast?', user_input):
            self.cast.cast(arg1, arg2)
        elif user_input.startswith('cc '):
            if self.smartCombat.thread and self.smartCombat.thread.is_alive():
                # See comments in user_cc
                self.smartCombat.stop_casting() # could keep attacking
            self.cast.start_thread(arg1, arg2)
        elif user_input == 'sc':
            self.cast.stop()
            self.smartCombat.stop_casting()
            self.telnetHandler.write('')
        elif user_input.startswith('kkc '):
            self.user_kkc(user_input.partition(' ')[2].strip())
        elif user_input.startswith('kks '):
            self.user_kk2(user_input.partition(' ')[2].strip(), stunlockmode=True)
        elif user_input.startswith('kkn '):
            self.user_kk2(user_input.partition(' ')[2].strip(), nervousmode=True)
        elif user_input.startswith('kl '):
            self.user_kk2(user_input.partition(' ')[2].strip(), continuemode=True)
        elif user_input.startswith('kk2 '):
            self.user_kk2(user_input.partition(' ')[2].strip())
        elif re.match('^(dro?|drop) ', user_input):
            # self.user_dr(user_input)
            self.drop.execute(user_input.split(" ", maxsplit=1)[1]) # This approach keeps the inventory correct
        elif re.match('^sell? ', user_input):
            # self.user_sell(user_input)
            self.sell.execute(user_input.split(" ", maxsplit=1)[1])
        elif user_input.startswith('sella'):
            #magentaprint(str(self.inventory.sellable()))
            # magentaprint(
            #     ReferencingList(
            #         [self.inventory.get(i) for i in self.inventory.sellable()]
            #     )
            # )
            # self.inventory.sellable()
            self.sell_bot.sellable()
        elif user_input.startswith('droppable'):
            magentaprint(str(self.inventory.droppable()))
        elif user_input.startswith('Sel') and not user_input.startswith('Sella'):
            # self.inventory.sell_stuff()
            self.sell_bot.sell_stuff() # Stoppable? Maybe not needed
        elif user_input.startswith('Dr') and not user_input.startswith('Dropp'):
            self.inventory.drop_stuff()
        elif user_input.startswith('ugo'):
            self.process("unlock east wood")
            self.process("east")
            self.user_move("east")
            # self.inventory.drop_stuff()
            self.sell_bot.drop_stuff()
        elif user_input == 'gopawn':
            self.travel_bot.go_to_nearest_pawn_shop() # Try ctrl C to kill the thread
        elif user_input == 'gotip':
            self.travel_bot.go_to_nearest_tip()
        elif user_input == 'ga':
            self.telnetHandler.write('get all')
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
        elif re.match("(wiel?|wield) ", user_input):
            self.wield.execute(user_input.partition(' ')[2])
        elif re.match("wie?2 +[a-zA-Z]+( +\d+)?", user_input):
            self.wield.execute_and_wait(user_input.partition(' ')[2])
            self.second.execute(user_input.partition(' ')[2])
            # self.user_wie2(user_input[4:].lstrip())
        elif re.match("wear? ", user_input):
            self.wear.execute(user_input.partition(' ')[2])
        elif re.match("(repai?|repair) ", user_input):
            self.repair.execute(user_input.partition(' ')[2])
        elif re.match("(lo?|look?) ", user_input):
            self.look.execute(user_input.partition(' ')[2])
        elif re.match("fle?$|flee$", user_input):
            self.stop_bot()
            self.user_flee()
        elif user_input == 'p':
            self.smartCombat.potion_thread_handler.consume.healing_potion()
        elif user_input.startswith('use '):
            self.use.execute(user_input.partition(' ')[2])
        elif re.match('drink? ', user_input):
            self.drink.execute(user_input.partition(' ')[2])
        # elif user_input.startswith('eat '):
        #     self.eat.execute(user_input.partition(' ')[2])
        elif user_input == 'pot':
            # NOTICE THIS COMMAND
            self.smartCombat.potion_thread_handler.consume.healing_potion()
        elif re.match("usec$", user_input):  # 'use c' following my pet syntax: end a command with 'c' to start a thread
            self.smartCombat.potion_thread_handler.spam_pots()
        elif re.match("usec2$", user_input):
            self.smartCombat.potion_thread_handler.spam_pots(prefer_big=True)
        elif re.match("su$", user_input):
            self.smartCombat.potion_thread_handler.stop()
        elif re.match("bot ?$|bot [0-9]+$", user_input):
            self.start_track_grind(user_input)
        elif re.match("reboot", user_input):
            self.character.server.reboot()
        elif re.match("noobgrind", user_input):
            self.start_noob_grind()
        # start the talk bot
        elif re.match("talkgrind", user_input):
            self.start_talk_grind(user_input)
        elif re.match("^gg$", user_input):
            self.telnetHandler.write('drink granite')
        elif re.match("dropkeys", user_input):
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
            self.telnetHandler.write('drop key yes')
        elif re.match("campgrind", user_input):
            self.start_camp_grind()
        elif re.match("grind$", user_input):
            self.start_grind(user_input)
        elif re.match("bot2$", user_input):
            self.start_top_down_grind(user_input)
        elif re.match("crawl$", user_input):
            self.start_crawl()
        elif re.match("crawl2", user_input):
            self.start_smart_crawl()
        elif re.match("goto -?[0-9]+$", user_input):
            self.start_goto(user_input)
        elif re.match("showto -?[0-9]+$", user_input):
            self.start_goto(user_input, True)
        elif re.match("slave", user_input):
            self.start_slave(user_input)
        elif user_input.startswith('buy '):
            self.buy.execute(user_input.partition(' ')[2])
        elif re.match("^(ask|talk)(.+?)?", user_input):
            M_obj = re.search("(?:ask|talk) (.+)", user_input)
            self.ask.execute(M_obj.group(1))
        elif re.match("bbuy (.+?)", user_input):
            self.bbuy(user_input)
        elif re.match("giver (.+?)", user_input):
            self.giver(user_input)
        elif re.match("equ?|equip?|equipme?|equipment?", user_input):
            self.equipment.execute()
        elif re.match("stop$", user_input):
            self.stop_bot()
        elif re.match("^q!$", user_input):
            raise Exception("Hard Quit!")
        elif re.match("aura (\d)", user_input):
            M_obj = re.search("aura (\d)", user_input)
            magentaprint(Aura.auras[int(M_obj.group(1))], False)
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
        elif re.match("mkl", user_input): #Monster List
            magentaprint(self.character.MONSTER_KILL_LIST, False)
            # magentaprint(self.SmartGrindThread.get_targets(), False)
        elif re.match("q ((\w+)\s?)+", user_input): #quick search
            self.quick_directions = user_input.split(' ')
            # for each word in the user input send a search command to the telnet handler

            for i in self.quick_directions:
                if self.quick_directions.index(i) == 0:
                    continue
                self.telnetHandler.write("look " + i)
        elif re.match("q", user_input): #quick search
            for i in self.quick_directions:
                if self.quick_directions.index(i) == 0:
                    continue
                self.telnetHandler.write("look " + i)
        elif re.match("hsdi", user_input):
            #quickly ask the heal slave to cast detect-invis on us
            self.telnetHandler.write("em wants to see with eyes unclouded by hate")
        elif re.match("bfexit", user_input):
            magentaprint("brute forcing all exits", False)
            exits = ExitType.get_hidden_exits()
            exit_objs = {}
            for exit in exits:
                first_word = exit.name.split(' ')[0]
                exit_objs[first_word] = first_word
            
            for unique_exit in exit_objs:
                self.telnetHandler.write("look " + unique_exit)
                time.sleep(0.2)
        elif re.match("ready?", user_input):
            is_ready = self.character.is_ready_for_tough_fight()
            magentaprint(str(is_ready), False)
        elif re.match("bfall", user_input):
            magentaprint("brute forcing all exits", False)
            exits = ExitType.get_all_exits()
            exit_objs = {}
            for exit in exits:
                first_word = exit.name.split(' ')[0]
                exit_objs[first_word] = first_word
            
            for unique_exit in exit_objs:
                self.telnetHandler.write("look " + unique_exit)
                time.sleep(0.2)
        elif re.match("bfdesc", user_input):
            area = self.character.MUD_AREA.area
            if area:
                description = re.sub(r'[!\.\?,\'\"]',' ',area.description)
                words = description.split(' ')
                unique_words = {}
                for word in words:
                    # if word is not a filler word then look at it
                    # remove punctuation from word
                    if len(word) < 4:
                        continue
                    word = re.sub(r's$','',word.lower())
                    unique_words[word.lower()] = word.lower()
                
                for unique_word in unique_words:
                    self.telnetHandler.write("look " + unique_word)
                    time.sleep(0.2)
        elif re.match("m2e (.+)", user_input):
            try:
                M_obj = re.search("m2e (.+)", user_input)
                self.character.MANA_TO_ENGAGE = int(M_obj.group(1))

                if (self.character.MANA_TO_ENGAGE == 0):
                    self.character.NEEDS_MAGIC = False
                else:
                    self.character.NEEDS_MAGIC = True
            except Exception as e:
                magentaprint("Can't set manage to engage!", False)
        elif re.match("h2e (.+)", user_input):
            try:
                M_obj = re.search("h2e (.+)", user_input)
                self.character.HEALTH_TO_HEAL = int(M_obj.group(1))
            except Exception as e:
                magentaprint("Can't set manage to engage!", False)
        elif re.match("ml", user_input): #Monster List
            try:
                magentaprint(str(self.character.MONSTER_LIST), False)
                if self.KillThread != None:
                    magentaprint("Cur KT Target: " + str(self.KillThread.target), False)
                magentaprint("Mobs Attacking " + str(self.character.MOBS_ATTACKING), False)
            except Exception as e:
                magentaprint(e, False)

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
            magentaprint("Starting gold: " + str(self.character.STARTING_GOLD), False)
            magentaprint("Current gold: " + str(self.character.GOLD), False)
            magentaprint("Profit: " + str(self.character.GOLD-self.character.STARTING_GOLD), False)
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
            report = self.combat_reactions.report(False)
            report['mkl'] = self.character.MONSTER_KILL_LIST
        elif re.match("(?i)mobs_joined_in", user_input):
            magentaprint(self.character.MOBS_JOINED_IN, False)
        elif re.match("(?i)aura", user_input):
            magentaprint(str(self.cast.aura))
            magentaprint(str(self.character.preferred_aura))
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
            magentaprint('get_item_name_from_ref: ' + \
                str(self.character.inventory.get_item_name_from_reference(user_input.partition(' ')[2]))
            )
            magentaprint('item_from_ref: ' + \
                str(self.character.inventory.item_from_reference(user_input.partition(' ')[2]))
            )
            magentaprint('name_from_ref: ' + \
                str(self.character.inventory.name_from_reference(user_input.partition(' ')[2]))
            )
        elif user_input.startswith('ref '):
        # elif user_input.startswith('lastref '):
            magentaprint("get_last_reference('%s'): %s" % \
                (user_input.partition(' ')[2], self.character.inventory.get_last_reference(user_input.partition(' ')[2]))
            )
        # elif user_input.startswith('count '):
            magentaprint("inventory.count('%s'): %s" % \
                (user_input.partition(' ')[2], self.character.inventory.count(user_input.partition(' ')[2]))
            )
        # elif user_input.startswith('ref '):
            magentaprint("inventory.get_reference('%s'): %s" % \
                (user_input.partition(' ')[2], self.character.inventory.get_reference(user_input.partition(' ')[2]))
            )
            magentaprint("inventory.get_first_reference('%s'): %s" % \
                (user_input.partition(' ')[2], self.character.inventory.get_first_reference(user_input.partition(' ')[2]))
            )
        elif user_input == 'i':
            self.inventory.get_inventory()
            #self.inventory.sellable()
        elif user_input == 'go_repair':
            self.armour_bot.start_thread()
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
        
    # def user_dr(self, user_input):
    #     # [command, item] = user_input.split(" ", maxsplit=1)
    #     # user_input = "drop " + item
    #     # self.telnetHandler.write(user_input)
    #     self.drop.execute(user_input.split(" ", maxsplit=1)[1]) # This approach keeps the inventory correct

    # def user_sell(self, user_input):
    #     # [command, item] = user_input.split(" ", maxsplit=1)
    #     # self.sell.execute(item)
    #     self.sell.execute(user_input.split(" ", maxsplit=1)[1])
    
    def user_kk(self, monster):
        # Commented: user_kk is deprecated and this code also doesn't work
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
    
    def user_ca(self, emote):
        self.telnetHandler.write('pray')
        self.telnetHandler.write('rest')

    def user_sk(self):
        self.kill.stop()
        self.smartCombat.stop()
        # self.telnetHandler.write("")

    def user_cc(self, argv):
        # This doesn't get called!
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

        if self.smartCombat and self.smartCombat.thread and self.smartCombat.thread.is_alive() and not self.smartCombat.stopping and spell:
            #if re.match('vi?g?o?r?', spell) or re.match('me?n?d?-?w?o?u?n?:
            # What about healing a party member???
            # Don't use smart combat then?
            # We like the vig reaction on it, right?
            # Very interesting
            # Friend won't become smartCombat.target certainly
            # Could just append the target to healing_spell
            # Eh smartCombat won't heal the friend if self hp is high, since it checks self hp
            # So, don't use smart combat if healing friend? Fair enough...
            # What about abilities... like turn... maybe you can queue it with turnc and sk
            # Is smart combat really bot combat
            # Well we like that it uses abilities
            # Let's have smart combat let the person change the spell, right
            # Maybe better would be to have it try to do it on its own
            # It can ask for vig amount, right...
            # Calculate a default based on piety.... yikes....
            # So better not use smartcombat in group?
            # Maybe cc kills smart combat and starts kk and cc
            # So we can open with combat ability then switch
            # That sounds good
            self.smartCombat.stop()
            self.kill.start_thread(user_input.partition(' ')[2].strip())
            # self.CastThread.set_spell(spell)
            # self.CastThread.set_target(target)
            # self.CastThread.keep_going()

            # if spell.startswith('v'):
            #     self.smartCombat.healing_spell = 'v ' + target if target else 'v' 
            # elif spell.startswith('m'):
            #     self.smartCombat.healing_spell = 'm ' + target if target else 'm'
            # else:
            #     # Update smart combat with this cc command input
            #     # (Don't start a cast thread if smart combat is running)
            #     self.smartCombat.healing = spell # Now we have to worry about typos, right?
            #     # .spell is for black magic...

        if self.CastThread and self.CastThread.is_alive():
            magentaprint("Updating existing cast thread.")
            self.CastThread.set_spell(spell)
            self.CastThread.set_target(target)
            self.CastThread.keep_going()
        else:
            self.CastThread = CastThread(self.character, self.mudReaderHandler, self.telnetHandler, spell, target)
            self.CastThread.start()      

    def user_kkc(self, argv, stunlockmode=False, nervousmode=False, continuemode=False):
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

        # magentaprint("Command handler kkc with target " + target)
        self.smartCombat.start_thread(target, spell, stunlockmode, nervousmode, continuemode)
            

    def user_kk2(self, argv, stunlockmode=False, nervousmode=False, continuemode=False):
        # Usage: "kk2 target"
        # Uses smart combat with level 2 spell
        teh_split = argv.split(" ")
        self.user_kkc(" ".join(teh_split), stunlockmode, nervousmode)
        if self.smartCombat.favourite_spell is comm.Spells.burn:
            teh_split.insert(0, comm.Spells.fireball)
        elif self.smartCombat.favourite_spell is comm.Spells.hurt:
            teh_split.insert(0, comm.Spells.dustgust)
        elif self.smartCombat.favourite_spell is comm.Spells.blister:
            teh_split.insert(0, comm.Spells.waterbolt)
        elif self.smartCombat.favourite_spell is comm.Spells.rumble:
            teh_split.insert(0, comm.Spells.crush)
        self.user_kkc(" ".join(teh_split), stunlockmode, nervousmode, continuemode)

    def user_kk3(self, argv, stunlockmode=False, nervousmode=False):
        teh_split = argv.split(" ")
        self.user_kkc(" ".join(teh_split), stunlockmode, nervousmode)
        if self.smartCombat.favourite_spell is comm.Spells.burn:
            teh_split.insert(0, comm.Spells.burstflame)
        elif self.smartCombat.favourite_spell is comm.Spells.hurt:
            teh_split.insert(0, comm.Spells.shockbolt)
        elif self.smartCombat.favourite_spell is comm.Spells.blister:
            teh_split.insert(0, comm.Spells.waterbolt)
        elif self.smartCombat.favourite_spell is comm.Spells.rumble:
            teh_split.insert(0, comm.Spells.crush)
        self.user_kkc(" ".join(teh_split), stunlockmode, nervousmode)

    def user_sc(self):
        self.cast.stop()
        self.smartCombat.stop_casting()
        self.telnetHandler.write("")

    # def user_wie2(self, argv):
    #     self.telnetHandler.write("wield %s\n" % (argv))
    #     self.telnetHandler.write("second %s\n" % (argv))

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

        self.character.TRYING_TO_MOVE = True
        self.character.LAST_DIRECTION = None
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
        # elif self.bot_thread and self.bot_thread.is_alive():
        # elif self.bot_thread:
        #     if self.bot_thread.stopping:
        #         magentaprint("bot_thread continuing.")
        #         # self.bot_thread.stopping = False
        #     else:
        #         magentaprint("Bot already going.")
        #         # self.bot_thread.stop()
        #         # self.bot_thread.join()
        #     return False
        elif self.bot_thread:
            if self.bot_thread.is_alive():
                magentaprint("Bot already going.")
                return False
            else:
                return True
        else:
            return True

    def start_noob_grind(self):
        if self.bot_check():
            self.bot_thread = NoobGrindThread(self.character, self, self.mudReaderHandler, self.mud_map)
            self.bot_thread.start()

    # start talk grind
    def start_talk_grind(self, user_input):
        M_obj = re.search("talkgrind (.+)", user_input)
        target = None
        if M_obj:
            target = M_obj.group(1)

        if self.bot_check():
            self.bot_thread = TalkGrindThread(self.character, self, self.mudReaderHandler, self.mud_map, target)
            self.bot_thread.start()

    def start_campslave(self):
        if self.bot_check():
            self.bot_thread = SlaveThread(self.character, self, self.mudReaderHandler, self.mud_map, "camp", False)
            self.bot_thread.start()

    def start_camp_grind(self):
        if self.bot_check():
            self.bot_thread = CampGrindThread(self.character, self, self.mudReaderHandler, self.mud_map)
            self.bot_thread.start()

    def start_track_grind(self, user_input):
        magentaprint("CommandHandler start_track_grind()")
        self.character.DEAD=False # Use case: run bot after death from manual play
        if self.bot_check():
            M_obj = re.search("[0-9]+", user_input)

            if M_obj:
                starting_path = int(M_obj.group(0))
            else:
                starting_path = 0

            self.bot_thread = TrackGrindThread(self.character, self, self.mudReaderHandler, self.mud_map, starting_path)
            self.bot_thread.start()

    def start_grind(self, user_input):
        if self.bot_check():
            self.bot_thread = SmartGrindThread(self.character, self, self.mudReaderHandler, self.mud_map)
            self.bot_thread.start()

    def start_crawl(self):
        if self.bot_check():
            self.bot_thread = CrawlThread(self.character, self, self.mudReaderHandler, self.mud_map)
            self.bot_thread.start()

    def start_smart_crawl(self):
        if self.bot_check():
            self.bot_thread = SmartCrawlThread(self.character, self, self.mudReaderHandler, self.mud_map)
            self.bot_thread.start()

    def start_goto(self, user_input, is_show_to=False):
        if self.bot_check():
            M_obj = re.search("-?[0-9]+", user_input)

            if M_obj:
                area_to = int(M_obj.group(0))
            else:
                area_to = None

            self.bot_thread = GotoThread(self.character, self, self.mudReaderHandler, self.mud_map, area_to, is_show_to)
            self.bot_thread.start()

    def start_slave(self, user_input):
        M_obj = re.search("slave (.+)", user_input)
        master_input = M_obj.group(1)
        master = master_input
        kill = False

        if ' ' in master_input:
            master = user_input.split(' ')[0]
            kill = True

        if self.bot_check():
            self.bot_thread = SlaveThread(self.character, self, self.mudReaderHandler, self.mud_map, master, kill)
            self.bot_thread.start()

    def do_mix(self, user_input):
        if self.bot_check():
            # magentaprint(user_input, False)
            M_obj = re.search(r"(?P<target>[A-Z\sa-z]+) (?P<reageant>[A-Za-z]+)(?P<qty> \d+)?$", user_input)
            can_mix = True
            # magentaprint(M_obj, False)

            try:
                target = M_obj.group('target')
                reageant = M_obj.group('reageant')

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
                self.mix_bot.run(target, reageant, quantity)
            else:
                magentaprint("Input not recognized - cannot start the mixer!", False)

    def stop_bot(self):
        # magentaprint("CommandHandler.stop_bot() self.bot_thread: " + str(self.bot_thread))
        # if self.bot_thread:
        #     magentaprint("CommandHandler.stop_bot() self.bot_thread.is_alive(): " + str(self.bot_thread.is_alive()))
        # Error - smithy_bot doesn't have is_alive()
        # if self.bot_thread and self.bot_thread.is_alive():
        if self.bot_thread:
            self.bot_thread.stop()
        
        self.weapon_bot.stop()
        self.armour_bot.stop()
        self.travel_bot.stop()
        self.mix_bot.stop()

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

    def giver(self, user_input):
        try:
            #bbuy item quant
            M_obj = re.search("giver (.+?) (.+?) ([\d]*)", user_input)
            item = M_obj.group(1)
            target = M_obj.group(2)
            quantity = int(M_obj.group(3))

            self.inventory.bulk_give(item, target, quantity)
        except Exception as e:
            magentaprint("Error in the bulk buy function" + str(M_obj.groups(0)), False)
            raise e

    def bulk_drop(self, arg_string):
        # self.sell_bot.bulk_drop(argv=arg_string.split(' ', maxsplit=1)[1])
        if arg_string:
            unique_word = arg_string.split(' ')[0]
            if ' ' in arg_string:
                if arg_string.split(' ')[1] == 'all':
                    quantity = 'all'
                else:
                    quantity = int(arg_string.split(' ')[1])
            else:
                quantity = 'all'

            # self.inventory.bulk_drop(unique_word, quantity)
            self.sell_bot.bulk_drop(unique_word, quantity)
        else:
            magentaprint("Bulk drop missing arguments")

    def find(self, user_input):
        M_obj = re.search("find (.+)", user_input)
        magentaprint("Finding: " + str(M_obj.group(1)))
        [areas, mob_locations, mobs] = MudMap.find(str(M_obj.group(1)))

        magentaprint("Areas found:", False)
        for area in areas:
            magentaprint("<" + str(area.id) + "> - " + area.name, False)

        magentaprint("Mobs locations found:", False)
        for mob_location in mob_locations:
            magentaprint("<" + str(mob_location.area.id) + "> - " + mob_location.mob.name, False)

        if len(mobs) > 0:
            magentaprint("Mobs found:", False)
            for mob in mobs:
                name = mob.name
                level = mob.level
                approx_level = mob.approximate_level
                aura = mob.aura
                aura_str = None

                if aura is not None:
                    aura_str = Aura.auras[aura]

                magentaprint("{0}, lvl {1}/{2}, {3}/{4}".format(name, level, approx_level, aura, aura_str), False)


    def quit(self):
        # Undesireable waiting for command response (hangs user input for a bit)
        # self.telnetHandler.write(user_input)
        magentaprint("CommandHandler quit")
        quit = Quit(self.mudReaderHandler, self.telnetHandler)
        magentaprint("CommandHandler quit returned " + str(quit.success))
        if quit.success:
            self.stop_bot()
        return quit.success

    def go_smithy(self, args):
        if self.bot_check():
            # tdg = TopDownGrind(self.character, self, self.mudReaderHandler, self.mud_map)
            # self.bot_thread = ThreadMaker(tdg, 'go_to_nearest_smithy')
            magentaprint("CommandHandler.go_smithy()")
            self.bot_thread = SmithyBot(self.character, self, self.mud_map)
            # t = Thread(target=self.bot_thread.go_to_nearest_smithy)
            # t.start()  # The Bot should BE the thread for the sake of 'stopping'

            # We must check upon starting whether a thread is already going.  That's easiest the current way (bot_check).
            # s = SmithyBot(self.character, self, self.mudReaderHandler, self.mud_map)
            # self.bot_thread = Thread(target=self.bot_thread.go_to_nearest_smithy)
            # self.bot_thread.start()
            # If we keep the bot object, we can stop but we don't know when it completed.  If we keep the thread,
            # we can't stop the process.  What if SmithyBot has the thread.  Then I don't have to reconstruct the object
            # every time.  SmartCombat does this I think.
            self.bot_thread.start_thread()

    def suit_up(self, args):
        magentaprint("In suit_up")
        if self.bot_check():
            # self.bot_thread = ThreadMaker(self.armour_bot, 'suit_up')
            # self.bot_thread.start()
            self.bot_thread = self.armour_bot
            self.bot_thread.start_thread()

    def start_weapon_bot(self):
        if self.bot_check():
            self.bot_thread = self.weapon_bot
            self.bot_thread.start_thread()

    def start_top_down_grind(self, user_input):
        if self.bot_check():
            # self.bot_thread = Thread(target=, args=())
            self.bot_thread = TopDownGrind(self.character, self, self.mudReaderHandler, self.mud_map)
            self.bot_thread.start()
