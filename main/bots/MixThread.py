
from bots.TelnetBotThread import TelnetBotThread
from misc_functions import *
from reactions.MixingReactions import *

class MixThread(TelnetBotThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None, telnet_handler=None, target=None, mix_target=None, quantity=1):
        super().__init__(character, command_handler, mud_reader_handler, mud_map, telnet_handler)

        self.target = target
        self.mix_target = mix_target
        self.quantity = quantity

        self.mixing_reactions = MixingReactions(mud_reader_handler, telnet_handler, character.inventory)

    def stop(self):
        super().stop()
        self.mixing_reactions.finished = True

    def decide_where_to_go(self):
        return [] #later we can implement this guy to walk or something while mixing

    def do_after_directions_travelled(self):
        self.mixing_reactions.mix_batch(self.target, self.mix_target, self.quantity)

        while not self.mixing_reactions.finished:
            self.sleep(2)

        self.stop()