
import time
import re
import threading
from threading import Thread
import atexit

from misc_functions import *
from Exceptions import *
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
from mini_bots.travel_bot import TravelBot
from mini_bots.mini_bot import MiniBot

# class SmithyBot(Thread):
class SmithyBot(MiniBot):
    def __init__(self, char, command_handler, mud_map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler  # We should create a "BasicCommandHandler" to eliminate this circular dependence
        # (CommandHandler makes bots who need to use CommandHandler - instead they can use BasicCommandHandler which can't make bots)
        self.map = mud_map
        self.smartCombat = command_handler.smartCombat
        self.kill = command_handler.smartCombat.kill
        self.cast = command_handler.smartCombat.cast
        self.equipment = command_handler.equipment
        # self.equipment = Equipment()
        self.slot_names = [
            'body','arms','legs','neck','neck2','face','hands','feet','finger','finger2','finger3',
            'finger4','finger5','finger6','finger7','shield','wielded','seconded','holding']
        self.equipment = dict.fromkeys(self.slot_names)
        self.travel_bot = TravelBot(self.char, self.command_handler, mud_map)

    def stop(self):
        super().stop()  # Unnecessary since travel_bot is the only loop
        self.travel_bot.stop()

    def run(self):
        # Parent implements start_thread() which makes a thread for this.
        self.go_to_nearest_smithy()

    # def is_alive(self):
    #     if self.travel_bot:
    #         return self.
    #     return True

    def go_to_nearest_smithy(self, grinding=False):
        self.stopping = False
        magentaprint("SmithyBot.go_to_nearest_smithy()")
        smithy_path = self.get_smithy_path()
        magentaprint("SmithyBot.get_smithy_path(): " + str(smithy_path))
        self.travel_bot.follow_path(smithy_path)

    def get_smithy_path(self):
        try:
            paths = self.map.get_smithy_paths(self.char.AREA_ID)
        except Exception as e:
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            magentaprint("Exception getting smithy path.")
            magentaprint(e, False)
            raise e

        if paths:
            return get_shortest_array(paths)
        else:
            magentaprint("SmartGrindThread.get_smithy_path() error... no exception but no path returned... make sure the DB is accessible.")
            self.rest_and_check_aura()
            return []

    def execute_equipment_command(self):
        # This is unused.  I think the tricky regex approach ended up being similar in difficulty due to dependencies (mud_map on the eq bot)
        # Making a thread to do this adds flexibility.
        # An alternative method creates a circular dependence - making the Eq command smart enough to keep track of the mud string.
        self.mrh.start_recording()
        self.equipment.execute()
        self.equipment.wait_for_flag()
        self = recorded_equipment = self.mrh.stop_recording()

    def go_repair(self, item_name):
        if self.go_to_nearest_smithy() and not self.stopping:
            self.repair_until_success_or_none_left(item_name)
        else:
            raise Exception("SmithyBot travel error.")

    def repair_until_success_or_none_left(self, item_name):
        # Example: If you have two broken maul hammers, and the first repair fails,
        # this will continue on and try to repair the second.
        return self.repair_until_success_or_none_left_by_ref(self.char.inventory.get_first_reference(item_name))

    def repair_until_success_or_none_left_by_ref(self, first_reference_of_item):
        item_name = self.char.inventory.get_item_name_from_reference(first_reference_of_item)
        magentaprint("SmithyBot.repair_until_success_or_none_left_by_ref() ref/item name: " + str(first_reference_of_item) + '/' + str(item_name))
        self.command_handler.repair.wait_until_ready(first_reference_of_item)
        self.command_handler.repair.execute_and_wait(first_reference_of_item)

        if self.command_handler.repair.success:
            self.char.inventory.set_usable(self.char.inventory.get_last_reference(item_name))
            return True
        elif self.command_handler.repair.failure:
            self.char.inventory.remove_by_ref(first_reference_of_item)
            if self.char.inventory.has(item_name):
                self.repair_until_success_or_none_left_by_ref(first_reference_of_item)  # Recursion!
            else:
                return False
        else:
            self.repair_until_success_or_none_left_by_ref(first_reference_of_item)  # Recursion!

    def repair_one(self, name):
        ref = self.char.inventory.get_last_reference(name)
        self.command_handler.repair.execute_and_wait(ref)
        if self.command_handler.repair.success:
            self.char.inventory.set_usable(ref)
            return True
        else:
            self.char.inventory.remove_by_ref(ref)
            return False

        # weapon_ref = self.char.inventory.get_first_reference(w)
        # weapon_ref = self.char.inventory.get_last_reference(w)
        # while self.char.inventory.name_from_ref(weapon_ref) == w:

        # This version is rough because client side inventory doesn't swap items around on repair, so we should always repair the
        # last
        # self.command_handler.repair.execute_and_wait(ref)
        # if self.command_handler.repair.success:
        #     self.char.inventory.set_usable(self.char.inventory.get_last_reference(self.char.inventory.get(ref).item.name))
        #     return True
        # else:
        #     self.char.inventory.remove_by_ref(self.char.inventory.get_last_reference(self.char.inventory.get(ref).item.name))
        #     return False

            # if self.command_handler.repair.success:
            #     self.rewield(weapon_ref)
            #     return True
            # elif self.command_handler.repair.result == R.no_gold:
            #     raise Exception("No gold!")
            # else:
            #     weapon_ref = MobTargetDeterminator().increment_ref(weapon_ref)


