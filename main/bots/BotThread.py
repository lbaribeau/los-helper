
print("... ... ... ... BotThread from misc_functions import *"); from misc_functions import *

magentaprint("... ... ... ... BotThread import threading"); import threading
# from threading import Thread
magentaprint("... ... ... ... BotThread import atexit"); import atexit
magentaprint("... ... ... ... BotThread import time"); import time
magentaprint("... ... ... ... BotThread import re"); import re

magentaprint("... ... ... ... BotThread import Exceptions *"); from Exceptions import *
magentaprint("... ... ... ... BotThread import db.Database"); from db.Database import *
magentaprint("... ... ... ... BotThread import db.MudMap"); from db.MudMap import MudMap

magentaprint("... ... ... ... BotThread import comm.Spells"); from comm import Spells

# Refer to https://docs.python.org/3/library/threading.html
# excepthook is available as a method from threading
# Only override .__init__ and .run()

class BotThread(threading.Thread):
    def __init__(self, character, command_handler, mudReaderHandler, mud_map, name='BotThread'):
        # Thread.__init__(self)
        super().__init__(name=name) # Do this first
        self.stopping = False

        self.character        = character
        self.command_handler  = command_handler
        self.mudReaderHandler = mudReaderHandler
        self.inventory        = character.inventory
        self.smartCombat      = command_handler.smartCombat
        self.kill             = command_handler.smartCombat.kill
        self.cast             = command_handler.smartCombat.cast
        self.direction_list   = []

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
    3   regular  (actions on every node travelled through)
    4     on successful go
    5     on blocking mob
    6     on go please wait
    7     on go timeout
    8     on go no exit
    9  post go (similar to successful go except also applies to failed go)
    A  do after directions travelled
    '''
    def run(self):
        self.stopping = False
        self.character.ACTIVELY_BOTTING = False
        self.do_run_startup()

        while not self.stopping:
            self.direction_list = self.decide_where_to_go()
            magentaprint('BotThread.run: decide_where_to_go returned ' + str(self.direction_list))
            self.do_pre_go_actions() # Can do shopping here, which can insert at the beginning of the direction list

            while self.direction_list and not self.stopping:
                magentaprint("BotThread has direction list")
                self.do_regular_actions()
                if self.go(self.direction_list[0]):
                    self.do_on_successful_go() # area regex or too_dark matched
                else:
                    # if self.character.mobs.GO_BLOCKING_MOB != "":
                    if self.command_handler.go.blocked:
                        # MUDReaderThread sets GO_BLOCKING_MOB when go returns false
                        self.do_on_blocking_mob()
                        continue
                    # elif self.character.GO_PLEASE_WAIT:
                    elif self.command_handler.go.please_wait:
                        # Just try again.
                        self.do_on_go_please_wait()
                        continue
                    # elif self.character.GO_TIMEOUT:
                    elif self.command_handler.go.timed_out:
                        self.do_on_go_timeout()
                    # elif self.character.GO_NO_EXIT:
                    elif self.command_handler.go.result_no_exit:
                        self.no_exit_count += 1
                        self.do_on_go_no_exit()
                        continue
                    elif self.command_handler.go.result_go_where:
                        magentaprint("BotThread: Ok go command is really confused (no target)")
                    elif self.command_handler.go.result_cliff:
                        self.do_on_go_result_cliff()
                    else:
                        pass
                # It's a loop, so we only need a hook on one side of it (no need for beginning + end hooks)
                #do_post_go_actions() # This doesn't seem necessary

            self.do_after_directions_travelled()
            magentaprint("BotThread looping, stopping is {0}".format(self.stopping))

        magentaprint("BotThread: finished now.")

    def do_on_go_result_cliff(self):
        # Ok let's handle cliffs... let's try it without mountain boots... so... maybe rest, maybe try the cliff again
        C = self.command_handler.character
        if C.current_damage > 10 or C.hp < min(23,C.maxHP) or C.mp < C.maxMP/2:
            self.rest_to_full()
        # So... if we do nothing... the current "track" won't be popped.... so autopilot will try again until successful go
        # What might happen is small bore worms will pile up...
        # Could definitely be bad

    def go(self, exit_str):
        # Not overridden
        if self.stopping:
            return True

        # wait_for_move_ready(self.character)
        self.command_handler.go.wait_until_ready()
        self.kill.wait_until_ready()
        self.cast.wait_until_ready()
        magentaprint("BotThread going " + exit_str + (". %.1f" % (time.time() - self.character.START_TIME)), False)

        self.character.mobs.GO_BLOCKING_MOB = ""
        self.character.GO_PLEASE_WAIT  = False
        self.character.GO_NO_EXIT      = False
        self.character.GO_TIMEOUT      = False
        self.character.SUCCESSFUL_GO   = False

        # A go hook is something other than an exit name in the direction list
        # Custom actions like prepare, sell, and areaN which gets expanded into real directions
        hook_done = self.do_go_hooks(exit_str)
            # ... we need to wait for Cartography before this happens
        if hook_done:
            return hook_done
            # Okkkkk can get get a redo on the rest code like this
            # Maybe just have it add another rest_here to the direction list... oy
            # The point was to be able to call engage_monster from that rest code
            # But also for engage monster to be able to rest if it had to flee
            # Maybe need two functions
            # The rest code does call engage monster... maybe it should be recursive with the base case being all the monsters got handled... that could be what my infinite loop was
        else:
            # if re.match("(.*?door)", exit_str):
            #     self.command_handler.process("open " + exit_str)
                # self.command_handler.process('door')
            # self.command_handler.process("go " + exit_str)
            # self.command_handler.go.execute(exit_str)
            self.command_handler.go.persistent_execute(exit_str)
            # self.command_handler.go.wait_for_flag()
            # return self.command_handler.go.result is 'success'
            return self.command_handler.go.success
            # return self.check_for_successful_go()
            # if re.match("(.*?door)", exit_str):
            #     self.command_handler.process("open " + exit_str)
            # return self.go.persistent_execute(exit_str)

    ''' STATIC METHODS '''
    @staticmethod
    def has_ideal_stat(cur_value, ideal_value):
        return cur_value >= ideal_value
        # Why not put >= inline?

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
        # Ummm this isn't what ideal means to me :(

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
        # elif re.match("mobname *", exit_str):
            # Expand out "mobname" shortcut specified by TrackGrind
            # (Why not have TrackGrind expand it out?)
        return False

    ''' Defined Hooks in Run() '''
    def do_run_startup(self):
        #self.set_up_automatic_ring_wearing()
        #setup heal reactions
        #self.__stopping=False
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
        # magentaprint("BotThread.in_chapel(): MUD_AREA is " + str(self.character.MUD_AREA))
        # magentaprint("BotThread.in_chapel(): MUD_AREA.area is " + str(self.character.MUD_AREA.area))
        return self.character.AREA_ID == 2
        # return self.character.MUD_AREA.is_restorative

    def decide_where_to_go(self): #each logic thread will have to implement this function
        #self.direction_list = []
        raise NotImplementedError()

    def do_regular_actions(self):
        return

    def do_on_successful_go(self):
        self.direction_list.pop(0)
        # self.character.MOBS_JOINED_IN = []
        # self.character.MOBS_ATTACKING = []
        # Just let mobs.list get overwritten, don't set it to []
        self.no_exit_count = 0
        if self.command_handler.go.too_dark:
            # "It's too dark to see"
            self.character.mobs.list=[]      # Maybe Cartography also does this
            self.character.mobs.attacking=[] # Maybe Cartography also does this
            pot = self.inventory.get_first_reference("glowing potion")
            if pot:
                self.command_handler.drink.execute_and_wait(pot)
            elif Spells.light in self.character.spells and self.character.MANA>=5:
                self.command_handler.cast.cast_and_wait(Spells.light)
                while self.command_handler.cast.failure and not self.command_handler.cast.result_no_mana:
                    self.command_handler.cast.cast_and_wait(light)
                if self.command_handler.cast.result_no_mana:
                    magentaprint("BotThread couldn't cast light!")
            else:
                magentaprint("BotThread couldn't cast light!")
                return None
            # Let's simulate a "go" to correct area id
            # Did this before in GrindThread.engage_monster after a flee to find ourselves
            self.character.TRYING_TO_MOVE=True
            self.command_handler.go.clear()
            self.command_handler.go.cartography.clear() # Ok we are "simulating" a "go" pretty well here... both of them should get 
            self.command_handler.process("l")
            self.command_handler.go.wait_for_flag()

    def do_on_blocking_mob(self):
        # Ok well we TRIED to leave and COULDN"T
        # So we have to fight
        # We don'g have to fight all of attacking but we have to fight (or flee... but that could create more problems)
        # We'll fight and flee might kick in
        # We don't need global variables we can just start the engagement
        # Can presume mobs.list is still OK
        ref = self.character.mobs.get_ref_of_attacking_mob(self.command_handler.go.M_obj)
        self.engage_monster(ref, ref)
        # self.get_items()
        self.character.mobs.GO_BLOCKING_MOB = "" # Not big on using these global variables any more
        #self.engage_mobs_who_joined_in() # These might block as well
        #self.engage_any_attacking_mobs() # Could leave these behind
        #self.check_weapons()

        #if (not self.character.BLACK_MAGIC):
        #    self.heal_up()
        return

    def do_on_go_please_wait(self):
        # The go object handles 'Please wait 1 second' now... maybe not longer times though.
        self.command_handler.go.wait_until_ready() # object likely recorded please wait time
        magentaprint("Bot: Got please wait on a go attempt, retrying.", False)

    def do_on_go_timeout(self):
        magentaprint("Bot: Check go timed out.  Could be sys clock.")
        # This can happen when the system clock makes time.time() inconsistent.
        # Unless I can fix this I have to ignore this case and hope it worked.
        # self.direction_list.pop(0) # Assumes it was successful?
        old_aid = self.character.AREA_ID # Supposing we got a hiccup that made R.area Go not match
        self.sleep(5)
        self.command_handler.go.clear() # Makes sure that wait_for_flag() happens properly (Make sure we get notify() called on a regex match)
        self.command_handler.process('l')
        self.command_handler.go.wait_for_flag()
        # Could we check aids now?
        # self.character.MOBS_JOINED_IN = []
        # self.character.MOBS_ATTACKING = []
        if self.character.AREA_ID == old_aid:
            magentaprint("Go failed weirdly? I guess don't pop direction_list") # Try again...
        else:
            magentaprint("I think we got Go to match this time, so pop() and continue.")
            self.direction_list.pop(0)

    def do_on_go_no_exit(self):
        # This is a tough one.  Hopefully it never happens.  I'm gonna assume it happened
        # because the last go actually worked and was wrongly determined not to.
        magentaprint("Go no exit on: " + self.direction_list.pop(0) + ". Try a look and cross fingers.", False)
            # We did drop one of the directions... did we go twice north by accident? Try to prevent that
        # self.character.MOBS_JOINED_IN = []
        # self.character.MOBS_ATTACKING = []
        # Ok I have an error case
        #"go chapel" I don't see that exit (we are in the chapel)
        # So areaid2 is saying the path is length 1 (saying we are outside)
        # But we are inside... so let's just add a LOOK here???
        # (I don't get these hooks)
        self.command_handler.go.clear() # Makes sure that wait_for_flag() happens properly (Make sure we get notify() called on a regex match)
        self.command_handler.process('l')
        self.command_handler.go.wait_for_flag() # You gotta unset the flag though
        # Now we have to check our area ids to know, right? Presumably, we shouldn't have repeated? Presumably, we are already too late (go no exit)
        # We need to catch it when it times out
        # Well we "popped" direction list...
        # I've seen this case.. when area wasn't matching at all... so popping is good thing to try... area should match though

    def do_post_go_actions(self):
        return

    def do_after_directions_travelled(self):
        #after the direction list is empty do these things (Looking at you Goto Thread)
        self.character.mobs.damage=[]
        return

    '''General helper functions for starting cast threads or managing inventory could be included here to assist the child classes
    The idea would be to limit the scope of the helper classes to tasks all the logic threads would need otherwise we should have
    another abstract class added'''

    def is_character_class(self, class_str):
        return self.character._class.id == class_str
