
from bots.GrindThread import GrindThread
from misc_functions import *

class CampGrindThread(GrindThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None):
      super().__init__(character, command_handler, mud_reader_handler, mud_map)

    def stop(self):
      super().stop()

    def decide_where_to_go(self):
      return ['rest']

    def update_aura(self):
      return True

    def do_go_hooks(self, exit_str):
      if exit_str == "rest":
        self.sleep(60)
        self.command_handler.process("rest")
        return True