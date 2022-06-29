
from bots.BotThread import *
from misc_functions import *
from db.MudMap import *

class GotoThread(BotThread):
    def __init__(self, character, commandHandler, mudReaderHandler, mud_map, area_to_id=None, is_show_to=False):
        super().__init__(character, commandHandler, mudReaderHandler, mud_map)

        if isinstance(area_to_id, int):
            self.area_to_id = area_to_id
            self.is_show_to = is_show_to
        else:
            magentaprint("No Area ID supplied to goto", False)

    def decide_where_to_go(self):
        directions = []
        magentaprint(str(self.character.AREA_ID) + " to " + str(self.area_to_id), False)

        try:
            directions = self.mud_map.get_path(self.character.AREA_ID, self.area_to_id)
            # Hmmm... get_path returning none...
        except Exception as e:
            # magentaprint("I/O error({0}): {1}".format(e.errno, e.strerror))
            magentaprint("GotoThread caught exception: " + str(e))
            self.stop()
            raise e  # Not sure which exceptions we want to survive...

        if "amethyst" in directions:
            magentaprint(directions, False)
            magentaprint("Path goes through limbo!")
            return []  # This will break the bot if the db gives a path through limbo

        if self.is_show_to:
            magentaprint(directions, False)
            directions = []
            self.stop()

        return directions

    def do_after_directions_travelled(self):
        self.stop()