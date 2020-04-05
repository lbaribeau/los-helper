
from bots.TrackGrindThread import TrackGrindThread
from misc_functions import *
from reactions.MixingReactions import *

class NoobGrindThread(TrackGrindThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None):
        super().__init__(character, command_handler, mud_reader_handler, mud_map, 0)
        self.track = ['purchase_key', 'unlock_south', 'south', 'get_book', 'trade_book', 'unlock_east', 'east', 'west']
        self.character.MONSTER_KILL_LIST = ['skeleton']

    def stop(self):
        super().stop()

    def decide_where_to_go(self):
      return self.track[:]

    def do_pre_go_actions(self):
      magentaprint("rawr")  

    def do_go_hooks(self, exit_str):
      if exit_str == "purchase_key":
        self.commandHandler.process("purchase key guide")
        return True
      elif exit_str == "unlock_south":
        self.commandHandler.process("unlock south grey")
        self.commandHandler.process("drop grey yes")
        return True
      elif exit_str == "get_book":
        self.commandHandler.process("get lar")
        return True
      elif exit_str == "unlock_south":
        self.commandHandler.process("unlock south grey")
        self.commandHandler.process("drop grey yes")
        return True
      elif exit_str == "unlock_east":
        self.commandHandler.process("unlock east wood")
        return True
      else:
        return super().do_go_hooks(exit_str)

    def update_aura(self):
      return True