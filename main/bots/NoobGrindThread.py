
from bots.TrackGrindThread import TrackGrindThread
from misc_functions import *

class NoobGrindThread(TrackGrindThread):
    keys = ['fragile white key', 'wooden key', 'light grey key']

    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None):
        super().__init__(character, command_handler, mud_reader_handler, mud_map, 0)

        self.reset = ['drop_keys', 'areaid86']
        self.setup_track = ['purchase_key', 'unlock_south', 'south', 'get_book', 'trade_book', 'north']
        self.skellington_track = ['buff', 'unlock_east', 'east', 'engage_skelington', 'west']
        self.probably_repair = False

        # if self.character.inventory.has('stout cudgel'):
        #   self.probably_repair = False
        #   self.command_handler.process('wield cudgel')

        # if self.character.inventory.has('fragile white key'):
        #   self.directions = ['drop_keys', 'areaid86']

        self.track_runs = 0
        self.character.MONSTER_KILL_LIST = ['skeleton']
        self.character.CAN_FLEE = False

    def stop(self):
        self.character.CAN_FLEE = True
        super().stop()

    def decide_where_to_go(self):
      magentaprint("Deciding where to go", False)
      magentaprint("Area ID: " + str(self.character.AREA_ID), False)
      if (self.character.AREA_ID != 2524 and\
         self.character.AREA_ID != 86) or\
         self.track_runs > 10:
        self.track_runs = 0
        return self.reset[:]

      if self.character.inventory.has('wooden key') and\
         self.track_runs != 0:
        self.track_runs += 1
        return self.skellington_track[:]
      
      self.track_runs += 1
      return self.setup_track[:]

    def do_pre_go_actions(self):
      if self.character.inventory.has_broken("stout cudgel") or self.probably_repair:
        magentaprint("Need to fix my stout cudgel", False)
        # self.command_handler.weapon_bot.smithy_bot.go_repair("stout cudgel")        
        # self.command_handler.process('wield cudgel')
        self.directions = self.reset[:]

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
        self.sleep(0.2)
        self.command_handler.process("i")
        self.sleep(0.2)
        return True
      elif exit_str == "asis_light":
        self.command_handler.process("ask guide light")
        self.sleep(5)
      elif exit_str == "buff":
        self.do_buff_skills()
        return True
      elif exit_str == "unlock_east":
        self.command_handler.process("unlock east wood")
        self.sleep(0.2)
        self.command_handler.process("open east")
        self.sleep(0.2)
        return True
      elif exit_str == "engage_skelington":
        self.engage_monster('skeleton')
        return True
      elif exit_str == "drop_keys":
        for _ in range(self.count_keys()):
          self.command_handler.process("drop key yes")
          time.sleep(0.1)
        self.command_handler.process("i")
        time.sleep(0.2)
        return True
      else:
        return super().do_go_hooks(exit_str)

    def count_keys(self):
      return sum(self.character.inventory.count(r) for r in self.keys)

    def update_aura(self):
      return True