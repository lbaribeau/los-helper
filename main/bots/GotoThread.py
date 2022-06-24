
from bots.BotThread import *
from misc_functions import *
from db.MudMap import *

class GotoThread(BotThread):
    def __init__(self, character, command_handler, mudReaderHandler, mud_map, area_to_id=None, is_show_to=False):
        super().__init__(character, command_handler, mudReaderHandler, mud_map)

        if isinstance(area_to_id, int):
            self.area_to_id = area_to_id
            self.is_show_to = is_show_to
        else:
            magentaprint("No Area ID supplied to goto", False)

    def decide_where_to_go(self):
        directions = []
        area_ids = []
        magentaprint(str(self.character.AREA_ID) + " to " + str(self.area_to_id), False)

        try:
            if self.area_to_id == -1:
                directions = self.mud_map.get_nearest_unexplored_path(self.character.AREA_ID)
            else:
                directions = self.mud_map.get_path(self.character.AREA_ID, self.area_to_id, True)
            # Hmmm... get_path returning none...
        except Exception as e:
            # magentaprint("I/O error({0}): {1}".format(e.errno, e.strerror))
            magentaprint("GotoThread caught exception: " + str(e))
            self.stop()
            # raise e  # Not sure which exceptions we want to survive...

        if "amethyst" in directions:
            magentaprint(directions, False)
            magentaprint("Path goes through limbo!")
            return []  # This will break the bot if the db gives a path through limbo

        if self.is_show_to:
            showto_path = []
            # i = 0
            # while i < len(area_ids):
            #     showto_path.append("{} <{}>".format(directions[i], area_ids[i]))
            #     i += 1
            magentaprint(directions, False)
            magentaprint(showto_path, False)
            directions = []
            self.stop()

        return directions

    def do_after_directions_travelled(self):
        self.stop()