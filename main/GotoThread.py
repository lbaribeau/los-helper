from BotThread import *
from misc_functions import *
from MudMap import *

class GotoThread(BotThread):
    def __init__(self, character, commandHandler, mudReaderHandler, mud_map, area_to_id, is_show_to=False):
        super().__init__(character, commandHandler, mudReaderHandler, mud_map)

        if isinstance(area_to_id, int):
            self.area_to_id = area_to_id
            self.is_show_to = is_show_to
        else:
            magentaprint("No Area ID supplied to goto", False)

    def decide_where_to_go(self):
        directions = self.mud_map.get_path(self.character.AREA_ID, self.area_to_id)

        if self.is_show_to:
            magentaprint(directions, False)
            directions = []

        return directions

    def do_after_directions_travelled(self):
        self.stop()
