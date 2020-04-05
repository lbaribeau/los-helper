
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

class TopDownGrind(Thread):
    def __init__(self, char, command_handler, mrh, mud_map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        self.mrh = mrh
        self.mud_map = mud_map
        self.smartCombat = command_handler.smartCombat
        self.kill = command_handler.smartCombat.kill
        self.cast = command_handler.smartCombat.cast
        self.stopping = False

        self.actions = {
            # R.you_wield: (lambda self, match : self.weapon = match.group('weapon')),
        }
        self.regex_cart = self.actions.keys()

        self.travel_bot = command_handler.travel_bot
        self.armour_bot = command_handler.armour_bot
        self.weapon_bot = command_handler.weapon_bot
        self.travel_bot = TravelBot(self.char, self.command_handler, mud_map)

    def notify(self, regex, match):
        self.actions[regex](match)

    def stop(self):
        self.stopping = True
        self.armour_bot.stop()
        self.weapon_bot.stop()
        self.travel_bot.stop()

    def run(self):
        self.stopping = False

        while not self.stopping:
            if self.stopping:
                break


            self.task

            self.go_repair_or_replace_weapon()
            self.go_repair_or_replace_armour()
            self.go_sell_and_drop()
            self.go_rest()
            self.combat_buff_up()
            self.go_hunting()
            # We want to do the nearest thing, except sometimes healing to full is not the nearest.
            # Well, not true.  Heal to full when:
            # - no need for weapons or armour or smithies/shops (depending) are farther
            # - no need to sell and drop or it's farther
            # - mob to kill is far (low health narrows mob choice)
            self.rest_distance = self.get_path_to_nearest_rest_location()
            self.smithy_distance = self.get_path_to_nearest_smithy()

    def go_repair_or_replace_weapon(self):
        pass

    def go_repair_or_replace_armour(self):
        pass

    def go_sell_and_drop(self):
        pass

    def go_replace_weapon(self):
        pass

    # def should_rest(self):
    #     pass
