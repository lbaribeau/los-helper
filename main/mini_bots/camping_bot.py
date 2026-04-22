
from mini_bots.mini_bot import MiniBot
# from combat.mob_target_determinator import MobTargetDeterminator
# from mini_bots.travel_bot import TravelBot
from misc_functions import magentaprint
import threading
from bots.GrindThread import GrindThread
from comm import RegexStore as R

class MobArriveWaiter(threading.Event):
    # We want this object to "subscribe" to regexes like "A dustman just arrived."
    # And provide a function for waiting for that.
    # The function can provide a reference...
    # Maybe this object knows the other mobs?
    # Maybe we implement this function on Mobs?
    # I think "Mobs" is a bit busy with other things to do, a new object is a good idea

    # def __init__(self, char, command_handler, mud_map):
    # def __init__(self, mobs, character):
    def __init__(self):
        super().__init__()
        # MobRegexReader.__init__(self)
        # self.command_handler = command_handler
        self.regex_cart = [
            R.mob_arrived,
            # R.mob_left,
            # R.mob_wandered,
            # R.you_attack,
            # R.mob_attacked,
            # R.mob_joined1,
            # R.mob_joined2,
            # R.mob_aggro,
            # R.ze_mob_died,
            # R.mob_defeated,
            # R.ze_mob_fled,
            # R.blocked_path
        ]
        # self.attacked=False
        # self.mobs=mobs
        # self.character=character
        self.clear() # Clear means people will now wait if they call wait

    def notify(self, regex, M_obj):
        self.M_obj = M_obj
        self.regex = regex
        self.set() # Set means people can go ahead if they are calling wait
        # self.attacking_mob_ref = self.mobs.get_ref_of_attacking_mob(M)

    def wait_for_mob(self, timeout=None):
        self.clear()
        self.wait(timeout)

    def stop(self):
        self.set()

# class CampingBot(MiniBot):
class CampingBot(GrindThread):
    # def __init__(self, character, command_handler, mud_map, rest_loop):
    def __init__(self, character, command_handler, mudReaderHandler, mud_map, rest_loop, current_AID):
        super().__init__(character, command_handler, mudReaderHandler, mud_map)
        self.rest_loop = rest_loop
        self.camp_AID  = current_AID
        self.stopping = False

    def stop(self):
        magentaprint("Ok stop was called in camping bot")
        super().stop()
        self.stopping=True
    # def set_up_current_location(self):
        # Do a "look" or just assume it's set

    def run(self):
        self.camp_here()

    def camp_here(self):
        C=self.character
        self.direction_list = []
        while not self.stopping:
            magentaprint("CampingBot camp_here starting, camping_bot.stopping: " +str(self.stopping))
            self.sleep(1) # Just to prevent spinning an infinite loop too fast if that would happen
            magentaprint("CampingBot chase is " + str(C.mobs.chase))
            if self.stopping:
                return

            # Gotta do "chase" off the top because otherwise the first thing is "rest"
            # if C.mobs.chase:
            # I think we can presume that we got directions added if .chase exists
            self.bothread_run_without_decide_where_to_go()  # Idea is to "chase" if we haven't (?)
                # Well if we call this loop (bothread run) then chasing is part of the function call (it goes while(direction_list))
            # This will burn up all existing directions... should probably do that regardless of chase
            # Ok yea try just calling that with nothing in case it has to cover "chase"
            # We could put a "rest" first... safer to chase first or rest first? I guess rest? Why isn't it chasing at all that's the real problem
            # Why didn't it work is the question... suppose I add "rest_here"
            # Does chase get unset or set?
            # We want do_regular_actions to set it but the whole point of inheriting grinthread is to be able to call it and have it chase also...
            # If we call "botthread_run" that might be so high level that chase gets unset?
            # Ehrm chase adds directions on so the idea is to go those directions... 

            # Ok that could have fought something and it could have run off so we might want to react to that, before putting "rest_here", 
            # might want to go through the top level again...
            # I think we want, while direction list... instead of just calling ... since things can get prepended to direction list, we keep calling until direction list is empty
            # Doesn't this call do that though?
            # Well in that case we know our state right now, we've done our chasing, the above does everything...
            # That's fair... so we just need to make sure that the above takes that swing in the dark

            if self.stopping:
                return
            # self.wait_for_mob(598) # < 10 m
            # mob_ref = self.mobs.get_ref_of_attacking_mob(self.command_handler.mob_arrive_waiter.M_obj)
            # I think just inherit Grindthread
            # Then call grindthread functions as necessary
            # Could assume the mob's in the kill list
            # Maybe manifest a grindthread
            # Ok instead of waiting off the bat can we call proper combat functions
            # self.rest_here()
            # fled_mob, fled_exit = (was going to call "engage" and get flee as return values")
            # (Instead we are putting "hooks" into direction list because rest could cause and engagement which could cause a chase)
            self.direction_list = ['rest_here'] # Ok I'm thinking that implements "chase" and attack retaliation
            self.bothread_run_without_decide_where_to_go() # should call rest_to_full...  (rest as the first order of business)
                # 'rest_here' will rest, engage, and hopefully chase anything that attacked while resting
                # I think "flee" also puts things onto the stack like rest again and the return direction
                # Ok 
            if self.stopping:
                return
            # Ok I think we were going to spam that just to make sure, right? Yeah...
            # It should neutralize itself if we are at 0
            # Ok I guess... 
            # Ok now maybe engage?
            # I think it always does that anyway, right?
            # Maybe it does... if it thinks it did a "go"
            # Ok in that case we are kinda done?
            # Just inifinite loop rest_here
            # but also if we are full then rest here anyway but don't return when full
            # I guess only call that function then?
            # We have a mob waiter to arrive
            # Ok rest to full then call do_regular_actions then call rest_to_full then call wait_for_mob_to_arrive?
            # Could we maybe do rest_to_full, kill_a_mobs_around if any, otherwise, just wait
            # if self.mobs.list:
            if not self.full_health_and_mana():
                magentaprint("CampBot called rest and aren't full hp/mana which I think is possible after flee or chase so just \"continue\"")
                continue 

            # Ok the idea here is that we've been able to "rest" and chase
            # self.do_regular_actions() # Will engage mobs around?
                # Might also add chase to the direction list etc.
                # Might also implement flee
                # I guess we call a high-level function and hope we get a lot of functionality coverage (chase, flee, engage)

                # The thing is "continue" will start the next fight (do_regular_actions) we actually needed to chase
                # Aha found it
                # We called .do_regular_actions
                # So we didn't end up chasing... we hit "continue" so chase didn't work because chase assumes direction list will get processed
                # And if we're not careful chase variables will get wiped
                # If we call it like this we don't get motion then chase variables get wiped

            # I think that maybe before resting we engaged the room? Well we may not have
            # I guess rest again?
            # Yeah just hit continue if we aren't full
            # (don't call self.do_regular_actions because that doesn't chase and then how do we chase without wiping out the chase variables)

            if self.stopping:
                return
            if not self.full_health_and_mana():
                magentaprint("CampBot called engage and we aren't full hp/mana which I think is possible after flee or chase so just \"continue\" again")
                continue

            # if not self.character.mobs.list:
            # Seems like we should implement chase here... maybe check if we fled or chased
            # I'm not too worried about "flee"... hmmm would be nice though

            if not self.ready_for_combat() or self.stopping:
                # What if weapon breaks... and we don't have a backup weapon... we exit!
                # (We are max hp right now)
                magentaprint(f"Camping bot noticed not ready for combat {not self.ready_for_combat}, maybe weapon broke, exiting!")
                break

            magentaprint("CampingBot mobs.list: "+str(C.mobs.list))
            if self.decide_which_mob_to_kill(C.mobs.list):
                magentaprint("Camping bot found mob to kill, continue should loop back, do a rest, engage the mob, (if we didn't see one we'd \camp\" (wait for one))")
                continue 
            else:
                magentaprint("CampingBot...  If there are no mobs to kill, that's when we call our new function, wait_for_mob_to_arrive(598)")
                self.command_handler.wait_for_mob_arrive(598)
                # Ehrm could we call self.decide_which_mob_to_kill?
                # Sure
                # You know there could be a mob there that we are deciding not to kill so we can't just check self.character.mobs.list

            # if fled_mob and fled_exit:
            #     self.find_return_path # Can we import or reuse GrindThread?
            #     self.command_handler.go.execute(fled_exit)
        magentaprint("Camping bot exiting altogether!")

    def bothread_run_without_decide_where_to_go(self):
        # Call self.camp_here...
        # --- COPIED CODE FROM BOTHREAD ---
        # I am just copy pasting functionality
        # I'm doing an edit to self.decide_where_to_go
        # I'm going to try to make use of things like rest_here and chase to make a bot that just camps but maybe kills mobs that arrive
        # This should help with aura I guess
        self.stopping = False
        self.character.ACTIVELY_BOTTING = False
        self.do_run_startup()

        # while not self.stopping:
            # self.direction_list = self.decide_where_to_go()
        magentaprint('CampingBot starting botthread loop, direction list is ' + str(self.direction_list))
        self.do_pre_go_actions() # Can do shopping here, which can insert at the beginning of the direction list

        # Ehrm does this while loop work??? I think so...
        

        while self.direction_list and not self.stopping:
            magentaprint("CampingBot looping on direction list, " + str(self.direction_list))
            self.do_regular_actions()
            magentaprint("CampingBot: do_regular_actions() exited so calling \"go\" (direction list is %s}" %(str(self.direction_list)))
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
                    magentaprint("CampingBot: Ok go command is really confused (no target)")
                elif self.command_handler.go.result_cliff:
                    self.do_on_go_result_cliff()
                else:
                    pass
            # It's a loop, so we only need a hook on one side of it (no need for beginning + end hooks)
            #do_post_go_actions() # This doesn't seem necessary

        magentaprint("CampingBot looping, stopping is {0}".format(self.stopping))
        self.do_after_directions_travelled()
        magentaprint("CampingBot: finished direction list (will likely rest).")

    def rest(self):
        self.rest_loop.run() # Okkkie this is not straightforward... actually fighting attackers took a lot of GrindThread functions
        # Ok we inherited grindthread

    def wait_for_mob(self, timeout=None):
        self.command_handler.wait_for_mob_arrive(timeout)

  