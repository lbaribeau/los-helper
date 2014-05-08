from GrindThread import *
from misc_functions import *
from Inventory import *
from Exceptions import *
from SmartGrindTarget import *
import random


class SmartGrindThread(GrindThread):

    def __init__(self, character, commandHandler, mudReaderHandler,
                inventory, database, mud_map, starting_path=None): 
        super(SmartGrindThread, self).__init__(character, commandHandler, mudReaderHandler, inventory, database, mud_map)
        target_list = ["theatre goer", "actor", "militia solider", "rancher sentry", "sawmill operator",
        "dwarven fieldworker", "market official", "fort sentry", "large bandit", "kobold sentry", "old kobold",
        "bandit swordsman", "gnoll sentry", "sword swallower"]

        self.smart_target_list = []

        for target in self.target_list:
            mob_locations = MudMap.get_mob_locations_by_name(self.cur_target)
            self.smart_target_list.append(SmartGrindTarget(target, mob_locations))

        self.cur_target = ""
        self.cur_area_id = self.character.AREA_ID

    def decide_where_to_go(self):
        self.cur_area_id = self.character.AREA_ID
        directions = []

        #get pawnshop path then tip path if necessary.
        self.inventory.get_inventory()
        if len(self.inventory.sellable()) > self.loot_threshold:
            directions = self.get_vendor_paths()
        elif(self.ready_for_combat()):
            directions = self.get_grind_path()
        else:
            directions = self.get_heal_path()

        return directions

    def get_grind_path(self):
        directions = []

        self.pick_new_target()
        paths_to_target = get_all_paths_to_target()

        i = 0

        while i < (len(paths_to_target) / 2):
            closest_path = get_shortest_array(paths_to_target)
            i = i + 1

        return directions

    def get_all_paths_to_target(from_path=-1):
        paths = []

        for area_id in self.cur_target.locations:
            if from_path == -1:
                paths.append(self.mud_map.get_path(self.cur_area_id, area_id))
            else:
                paths.append(self.mud_map.get_path(from_path, area_id))

        return paths

    def pick_directions_from_list(self, direction_list):
        directions = []

        last_area_id = self.cur_area_id

        i = 0

        for area_id in direction_list:
            if i < 10:
                try:
                    directions.extend(self.mud_map.get_path(last_area_id, area_id))
                    last_area_id = area_id
                    i = i + 1
                except Exception:
                    #we should maybe mark the direction set as unpathable but...
                    #it could just be a glitch on this particular location we're in
                    continue

        return directions

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

    def get_vendor_paths(self):
        directions = []

        directions.extend(self.get_pawnshop_path())
        directions.extend(self.get_tip_path(336))

        return directions

    def get_pawnshop_path(self):
        directions = []

        try:
            directions = self.mud_map.get_path(self.cur_area_id, 336)
            directions.append("sell_items")
        except Exception:
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            self.get_heal_path()

        return directions

    def get_tip_path(self, from_path=-1):
        directions = []

        try:
            if from_path == -1:
                directions = self.mud_map.get_path(self.cur_area_id, 160)
            else:
                directions = self.mud_map.get_path(from_path, 160)
            directions.append("drop_items")
        except Exception:
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            self.get_heal_path()

        return directions

    def pick_new_target(self):
        next_target = self.cur_target

        while next_target == self.cur_target:
            next_target = random.choice(self.smart_target_list)

        self.cur_target = next_target
        magentaprint("Picking new target: " + next_target, False)

    def do_rest_hooks(self):
        #this sets us on a path towards the chapel if possible - if not this will return an empty 
        #array that causes the bot to sit and wait to heal
        self.direction_list = self.get_heal_path(self.character.AREA_ID)

    def do_flee_hook(self):
        unsafe_area = self.character.AREA_ID
        self.commandHandler.user_flee()
        #we should have a new area id now
        self.direction_list = self.get_heal_path(self.character.AREA_ID)