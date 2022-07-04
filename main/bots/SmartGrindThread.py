
import random, math, sys

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

    def __init__(self, character, command_handler, mudReaderHandler, mud_map): 
        super().__init__(character, command_handler, mudReaderHandler, mud_map)

        self.is_actually_dumb = True

        self.cur_target = None
        self.cur_area_id = self.character.AREA_ID
        self.on_heal_path = False

        self.track_start_time = 0
        self.track_end_time = 0

        # if self.character.AREA_ID != 2:
        #     self.direction_list = self.get_heal_path()

        low_level_modifier = -1
        high_level_modifier = 0# + 1 #risky business
        if self.is_character_class('Mon'):
            low_level_modifier = -2 # kill everything in sight

        if self.is_character_class('Mag') or self.is_character_class('Dru') or self.is_character_class('Alc') or self.is_character_class('Cle'):
            self.character.MANA_TO_ENGAGE = self.character.info.maxMP / 2
            if self.character.MANA_TO_ENGAGE < 21 and self.character.info.maxMP > 21:
                self.character.MANA_TO_ENGAGE = 21

        self.low_level = int(math.floor(self.character.level / 2)) + low_level_modifier
        self.high_level = max([int(math.ceil(self.character.level / 2)), self.character.level - 3]) + high_level_modifier

        self.min_target_aura = Aura('demonic red')
        self.max_target_aura = Aura('heavenly blue')

        if self.is_character_class('Cle'):
            self.KOBOLD_PATH = [
                'areaid1679','areaid2'
                ]

    def do_pre_go_actions(self):
        # super().do_pre_go_actions()
        if self.track_start_time != 0:
            self.track_end_time = get_timeint()
            self.character.TRACK_TIME += (self.track_end_time - self.track_start_time).total_seconds()

        rest_start = get_timeint()
        if self.aura_changed():
            self.aura_updated_hook()
        
        if self.in_chapel() and not self.ready_for_combat(): #in healing area
            self.rest_and_check_aura()
        rest_end = get_timeint()
        self.character.REST_TIME += (rest_end - rest_start).total_seconds()
        self.track_start_time = get_timeint()

        self.check_weapons()
        self.check_armour()

        if self.has_buff_ability():
            if self.use_buff_ability():
                self.use_extra_buff_items()
        else:
            pass

        # self.inventory.get_inventory()
        # # self.inventory.get_equipment(self.character.name)

        # self.check_weapons()
        # self.check_armour()

        if len(self.character.MONSTER_KILL_LIST) == 0:
            self.get_targets()

    def do_reboot_hooks(self):
        if self.character.is_sleepy == False:
            magentaprint("Here I go rebooting again!", False)
            self.direction_list = ['areaid2', 'shutdown']
            self.character.is_sleepy = True

    def do_go_hooks(self, exit_str):
        if self.go_rest_if_not_ready() and not self.on_heal_path:
            magentaprint("going to rest and not on heal path", False)
            magentaprint(self.direction_list, False)
            return True

        if exit_str == "shutdown" and self.character.is_sleeping == False:
            self.stop()
            self.character.is_sleeping = True
            self.character.is_sleepy = False
            raise Reboot
            # self.command_handler.process('') #move cursor forward
            # sys.stdout.write('')
            return True
        else:
            return super().do_go_hooks(exit_str)

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
        # magentaprint("SmartGrindThread.get_heal_path() from_path is " + str(from_path) + ", character.AREA_ID is " + str(self.character.AREA_ID) + ".", False)
        if self.is_actually_dumb and self.character.AREA_ID != 2:
            return ["areaid2"]
        elif self.character.AREA_ID == 2:
            return []
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
        magentaprint("SmartGrind getting targets - parameters - {} {} {}/{} {}/{}".format(\
            self.low_level, self.high_level, self.min_target_aura.index(), self.min_target_aura, self.max_target_aura, self.max_target_aura.index()), False)

        target_list = MudMob.get_mobs_by_level_and_aura_ranges(
            self.low_level, 
            self.high_level, 
            self.min_target_aura.index(), 
            self.max_target_aura.index()
        )

        # if not target_list:

        self.character.MONSTER_KILL_LIST = []

        # magentaprint(target_list.count(), False)
        # magentaprint(target_list, False)

        for target in target_list:
            mob_locations = MudMap.get_mob_locations_by_id(target.id)
            self.character.MONSTER_KILL_LIST.append(target.name) # This might append too many?
            self.smart_target_list.append(SmartGrindTarget(target, mob_locations))

        if self.character.is_headless:
            output_api_feed('mkl', self.character.MONSTER_KILL_LIST)

    def reset_kill_list(self):
        self.get_targets()

    def pick_new_target(self):
        next_target = self.cur_target

        while next_target == self.cur_target:
            next_target = random.choice(self.smart_target_list)

        self.cur_target = next_target
        magentaprint("Picking new target: " + next_target.to_string(), True)

    def aura_updated_hook(self):
        # self.low_level = int(math.ceil(self.character.level / 2)) - 2
        magentaprint("Current Aura Scale: " + str(Aura.auras))
        magentaprint("Preferred Aura Scale: " + str(self.character.preferred_aura))
        aura_context = "fine"

        if self.character.AURA < self.character.preferred_aura:
            # Too evil
            # self.low_level = 2
            self.min_target_aura = Aura('demonic red')
            self.max_target_aura = Aura('grey')
            aura_context = "too evil"
        elif self.character.AURA > self.character.preferred_aura:
            # Too good
            # self.low_level = 2
            self.min_target_aura = Aura('grey')
            self.max_target_aura = Aura('heavenly blue')
            aura_context = "way too good"
        else:
            self.min_target_aura = Aura('demonic red')
            self.max_target_aura = Aura('heavenly blue')

        magentaprint("My aura is {}".format(aura_context), False)

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
        self.command_handler.user_flee()
        #we should have a new area id now
        self.direction_list = self.get_heal_path(self.character.AREA_ID)

    def do_on_go_no_exit(self):
        if self.no_exit_count > 10:
            magentaprint("Walking back to the chapel")
            self.direction_list = self.get_heal_path(self.character.AREA_ID)
            self.no_exit_count = 0
            self.command_handler.process("l")
        else:
            #magentaprint("Go no exit on: " + self.direction_list.pop(0), False)
            self.character.MOBS_JOINED_IN = []
            self.character.MOBS_ATTACKING = []

    def do_after_directions_travelled(self):
        self.go_rest_if_not_ready()

    def go_rest_if_not_ready(self):
        if not self.ready_for_combat():
            self.direction_list = self.get_heal_path()
            self.on_heal_path = True

            if len(self.direction_list) == 0:
                self.on_heal_path = False

            return True
        return False

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