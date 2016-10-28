
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

class EquipmentBot(Thread):
    def __init__(self, char, command_handler, mrh, map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        self.mrh = mrh
        self.map = map
        self.smartCombat = command_handler.smartCombat
        self.kill = command_handler.smartCombat.kill
        self.cast = command_handler.smartCombat.cast
        self.stopping = False

    def stop(self):
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

