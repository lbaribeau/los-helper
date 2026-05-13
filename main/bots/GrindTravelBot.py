
# Ok the idea is
# GrindThread does so many things so well
# Let's make another instance of it
# Just to travel
# Then it'll be able to chase, rest, flee, etc.
# A bit spaghetti code but hey better than copy pasting

# from bots.GotoThread import GotoThread
# from bots.GrindThread import GrindThread
from bots.TrackGrindThread import TrackGrindThread
from misc_functions import magentaprint
from collections import deque

class GrindTravelBot(TrackGrindThread):
    def __init__(self, character, command_handler, mudReaderHandler, mud_map):
        super().__init__(character, command_handler, mudReaderHandler, mud_map)

    # Ok we don't even need to make a thread, in this case, we can use the caller's thread
    # The caller won't call "run" because we aren't the same as GrindThread right now

    def goto(self, destination_id):
        # I might be hard-coding desitnation ids
        # And relying on the db get_path to work to get direction_list
        # At some point we will call a GrindThread function on self
        # But we have to make sure it's not an infinite loop that uses decide_where_to_go
        # So this is basically a super-heavyweight travel the same way track grind travels
        # self.direction_list = self.mud_map.get_path(self.character.AREA_ID, destination_id)
        self.direction_list = deque(self.mud_map.get_path(self.character.AREA_ID, destination_id))
        self.run() # I rewrote run to exit once we finish
        # Ok should GrindThread be a singleton or anything like that??!
        # I guess we'll find out

    def goto_given_direction_list(self, direction_list):
        self.direction_list = direction_list
        self.run()

    def run(self):
        # Ok let's inherit TrackGrindThread... in case that has some things we need... guess we can change it and test if needed later
        # Some hooks might be implemented there and not on GrindThread
        self.stopping = False
        self.character.ACTIVELY_BOTTING = False
        self.do_run_startup() # Does nothing, annoyingly (Both GrindThread and BotThread implement nothing)

        # while not self.stopping:
            # self.direction_list = self.decide_where_to_go()
        # magentaprint('BotThread.run: decide_where_to_go returned ' + str(self.direction_list))
        self.do_pre_go_actions() 
            # Can do shopping here, which can insert at the beginning of the direction list
            # Only does anything if we are in the chapel
            # Ok it has some legacy sketch
            # It prepends areaid_2 if we aren't in the chapel
            # It uses buffs
            # in_chapel() doesn't seem to help much

        while self.direction_list and not self.stopping:
            magentaprint("GrindTravelBot has direction list")
            self.do_regular_actions() # mainly does combat, also does some healing
            if self.go(self.direction_list[0]):
                self.do_on_successful_go() # There was a typo before... implements "fled" (sets up for engage_monster to see on next loop iteration)
            else:
                if self.character.mobs.GO_BLOCKING_MOB != "":
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
                else:
                    pass
            # It's a loop, so we only need a hook on one side of it (no need for beginning + end hooks)
            #do_post_go_actions() # This doesn't seem necessary

        self.do_after_directions_travelled()
        magentaprint("GrindTravelBot BotThread looping, stopping is {0}".format(self.stopping))

    magentaprint("GrindTravelBot's BotThread loop finished now.")

    # We just have to set up "stop" to be called on this
    # It doesn't really have to be a "singleton"
    # We could garbage collect it

