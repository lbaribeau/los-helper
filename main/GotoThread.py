from BotThread import *
from misc_functions import *
from MudMap import *

class GotoThread(BotThread):
    def __init__(self, character_in=None, commandHandler=None, mudReaderHandler_in=None,
                inventory_in=None, mud_map=None, area_to_id=None, is_show_to=False):
        super(GotoThread, self).__init__(character_in, commandHandler, mudReaderHandler_in, inventory_in, mud_map)

        if(isinstance(area_to_id, int)):
            self.area_to_id = area_to_id
            self.is_show_to = is_show_to
        else:
            magentaprint("No Area ID supplied to goto", False)

    def decide_where_to_go(self):
        try:
            directions = self.mud_map.get_path(self.character.AREA_ID, self.area_to_id)

            if (self.is_show_to):
                magentaprint(directions, False)
                directions = []
            return directions
        except Exception:
            magentaprint("Unable to build a path to that destination", False)
            self.stop()

    def do_after_directions_travelled(self):
        self.stop()