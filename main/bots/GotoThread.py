
from bots.BotThread import *
from misc_functions import *
from db.MudMap import *
from collections import deque

class GotoThread(BotThread):
    def __init__(self, character, commandHandler, mudReaderHandler, mud_map, area_to_id=None, is_show_to=False):
        super().__init__(character, commandHandler, mudReaderHandler, mud_map)

        if isinstance(area_to_id, int):
            self.area_to_id = area_to_id
            self.is_show_to = is_show_to
        else:
            magentaprint("No Area ID supplied to goto", False)

    def decide_where_to_go(self):
        # directions = []
        directions = deque()
        magentaprint(str(self.character.AREA_ID) + " to " + str(self.area_to_id), False)

        try:
            # directions = self.mud_map.get_path(self.character.AREA_ID, self.area_to_id)
            directions.extendleft(reversed(self.mud_map.get_path(self.character.AREA_ID, self.area_to_id)))
            # Hmmm... get_path returning none...
        except Exception as e:
            # magentaprint("I/O error({0}): {1}".format(e.errno, e.strerror))
            magentaprint("GotoThread caught exception: " + str(e))
            self.stop()
            raise e  # Not sure which exceptions we want to survive...

        for i in range(len(directions)):
            exit_split = directions[i].split(' ')
            if len(exit_split) > 1:
                try:
                    int(exit_split[1])
                except ValueError:
                    directions[i]=exit_split[0]
                # The idea here is, to convert "mine shaft" to "mine", just because "go mine shaft" isn't right
                # (I had code that expected an integer... Cartography string match exit name)
                # But keep "cave 3", since the 2nd part is needed...
                # Hopefully 1st word approach is ok, doesn't have ambiguity... 2 words would never work anyway though so, wouldn't be a regression error

        if "amethyst" in directions:
            magentaprint(directions, False)
            magentaprint("Path goes through limbo!")
            # return []  # This will break the bot if the db gives a path through limbo
            return deque()  # This will break the bot if the db gives a path through limbo

        if self.is_show_to:
            magentaprint(directions, False)
            # directions = []
            directions = deque() 
            self.stop()

        return directions

    def do_after_directions_travelled(self):
        self.stop()