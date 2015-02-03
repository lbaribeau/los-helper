from GrindThread import *
from misc_functions import *
from Inventory import *
from Exceptions import *
from MudMob import *
import random, math

class SmartGrindThread(GrindThread):
    smart_target_list = []


    def __init__(self, character, commandHandler, mudReaderHandler,
                inventory, mud_map, starting_path=0): 
        super(SmartGrindThread, self).__init__(character, commandHandler, mudReaderHandler, inventory, mud_map, starting_path)

        self.is_actually_dumb = False

        self.cur_target = None
        self.cur_area_id = self.character.AREA_ID

        self.low_level = int(self.character.level / 2) - 2
        self.high_level = int(math.ceil(self.character.level / 2))# + 1 #risky business
        
        self.low_aura = 0 #how evil the targets are
        self.high_aura = 16 #how good the targets are
        self.aura_updated_hook()

    def do_pre_go_actions(self):
        self.go_rest_if_not_ready()
        self.check_weapons()
        self.check_armour()
        return

    def check_weapons(self):
            #check if we have a weapon equipped
            #if not then 
            #   check inventory for out favorite type of weapon
            #   if we don't have one lets go buy one and equip it
            #otherwise laugh hysterically

        return

    def purchase_weapon(self):
        return

    def equip_weapon(self):
        return

    def check_armour(self):
        return

    def decide_where_to_go(self):
        if self.is_actually_dumb:
            return super(SmartGrindThread, self).decide_where_to_go()
        else:
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

        #Half assed shortest paths
        for location in self.cur_target.locations:
            directions.append("areaid%s" % location)
            if len(directions) > 10:
                break
            

        magentaprint(directions)

        return directions

    def get_all_paths_to_target(self, from_path=-1):
        paths = []

        for area_id in self.cur_target.locations:
            try:
                if from_path == -1:
                    paths += (self.mud_map.get_path(self.cur_area_id, area_id))
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
                directions = get_shortest_array(self.mud_map.get_paths_to_nearest_restorative_area(self.cur_area_id))
            else:
                directions = get_shortest_array(self.mud_map.get_paths_to_nearest_restorative_area(from_path))
        except Exception as e:
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            magentaprint("Exception getting heal path - resting here...", False)
            magentaprint(e)
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

    def get_targets(self):
        target_list = MudMob.get_mobs_by_level_and_aura_ranges(self.low_level, self.high_level, self.low_aura, self.high_aura)

        self.character.MONSTER_KILL_LIST = []

        for target in target_list:
            self.character.MONSTER_KILL_LIST.append(target.name)
            mob_locations = MudMap.get_mob_locations_by_id(target.id)
            self.smart_target_list.append(SmartGrindTarget(target, mob_locations))

    def pick_new_target(self):
        next_target = self.cur_target

        while next_target == self.cur_target:
            next_target = random.choice(self.smart_target_list)

        self.cur_target = next_target
        magentaprint("Picking new target: " + next_target.to_string())

    def aura_updated_hook(self):
        self.low_aura = 0
        self.high_aura = 15

        magentaprint("Current Aura Scale: " + str(self.character.AURA_SCALE))
        magentaprint("Preferred Aura Scale: " + str(self.character.AURA_PREFERRED_SCALE))

        #if character is too evil
        if self.character.AURA_SCALE < self.character.AURA_PREFERRED_SCALE:
            self.low_aura = 0
            self.high_aura = 7
        #if character is too good
        elif self.character.AURA_SCALE > self.character.AURA_PREFERRED_SCALE:
            self.low_aura = 7
            self.high_aura = 15

        self.get_targets()


    def do_rest_hooks(self):
        #this sets us on a path towards the chapel if possible - if not this will return an empty 
        #array that causes the bot to sit and wait to heal
        self.direction_list = self.get_heal_path(self.character.AREA_ID)

    def do_flee_hook(self):
        unsafe_area = self.character.AREA_ID
        self.commandHandler.user_flee()
        #we should have a new area id now
        self.direction_list = self.get_heal_path(self.character.AREA_ID)

    def do_on_go_no_exit(self):
        if (self.no_exit_count > 10):
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
        if not (self.ready_for_combat()):
            directions = self.get_heal_path()
            
            if (len(directions) == 0):
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