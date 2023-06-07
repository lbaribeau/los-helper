
from bots.TrackGrindThread import TrackGrindThread
from misc_functions import *

class NoobGrindThread(TrackGrindThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None):
        super().__init__(character, command_handler, mud_reader_handler, mud_map, 0)
        self.track = ['purchase_key', 'unlock_south', 'south', 'get_book', 'trade_book', 'north', 'buff',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'unlock_east', 'east', 'engage_skelington', 'west',
        'drop_keys'
        ]
        self.training_area = ['areaid86']
        self.probably_repair = False

        # if self.character.inventory.has('stout cudgel'):
        #   self.probably_repair = False
        #   self.command_handler.process('wield cudgel')

        # if self.character.inventory.has('fragile white key'):
        #   self.directions = ['drop_keys', 'areaid86']

        self.character.MONSTER_KILL_LIST = ['skeleton']
        self.character.CAN_FLEE = False

    def stop(self):
        self.character.CAN_FLEE = True
        super().stop()

    def decide_where_to_go(self):
      if self.character.AREA_ID != 86:
        return self.training_area[:]
      return self.track[:]

    def do_pre_go_actions(self):
      if self.character.inventory.has_broken("stout cudgel") or self.probably_repair:
        magentaprint("Need to fix my stout cudgel", False)
        # self.command_handler.weapon_bot.smithy_bot.go_repair("stout cudgel")        
        # self.command_handler.process('wield cudgel')
        self.directions = self.training_area[:]

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
      elif exit_str == "buff":
        self.buff_up()
        return True
      elif exit_str == "unlock_east":
        self.command_handler.process("unlock east wood")
        return True
      elif exit_str == "engage_skelington":
        self.engage_monster('skeleton')
        return True
      elif exit_str == "drop_keys":
        self.command_handler.process("drop key yes")
        self.command_handler.process("drop key yes")
        self.command_handler.process("drop key yes")
        self.command_handler.process("drop key yes")
        self.command_handler.process("drop key yes")
        self.command_handler.process("drop key yes")
        self.command_handler.process("drop key yes")
        self.command_handler.process("drop key yes")
        return True
      else:
        return super().do_go_hooks(exit_str)

    def update_aura(self):
      return True