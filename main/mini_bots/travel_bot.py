
from bots.GotoThread import GotoThread
from mini_bots.mini_bot import MiniBot

class TravelBot(MiniBot):
    # Should make use of goto thread

    def __init__(self, char, commandHandler, map):
        self.map = map

    def go_to_area_by_id(self, id):
        GotoThread()

    def go_to_area_by_title(self, title_fragment):
        pass


