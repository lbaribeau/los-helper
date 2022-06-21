
import random, math

from bots.TrackGrindThread import TrackGrindThread
from misc_functions import *
from command.Inventory import *
from Exceptions import *
from db.MudMob import *
from Aura import Aura

class SmartGrindThread(TrackGrindThread):
    smart_target_list = []
    # chapel_aid = 2
    # pawnshop_aid = 130
    # tip_aid = 266

    def __init__(self, character, commandHandler, mudReaderHandler, mud_map): 
        super().__init__(character, commandHandler, mudReaderHandler, mud_map)

        self.is_actually_dumb = True

        self.cur_target = None
        self.cur_area_id = self.character.AREA_ID

        self.low_level = min(int(math.ceil(self.character.level / 2)) - 2, 1)
        self.high_level = int(math.ceil(self.character.level / 2))# + 1 #risky business

        self.min_target_aura = Aura('demonic red')
        self.max_target_aura = Aura('heavenly blue')

        self.update_aura()
        self.aura_updated_hook()

    def do_pre_go_actions(self):
        self.go_rest_if_not_ready()

        self.inventory.get_inventory()
        # self.inventory.get_equipment(self.character.name)

        self.check_weapons()
        self.check_armour()

        if len(self.character.MONSTER_KILL_LIST) == 0:
            self.get_targets()

    def do_on_successful_go(self):
        super().do_on_successful_go()
        # self.cartography

    def go_purchase_item_by_type(self, model, data, level):  # parent
        self.character.MONSTER_KILL_LIST = []
        super().go_purchase_item_by_type(model, data, level)

    def buy_and_wield(self, exit_str):
        self.direction_list = [""]
        return super().buy_and_wield(exit_str)

    def decide_where_to_go(self):
        magentaprint("SmartGrindThread.decide_where_to_go()")
        self.cur_area_id = self.character.AREA_ID

        if self.is_actually_dumb:
            if self.cur_area_id != 2:
                self.direction_list = ["areaid2"]

            return super().decide_where_to_go()
        else:
            directions = []

            #get pawnshop path then tip path if necessary.
            # self.inventory.get_inventory()
            sellable = self.inventory.sellable()

            # magentaprint("Items in sellable: " + str(sellable), False)
            if len(sellable) > self.loot_threshold:
                # magentaprint("Selling", False)
                directions = self.get_vendor_paths()
            elif self.ready_for_combat():
                directions = self.get_grind_path()
            else:
                magentaprint("SmartGrindThread.decide_where_to_go() not ready for combat.")
                directions = self.get_heal_path()

            return directions

    def get_grind_path(self):
        directions = []

        self.pick_new_target()

        #Half assed shortest paths
        for location in self.cur_target.locations:
            directions.append("areaid%s" % location)
            if len(directions) > 10:
                break

        magentaprint("SmartGrind directions: " + str(directions))

        return directions

    def get_all_paths_to_target(self, from_path=-1):
        paths = []

        for area_id in self.cur_target.locations:
            try:
                if from_path == -1:
                    paths += (self.mud_map.get_path(self.character.AREA_ID, area_id))
                else:
                    paths += (self.mud_map.get_path(from_path, area_id))
            except Exception:
                magentaprint("Area ID: {" + str(area_id) + "} cannot be pathed to!")
                self.cur_target.locations.remove(area_id)

        return paths

    def pick_directions_from_list(self, direction_list):
        directions = []

        last_area_id = self.cur_area_id

        i = 0

        for area_id in direction_list:
            if i < 5:
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
        magentaprint("SmartGrindThread.get_heal_path() from_path is " + str(from_path) + ", character.AREA_ID is " + str(self.character.AREA_ID) + ".")
        if self.is_actually_dumb:
            return ["areaid2"]
        else:
            try:
                if from_path == -1:
                    paths = self.mud_map.get_paths_to_nearest_restorative_area(self.character.AREA_ID)
                else:
                    paths = self.mud_map.get_paths_to_nearest_restorative_area(from_path)
            except Exception as e:
                #not a good situation - we can't find a way to the chapel from wherever we are
                #therefore we should just sit and wait here until we can go on the warpath again
                magentaprint("Exception getting heal path.")
                magentaprint(e, False)
                raise e

            if not paths:
                magentaprint("SmartGrindThread.get_heal_path() error... no exception but no path returned... make sure the DB is accessible.")
                self.rest_and_check_aura()
                return []
            else:
                return get_shortest_array(paths)

    def get_vendor_paths(self):
        directions = []

        directions.extend(self.get_pawnshop_path())
        directions.extend(self.get_tip_path(130))

        return directions

    def get_pawnshop_path(self):
        directions = []

        try:
            directions = self.mud_map.get_path(self.character.AREA_ID, 130)
            directions.append("sell_items")
        except Exception as e:
            magentaprint("SmartGrind.get_pawnshop_path() exception.")
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            self.get_heal_path()

        return directions

    def get_tip_path(self, from_path=-1):
        directions = []

        try:
            if from_path == -1:
                directions = self.mud_map.get_path(self.character.AREA_ID, 266)
            else:
                directions = self.mud_map.get_path(from_path, 266)
            directions.append("drop_items")
        except Exception:
            magentaprint("SmartGrind.get_tip_path() exception.")
            self.get_heal_path()

        return directions

    def get_targets(self):
        magentaprint("SmartGrind getting targets - parameters - {0} {1} {2} {3}".format(\
            self.low_level, 
            self.high_level, 
            self.min_target_aura, 
            self.max_target_aura
        ))
        target_list = MudMob.get_mobs_by_level_and_aura_ranges(
            self.low_level, 
            self.high_level, 
            self.min_target_aura, 
            self.max_target_aura
        )

        # if not target_list:

        self.character.MONSTER_KILL_LIST = []

        # magentaprint(target_list.count(), False)
        # magentaprint(target_list, False)

        for target in target_list:
            # magentaprint(target, False)
            mob_locations = MudMap.get_mob_locations_by_id(target.id)
            self.character.MONSTER_KILL_LIST.append(target.name) # This might append too many?
            self.smart_target_list.append(SmartGrindTarget(target, mob_locations))

    def reset_kill_list(self):
        self.get_targets()

    def pick_new_target(self):
        next_target = self.cur_target

        while next_target == self.cur_target:
            next_target = random.choice(self.smart_target_list)

        self.cur_target = next_target
        magentaprint("Picking new target: " + next_target.to_string())

    def aura_updated_hook(self):
        # self.low_level = int(math.ceil(self.character.level / 2)) - 2
        # magentaprint("Current Aura Scale: " + str(self.character.AURA_SCALE), False)
        # magentaprint("Preferred Aura Scale: " + str(self.character.AURA_PREFERRED_SCALE), False)

        if self.character.level < 4:
            self.min_target_aura = 0
            self.max_target_aura = len(Aura.auras)
        # elif self.character.AURA_SCALE < self.character.AURA_PREFERRED_SCALE:
        elif self.cast.aura < self.character.preferred_aura:
            # Too evil
            # self.low_level = 2
            self.min_target_aura = 0
            self.max_target_aura = math.floor(len(Aura.auras) / 2)
        elif self.cast.aura > self.character.preferred_aura:
            # Too good
            # self.low_level = 2
            self.min_target_aura = math.ceil(len(Aura.auras) / 2)
            self.max_target_aura = len(Aura.auras) - 1
        else:
            self.min_target_aura = math.floor(len(Aura.auras) / 2)
            self.max_target_aura = math.ceil(len(Aura.auras) / 2)

        self.get_targets()

    def do_rest_hooks(self):
        pass
        # Erhm this is causing me problems.

        #this sets us on a path towards the chapel if possible - if not this will return an empty 
        #array that causes the bot to sit and wait to heal
        # magentaprint("SmartGrindThread.do_rest_hooks()")
        # if not self.is_actually_dumb:
        #     self.direction_list = self.get_heal_path(self.character.AREA_ID)

    def do_flee_hook(self):
        unsafe_area = self.character.AREA_ID
        self.commandHandler.user_flee()
        #we should have a new area id now
        self.direction_list = self.get_heal_path(self.character.AREA_ID)

    def do_on_go_no_exit(self):
        if self.no_exit_count > 10:
            magentaprint("Walking back to the chapel")
            self.direction_list = self.get_heal_path(self.character.AREA_ID)
            self.no_exit_count = 0
        else:
            #magentaprint("Go no exit on: " + self.direction_list.pop(0), False)
            self.character.MOBS_JOINED_IN = []
            self.character.MOBS_ATTACKING = []

    def do_after_directions_travelled(self):
        self.go_rest_if_not_ready()

    def go_rest_if_not_ready(self):
        magentaprint("SmartGrindThread.go_rest_if_not_ready()")
        if not self.ready_for_combat():
            directions = self.get_heal_path()
            
            if len(directions) == 0:
                self.rest_and_check_aura()        

class SmartGrindTarget(object):
    def __init__(self, name, locations):
        self.name = name
        self.locations = locations

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def to_string(self):
        return self.name.to_string() #+ ", " + str(self.locations)