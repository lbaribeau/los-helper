from misc_functions import *
from BotThread import *
from Database import *
from MudMap import *

class CrawlThread(BotThread):
    def __init__(self, character_in=None, commandHandler=None, mudReaderHandler_in=None,
                inventory_in=None, database=None, mud_map=None):
        super(CrawlThread, self).__init__(character_in, commandHandler, mudReaderHandler_in, inventory_in, database, mud_map)

    def decide_where_to_go(self):
        if (not self.character.CAN_SEE):
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
        #find a null exit
        for area_exit in area_exit_list:
            if (area_exit.area_to is None and area_exit.is_useable):
                return [area_exit.exit_type.name]

        #if we didn't find a null exit we end up here and the magic starts
        self.mud_map = MudMap() #if we actively update the map in Cartography then we wouldn't have to re-create it here

        return self.mud_map.get_nearest_unexplored_path(self.character.AREA_ID)
