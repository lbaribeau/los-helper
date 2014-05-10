from TelnetBotThread import *
from misc_functions import *
from MixingReactions import *

class MixThread(TelnetBotThread):
    def __init__(self, character_in=None, commandHandler=None, mudReaderHandler_in=None,
                inventory_in=None, mud_map=None, telnet_handler=None, target=None, mix_target=None, quantity=1):
        super(MixThread, self).__init__(character_in, commandHandler, mudReaderHandler_in, inventory_in, mud_map, telnet_handler)

        self.target = target
        self.mix_target = mix_target
        self.quantity = quantity

        self.mixing_reactions = MixingReactions(mudReaderHandler_in, telnet_handler)

    def stop(self):
        super(MixThread, self).stop()
        self.mixing_reactions.finished = True

    def decide_where_to_go(self):
        return [] #later we can implement this guy to walk or something while mixing

    def do_after_directions_travelled(self):
        self.mixing_reactions.mix_batch(self.target, self.mix_target, self.quantity)

        while not self.mixing_reactions.finished:
            self.sleep(20)

        self.stop()