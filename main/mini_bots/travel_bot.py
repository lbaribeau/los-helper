
from bots.GotoThread import GotoThread
from mini_bots.mini_bot import MiniBot

class TravelBot(MiniBot):
    # Should make use of goto thread

    def __init__(self, char=None, command_handler=None, map=None):
        self.char = char
        self.command_handler = command_handler
        self.map = map

    def go_to_area_by_id(self, id):
        GotoThread()

    def go_to_area_by_title(self, title_fragment):
        pass

    def get_directions(self, map, orig_aid, dest_aid):
        


