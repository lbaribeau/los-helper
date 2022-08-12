
import re, time

from reactions.BotReactions import *
from misc_functions import *

class MixingReactions(BotReactionWithFlag):
    def __init__(self, mudReaderHandler, telnetHandler, inventory):
        super().__init__() # threading.Event
        self.prepare_success = "You finish preparing a (.+?)\."
        self.prepare_fail = "Your preparation of a (.+?) fails\."

        #self.mix_types = "(for eating|into a paste)"
        #self.mix = "You begin to mix a (.+?) " + self.mix_types + "\."
        #self.you_hold = "You hold a (.+?)\."

        self.regexes = [self.prepare_success, self.prepare_fail]

        self.mix_succeeded = False

        self.inventory = inventory
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)
        self.__class__.good_MUD_timeout = 15.0 #estimate of how long a mix should take
        self.fail_count = 0
        self.finished = False

    def notify(self, regex, M_obj):
        if regex is self.prepare_success:
            #excellent keep that root
            self.mix_succeeded = True
        elif regex is self.prepare_fail:
            #crud - ok we want to drop that bad root
            self.mix_succeeded = False

        super(MixingReactions, self).notify(regex, M_obj)  # sets __waiter_flag? Now sets threading.Event's internal flag

    def mix_target_to_target(self, target, mix_target):
        self.telnetHandler.write("hold " + target)
        self.telnetHandler.write("mix "+ mix_target)
        self.wait_for_flag()
        self.telnetHandler.write("rem " + target)
        return self.mix_succeeded

    def mix_batch(self, target, mix_target, quantity):
        magentaprint("Starting batch " + target + " | " + mix_target + " | " + str(quantity))
        i = 0
        self.fail_count = 0

        while i < quantity or self.finished:
            i = i + 1
            self.mix_target_to_target(target, mix_target)

            if not self.mix_succeeded:
                time.sleep(2) #give a chance for the remove to register in inventory
                self.inventory.drop_last(target)
                self.fail_count = self.fail_count + 1

        self.finished = True
        magentaprint("Finished batch with " + str(self.fail_count) + " failures" , False)
