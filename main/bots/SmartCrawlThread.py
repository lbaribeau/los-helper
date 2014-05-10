from misc_functions import *
from CrawlThread import *

'''
Similar to SmartBotThread this child class is intended to provide better logic for crawling notably:
- combat versus blocking mobs
- looking at mobs to see their rudimentary level
- killing mobs whose exp values have not been determined (if they can be killed with a needle)
- sneaking vs mobs that cannot be attacked
- listing items in shops
- healing when necessary
'''

class SmartCrawlThread(CrawlThread):
    def __init__(self, character_in=None, commandHandler=None, mudReaderHandler_in=None,
                inventory_in=None, mud_map=None):
        super(SmartCrawlThread, self).__init__(character_in, commandHandler, mudReaderHandler_in, inventory_in, mud_map)
    
    def do_pre_go_actions(self):
        if self.character.AREA_ID == 45:
            self.rest_and_check_aura()
        return  

    def do_post_go_actions(self):
        if self.ready_for_combat():
            self.directions = self.get_heal_path()

        return

    def get_heal_path(self, from_path=-1):
        directions = []

        try:
            if from_path == -1:
                directions = self.mud_map.get_path(self.cur_area_id, 45)
            else:
                directions = self.mud_map.get_path(from_path, 45)
        except Exception:
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            self.rest_and_check_aura()

        return directions

    def do_on_blocking_mob(self):
        self.engage_monster(self.character.GO_BLOCKING_MOB)
        self.character.GO_BLOCKING_MOB = ""
        self.engage_mobs_who_joined_in()
        self.engage_any_attacking_mobs()
        self.check_weapons()