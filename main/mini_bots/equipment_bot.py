
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

# class EquipmentBot(Thread):
class EquipmentBot(MiniBot):
    def __init__(self, char, command_handler, mrh, map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler  # We should create a "BasicCommandHandler" to eliminate this circular dependence
        # (CommandHandler makes bots who need to use CommandHandler - instead they can use BasicCommandHandler which can't make bots)
        self.mrh = mrh
        self.map = map
        self.smartCombat = command_handler.smartCombat
        self.kill = command_handler.smartCombat.kill
        self.cast = command_handler.smartCombat.cast
        self.equipment = command_handler.equipment
        # self.equipment = Equipment()
        self.slot_names = [
            'body','arms','legs','neck','neck2','face','hands','feet','finger','finger2','finger3',
            'finger4','finger5','finger6','finger7','shield','wielded','seconded','holding']
        self.equipment = dict.fromkeys(self.slot_names)

    def stop(self):
        super().stop()
        self.travel_bot.stop()

    def go_to_nearest_smithy(self, grinding=False):
        magentaprint("TopDownGrind.go_to_nearest_smithy()")
        smithy_path = self.get_smithy_path()
        magentaprint("TopDownGrind.get_smithy_path(): " + str(smithy_path))
        self.travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.map)
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

