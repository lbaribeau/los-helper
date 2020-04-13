
from bots.TrackGrindThread import TrackGrindThread
from misc_functions import *

class NoobGrindThread(TrackGrindThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None):
        super().__init__(character, command_handler, mud_reader_handler, mud_map, 0)
        self.track = ['purchase_key', 'unlock_south', 'south', 'get_book', 'trade_book', 'north',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'drop_keys'
        ]

    def stop(self):
        super().stop()

    def decide_where_to_go(self):
      return self.track[:]

    def do_pre_go_actions(self):
      self.check_weapons()
      self.buff_up()

    def do_go_hooks(self, exit_str):
      if exit_str == "purchase_key":
        self.command_handler.process("purchase key guide")
        return True
      elif exit_str == "unlock_south":
        self.command_handler.process("unlock south grey")
        return True
      elif exit_str == "get_book":
        self.command_handler.process("get lar")
        return True
      elif exit_str == "trade_book":
        self.command_handler.process("trade lar lib")
        return True
      elif exit_str == "asis_light":
        self.command_handler.process("ask guide light")
        self.sleep(5)
        return True
      elif exit_str == "unlock_east":
        self.command_handler.process("unlock east wood")
        return True
      elif exit_str == "engage_skelington":
        self.engage_monster('skeleton')
        return True
      elif exit_str == "drop_keys":
        self.command_handler.process("drop fragile yes")
        self.command_handler.process("drop fragile yes")
        self.command_handler.process("drop fragile yes")
        self.command_handler.process("drop fragile yes")
        self.command_handler.process("drop fragile yes")
        self.command_handler.process("drop fragile yes")
        self.command_handler.process("drop wood yes")
        self.command_handler.process("drop grey yes")
        return True
      else:
        return super().do_go_hooks(exit_str)

    def update_aura(self):
      return True