
import threading
from threading import Thread
import atexit 
import time
import re

from misc_functions import *
from Exceptions import *
from db.Database import *
from db.MudMap import MudMap

class BotThread(threading.Thread):
    def __init__(self, character, commandHandler, mudReaderHandler, mud_map):
        # Thread.__init__(self)
        super().__init__()
        self.stopping = False

        self.character = character
        self.commandHandler = commandHandler
        self.mudReaderHandler = mudReaderHandler
        self.inventory = character.inventory
        self.smartCombat = commandHandler.smartCombat
        self.kill = commandHandler.smartCombat.kill
        self.cast = commandHandler.smartCombat.cast
        self.direction_list = []

        self.character.ACTIVELY_BOTTING = False

        self.no_exit_count = 0

        self.mud_map = mud_map
        create_tables()
        db.close()

        atexit.register(self.stop)

    def stop(self):
        self.stopping = True
        self.character.ACTIVELY_BOTTING = False

    def is_stopping(self):
        # A bit unnecessary
        return self.stopping

    def keep_going(self):
        self.stopping = False

    def sleep(self, duration):
        time.sleep(duration)
    '''
    BotThread hooks.  2 and 3 are the main ones
    1  run startup
    2  pre go   (actions when direction list has emptied)
    3  regular  (actions on every node travelled through)
    4   on successful go
    5   on blocking mob
    6   on go please wait
    7   on go timeout
    8   on go no exit
    9  post go (similar to successful go except also applies to failed go)
    A  do after directions travelled
    '''
    def run(self):
        self.stopping = False
        self.character.ACTIVELY_BOTTING = False
        self.do_run_startup()

        # Here is where the fun begins.
        while not self.stopping:
            if self.stopping:
                break

            self.do_pre_go_actions()

            if len(self.direction_list) is 0:
                self.direction_list = self.decide_where_to_go()
                magentaprint('decide_where_to_go returned ' + str(self.direction_list))

            while len(self.direction_list) is not 0 and not self.stopping:
                self.do_regular_actions()
                if self.go(self.direction_list[0]):
                    self.do_on_succesful_go()
                else:
                    if self.character.GO_BLOCKING_MOB != "":
                        # MUDReaderThread sets GO_BLOCKING_MOB when go returns false
                        self.do_on_blocking_mob()
                        continue
                    elif self.character.GO_PLEASE_WAIT:
                        # Just try again.
                        self.do_on_go_please_wait()
                        continue
                    elif self.character.GO_TIMEOUT:
                        self.do_on_go_timeout()
                    elif self.character.GO_NO_EXIT:
                        self.no_exit_count += 1
                        self.do_on_go_no_exit()
                        continue

                #now we add a hook for any actions in this new area
                self.do_post_go_actions()
            self.do_after_directions_travelled()

        magentaprint("BotThread: finished now.")

    def go(self, exit_str):
        if self.stopping:
            return True

        # wait_for_move_ready(self.character)
        self.commandHandler.go.wait_until_ready()
        self.kill.wait_until_ready()
        self.cast.wait_until_ready()
        magentaprint("Going " + exit_str + (". %.1f" % (time.time() - self.character.START_TIME)), False)

        self.character.GO_BLOCKING_MOB = ""
        self.character.GO_PLEASE_WAIT = False
        self.character.GO_NO_EXIT = False
        self.character.GO_TIMEOUT = False
        self.character.SUCCESSFUL_GO = False

        # A go hook is something other than an exit name in the direction list
        # Custom actions like prepare, sell, and areaN which gets expanded into real directions
        hook_found = self.do_go_hooks(exit_str)
            # ... we need to wait for Cartography before this happens

        if not hook_found:
            # if re.match("(.*?door)", exit_str):
            #     self.commandHandler.process("open " + exit_str)
                # self.commandHandler.process('door')
            # self.commandHandler.process("go " + exit_str)
            # self.commandHandler.go.execute(exit_str)
            self.commandHandler.go.persistent_execute(exit_str)
            # self.commandHandler.go.wait_for_flag()
            # return self.commandHandler.go.result is 'success'
            return self.commandHandler.go.success
            return self.check_for_successful_go()
            # if re.match("(.*?door)", exit_str):
            #     self.commandHandler.process("open " + exit_str)
            # return self.go.persistent_execute(exit_str)
        else:
            return hook_found  # (True - well, it's not a successful go but it's assumed to be a successful hook)

    ''' STATIC METHODS '''
    @staticmethod
    def has_ideal_stat(cur_value, ideal_value):
        return cur_value >= ideal_value

    @staticmethod
    def can_use_timed_ability(last_use, timeout):
        # cooldown = time.time() - last_use

        # if timeout < cooldown:
        #     return True

        # return False
        return timeout < time.time() - last_use

    @staticmethod
    def can_cast_spell(current_mana, spell_cost, knows_spell):
        return knows_spell and current_mana >= spell_cost

    @staticmethod
    def should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items):
        should_heal = not BotThread.has_ideal_stat(current_health, ideal_health)

        if should_heal:
            can_cast_spell = BotThread.can_cast_spell(current_mana, heal_cost, knows_spell)

            if can_cast_spell or has_healing_items:
                should_heal = True
            else:
                should_heal = False

        return should_heal

    def has_ideal_mana(self):
        return BotThread.has_ideal_stat(self.character.MANA, self.character.MANA_TO_WAIT)

    def has_ideal_health(self):
        return BotThread.has_ideal_stat(self.character.HEALTH, self.character.HEALTH_TO_HEAL)

    def do_go_hooks(self, exit_str):
        # add the path to a given areaid to out current direction_list
        if re.match("areaid[\d]*", exit_str):
            #magentaprint("go hook found with: " + str(self.direction_list), False)
            area_id = int(exit_str.replace("areaid", ""))
            self.direction_list.pop(0)

            try:
                path = self.mud_map.get_path(self.character.AREA_ID, area_id)

                if len(path) == 0:
                    self.direction_list = ["buffer"] + self.direction_list
                else:
                    self.direction_list = ["buffer"] + path + self.direction_list

            except Exception:
                magentaprint("BotThread.do_go_hooks() problem with go hook " + exit_str + ", unsuccessful go.")
                if len(self.direction_list) > 0:
                    self.direction_list.pop(0) #remove the areaid[/d]*
                return False
            #magentaprint("path added to list: " + str(self.direction_list), False)
            return True
        return False

    ''' Defined Hooks in Run() '''
    def do_run_startup(self):
        #self.set_up_automatic_ring_wearing()
        #setup heal reactions
        return

    def do_pre_go_actions(self):
        # Before starting a new direction list
        # We need a hook for chapel actions...
        # This is not before every go, just before (after) every direction list
        # (I think this in_chapel check will be unnecessary when another fix happens...
            # there's currently a bug where the direction list gets remade too often)
        self.do_regular_actions()
        # if self.in_chapel():
        #     self.rest_and_check_aura()
        #     self.check_weapons()
        #     self.check_armour()

    def in_chapel(self):
        magentaprint("BotThread.in_chapel(): MUD_AREA is " + str(self.character.MUD_AREA))
        return self.character.AREA_ID == 2
        # return self.character.MUD_AREA.is_restorative

    def decide_where_to_go(self): #each logic thread will have to implement this function
        #self.direction_list = []
        raise NotImplementedError()

    def do_regular_actions(self):
        return

    def do_on_succesful_go(self):
        self.direction_list.pop(0)
        # self.character.MOBS_JOINED_IN = []
        # self.character.MOBS_ATTACKING = []
        self.no_exit_count = 0

    def do_on_blocking_mob(self):
        #self.engage_monster(self.character.GO_BLOCKING_MOB)
        #self.get_items()
        #self.character.GO_BLOCKING_MOB = ""
        #self.engage_mobs_who_joined_in()
        #self.engage_any_attacking_mobs()
        #self.check_weapons()

        #if (not self.character.BLACK_MAGIC):
        #    self.heal_up()
        return

    def do_on_go_please_wait(self):
        # The go object handles 'Please wait 1 second' now... maybe not longer times though.
        magentaprint("Bot: Got please wait on a go attempt, retrying.", False)

    def do_on_go_timeout(self):
        magentaprint("Bot: Check go timed out.  Could be sys clock.")
        # This can happen when the system clock makes time.time() inconsistent.
        # Unless I can fix this I have to ignore this case and hope it worked.
        self.direction_list.pop(0)
        # self.character.MOBS_JOINED_IN = []
        # self.character.MOBS_ATTACKING = []
        self.sleep(6)

    def do_on_go_no_exit(self):
        # This is a tough one.  Hopefully it never happens.  I'm gonna assume it happened
        # because the last go actually worked and was wrongly determined not to.
        magentaprint("Go no exit on: " + self.direction_list.pop(0), False)
        # self.character.MOBS_JOINED_IN = []
        # self.character.MOBS_ATTACKING = []

    def do_post_go_actions(self):
        return

    def do_after_directions_travelled(self):
        #after the direction list is empty do these things (Looking at you Goto Thread)
        return

    '''General helper functions for starting cast threads or managing inventory could be included here to assist the child classes
    The idea would be to limit the scope of the helper classes to tasks all the logic threads would need otherwise we should have
    another abstract class added'''

    def is_character_class(self, class_str):
        return self.character._class.id == class_str
