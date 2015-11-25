import random

from misc_functions import *
from bots.BotThread import *
from db.Database import *
from db.MudMap import *

class CrawlThread(BotThread):
    def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
                mud_map=None):
        super().__init__(character, command_handler, mud_reader_handler, mud_map)
        self.character.ACTIVELY_MAPPING = True

    def stop(self):
        super(CrawlThread, self).stop()
        self.character.ACTIVELY_MAPPING = False

    def decide_where_to_go(self):
        if not self.character.CAN_SEE:
            magentaprint("I'm bliiiiiinnddddd!!!", False)
            self.commandHandler.process("c light")
            time.sleep(2)
            self.commandHandler.process("l")
        elif self.character.DEAD:
            time.sleep(12) #wait in Limbo
            self.character.DEAD = False
        
        time.sleep(0.5)
        curArea = Area.get_area_by_id(self.character.AREA_ID)
        curAreaExits = AreaExit.get_area_exits_from_area(curArea)
        chosen_exit = self.pick_exit(curAreaExits)
        directions = chosen_exit

        return directions

    def pick_exit(self, area_exit_list):
        exit = None
        exits = []

        self.mud_map = MudMap()

        #find a null exit
        for area_exit in area_exit_list:
            if (area_exit.area_to is None and area_exit.is_useable):
                exit = [area_exit.exit_type.name]
                break
            exits.append(area_exit.exit_type.name)

        if exit is None:
            #if we didn't find a null exit we end up here and the magic starts
            #self.mud_map = MudMap() #if we actively update the map in Cartography then we wouldn't have to re-create it here

            while (not self.mud_map.ready):
                time.sleep(1)

            try:
                exit = self.mud_map.get_nearest_unexplored_path(self.character.AREA_ID)
            except Exception:
                #If for some reason we don't know how to find the nearest unexplored path let's just pick a random exit and try again
                exit = [random.choice(exits)]


        return exit
