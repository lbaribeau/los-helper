
import time

from comm import RegexStore as R
from misc_functions import magentaprint
from mini_bots.mini_bot import MiniBot

# MiniBot is a wrapper implementing a way to run as a new thread or as a current thread
# - __init__(self): self.stopping = False; self.thread = None
# - stop(self): self.stopping = True
# - is_alive(self): is self.thread: return self.thread.is_alive()
# - start_thread(self): sets selt.thread = Thread(target=self.run()) ; sef.thread.start()

# Started by referring to from "Rest(Command)" and SellBot(MiniBot)

# class RestLoop(MiniBot, MobRegexReader):
# Ok well we need to be given "Mobs" since we'll need mobs.list so we don't have to inherit "MobRegexReader"... 
# So that "parent" probably doesn't need to exist...
# Hopefully I can use the functions on self.mobs...

class RestLoop(MiniBot):
    # The idea here is that mobs.attacking is jank that I don't want to mess with
    # Also no need to overload Rest(Command) which can stay simple.
    # So we are making an object that can subscribe to mob attacks... 
    # So we can rest, and wake up and kill a mob if it attacks
    # I guess we don't need command_handler?? If we end up with "chase" or "flee" well the caller will have to deal with that, right??
    # "Flee" will have called us in all likelihood

    # def __init__(self, char, command_handler, mud_map):
    def __init__(self, rest, mobs, character):
        super().__init__()
        # MobRegexReader.__init__(self)
        # self.command_handler = command_handler
        self.rest = rest
        # self.SC = smartCombat
        self.regex_cart = [
            # R.mob_arrived,
            # R.mob_left,
            # R.mob_wandered,
            # R.you_attack,
            R.mob_attacked,
            # R.mob_joined1,
            # R.mob_joined2,
            # R.mob_aggro,
            # R.ze_mob_died,
            # R.mob_defeated,
            # R.ze_mob_fled,
            # R.blocked_path
        ]
        self.attacked=False
        self.mobs=mobs
        self.character=character

    def notify(self, r, M):
        if r in R.mob_attacked:
            # Most of Mobs.py doesn't care WHICH mob is which, ie., which mob left... it only cares to have an accurate count
            # The only example code I see that uses "nth" is commented out of mobs attacking
            # self.attacked=match.
            # Ok this code is sketch... how does "c" make sense... i am expecting on mob to be hitting me (in the sentence) even if it's the 2nd stall holder
            # c = self.attacking.count(M.group('mob').strip()) # Counts existng instances of the mob in "attacking" (list)
            # if c == 0:
                # self.attacking.append(M.group('mob'))
            # else:
            #"__numbers3     = "(?P<nth>\d*1st|\d*2nd|\d*3rd|\d+th) "
            # Ok this regex can be 21st or 1st or 22nd or 23rd or 24th etc (5 though 9 are 5th, 6th, 7th, all "th")... or even 111th... the \d wildcard is one digit and the star makes it many
            # Ok time to start writing code...
            # ("Nth" being in the regex is great but I'm not sure it's ever been processed / parsed ie. to get stall 2)
            # Might need to edit the regex to parse out "n""

            # This code takes the mob text and finds out a reference for that mob
            # ie. "2nd stall holder" -> "stall 3" (supposing a stall bolder is present)

            self.attacking_mob_ref = self.mobs.get_ref_of_attacking_mob(M)
            # return self.attacking_mob_ref
        # super().notify(r, match)

    def run(self):
        # Was going to be GrindThread.rest_to_full()
        self.attacking_mob_ref = None
        self.stopping = False

        rest = self.rest
        # rest.execute_and_wait()
        # rest.execute()
        # if rest.success:
            # while self.health_ticks_needed()
            # self.health_ticks_needed()
        C = self.character

        if C.HEALTH >= C.maxHP and C.MANA >= C.maxMP:
            return

        rest.execute() # We're not even checking text that comes back...
        magentaprint("Entering RestLoop rest_to_full loop wait loop")
        while (C.HEALTH < C.maxHP or C.MANA < C.maxMP) and not self.stopping:
            # while C.mobs.attacking != [] and not self.stopping:
            # while self.attacking_mob_ref and not self.stopping:
            if self.attacking_mob_ref:
                # self.engage_any_attacking_mobs() # Outer loop is superfluous but that's fine (engage_any_attacking_mobs SHOULD empty mobs.attacking)
                # SC.target = str(monster)
                # SC.run()
                # Maybe call engage_monster?
                # Yeah just return up if we got attacked like it's an exception...
                # Caller can handle it... call engange_monster()... if win then call again, if loss then flee and call again that way, if chase well it could get complicated... 
                #probably add to path but rest 
                return self.attacking_mob_ref
                # Ok so I guess we aren't finishing the rest loop as intended...
                # Caller is actually engage_monster() wow... ok so SC fled, engage_monster notices and decides to rest... rest returns saying we got another one
                # So engage fights that one and calls rest again... shouldn't go infinite because the base case is that we will run out of attackers (we only return if there's an attacker)
                # Other base case is that we actually finish resting
                # So this isn't rest loop it's more like try_rest or something...... it is a loop though it's monitoring
                
                # rest.execute_and_wait()
                # rest.execute()
            time.sleep(1) # We're not even reacting immediately... why not just wait on self? Well we have to also notice if we are full HP... which is doable by subscribing to prompt
            # So it could be better
            
            # magentaprint("GrindThread rest_to_full() waiting, hopefully resting is active")
            # Very rudimentary check for combat interrupt... not sure any of the other code does it better though

        return None # Ok it's a bit bananas but, if we return an attacking mob, engage_monster will get called again... will it know to rest again though??

        # Rest_until_ready had this bit to help the "go" regex... 
        # self.command_handler.prompt.clear()
        # self.command_handler.process('')
        # self.command_handler.prompt.wait()


# ___ 1st attempt in GrindThread before creating rest_loop.py ___

        # Ok it can actually call engage monster, creating a call stack loop
        # But only if mobs keep attacking us
        # So it shouldn't go infinite


        # # SEE REST_LOOP.PY
        # # Ok this one's new I went a long time with super-optimal resting code but now I'm like just type "rest" (ASAP), that'll get us to full
        # # Might we get attacked???
        # # I guess we fight if so...
        # # Should I make a "rest" command to check that it's working?
        # # self.command_handler.process("rest")

        # rest=self.command_handler.rest
        # # rest.execute_and_wait()
        # # rest.execute()
        # # if rest.success:
        #     # while self.health_ticks_needed()
        #     # self.health_ticks_needed()
        # C=self.character
        # rest.execute()
        # magentaprint("Entering GrindThread rest_to_full loop wait loop")
        # while (C.HEALTH < C.maxHP or C.MANA < C.maxMP) and not self.stopping:
        #     while C.mobs.attacking != [] and not self.stopping:
        #         self.engage_any_attacking_mobs() # Outer loop is superfluous but that's fine (engage_any_attacking_mobs SHOULD empty mobs.attacking)
        #         # rest.execute_and_wait()
        #         rest.execute()
        #     self.sleep(2)
        #     # magentaprint("GrindThread rest_to_full() waiting, hopefully resting is active")
        #     # Very rudimentary check for combat interrupt... not sure any of the other code does it better though

        # # Rest_until_ready had this bit to help the "go" regex... 
        # # self.command_handler.prompt.clear()
        # # self.command_handler.process('')
        # # self.command_handler.prompt.wait()
        # # SEE REST_LOOP.PY
