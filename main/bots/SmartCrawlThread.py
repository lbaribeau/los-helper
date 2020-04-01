
from bots.CrawlThread import CrawlThread
from misc_functions import *
from db.MudArea import *

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
    def get_heal_path(self, from_path=-1):
        directions = []

        try:
            if from_path == -1:
                directions = self.mud_map.get_path(self.cur_area_id, 2)
            else:
                directions = self.mud_map.get_path(from_path, 2)
        except Exception:
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            self.rest_and_check_aura()

        return directions

    def do_on_blocking_mob(self):
        #mark destination as blocked
        MudArea.set_area_exit_as_unusable("Blocking mob: " + self.character.GO_BLOCKING_MOB, self.character.AREA_ID, self.character.LAST_DIRECTION)
        #try next area - if that doesn't work then eat bugs
        #engage monster + die and go to ame
        self.engage_monster(self.character.GO_BLOCKING_MOB)
        self.character.GO_BLOCKING_MOB = ""
        self.engage_mobs_who_joined_in()
        self.engage_any_attacking_mobs()

    def engage_monster(self, monster):
        self.kill.wait_until_ready()

        if self.stopping:
            return

        new_target = self.character.mobs.list.get_first_reference(monster)

        if new_target:
            self.smartCombat.target = new_target
        else:
            # ie. dark room
            if len(monster.split(' ')) > 1:
                self.smartCombat.target = str(monster).split(' ')[0]
            else:
                self.smartCombat.target = str(monster)

        self.smartCombat.run()