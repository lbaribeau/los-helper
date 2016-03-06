
from bots.GotoThread import GotoThread
from mini_bots.mini_bot import MiniBot

class TravelBot(MiniBot):
    # Should make use of goto thread

    def __init__(self, char, command_handler, mud_reader_handler, map):
        self.char = char
        self.command_handler = command_handler
        self.mrh = mud_reader_handler
        self.map = map

    def go_to_area_by_id(self, area_to_id):
        goto = GotoThread(self.char, self.command_handler, self.mrh, self.map, area_to_id)
        goto.run()

    def go_to_area_by_title(self, title_fragment):
        pass

    def get_directions(self, map, orig_aid, dest_aid):
        pass


