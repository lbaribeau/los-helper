
from bots.GrindThread import GrindThread
from misc_functions import magentaprint
from Aura import Aura
import db.Area
import random

class Path():
    def __init__(self, aura, directions):
        self.aura = aura
        self.directions = directions

class TrackGrindThread(GrindThread):
    def __init__(self, character, command_handler, mudReaderHandler, mud_map, starting_path=None):
        super().__init__(character, command_handler, mudReaderHandler, mud_map)

        # Set TOTALPATHS.  Setting it lower than the actual number
        # of paths in decide_where_to_go is a way to truncate paths
        # you don't want to send low level characters on.

        if self.character.level <= 2:
            self.__TOTALPATHS = 8 # Kobolds are level 1 safe.
        elif self.character.level <= 6:
            self.__TOTALPATHS = 12 # include hookers for level 3
        elif self.character.level <= 7:
            # lvl 7 strong enough for bandits
            self.__TOTALPATHS = 16
        elif self.character.level <= 11:
            self.__TOTALPATHS = 24
        else:
            # self.__TOTALPATHS = 28  # # Area ids unfortunately must be updated.
            #self.__TOTALPATHS = 30
            self.__TOTALPATHS = 52 # Added some graph pathing
        # elif self.character.level <= 10:
        #     self.__TOTALPATHS = 20 # start the fort and bandits at lvl 8
        # elif self.character.level > 12:
        #     self.__TOTALPATHS = 24
        # else:
        #     self.__TOTALPATHS = 22 # start the fort and bandits at lvl 8

        if isinstance(starting_path, int) and starting_path < self.__TOTALPATHS:
            self.__nextpath = starting_path
        else:
            self.__nextpath = random.randrange(0, self.__TOTALPATHS)

        self.LIMBO_TO_CHAPEL = ["ame", "out", "w", "n", "chapel"]

        self.SHOP_AND_TIP_PATH = [
            "out", "south", "west", 'west', 'west', 'south', 'south', "shop",
            "sell_items","out", "southeast", 'east', 'east', 'east', 'east', "northeast", "tip",
            "drop_items","out", 'north', 'north', 'west', 'west', 'west', 'north', "chapel"
        ]
        self.THEATRE_PATH = [
            "out", "s", "w", "w", "w", "s", "theat", "stairs","cubby", "out", "box", "out", "box 2",
            "out", "down", "swing", "seat", "out", "down", "seat", "out", "door", "office", "out",
            "stage","side 2","backstage", "door", "out", "door 2", "out", "curtain", "stage",
            "side", "door","up", "out", "out", "n", "e","e", "e", "n", "chapel"
        ]

        self.MARKET_PATH = ['out',
            's','e','e','e','n','w','w',
            'office','out',
            'n','n','s','w','e','s',
            'w','s','n','w','e','n','s','e',
            'e','out','s', 'w', 'w', 'w', 'n','chapel'
        ]
        self.MILITIA_SOLDIERS_PATH = [
            'out','s','e','s','s','s','w','gate','s','s','sw','sw','sw','sw','s','s','s','sw','southeast','s','s','s','s',
            's','s','s','s','s','w','doo','stor','ou','ou','w','w','w','n','n','s','s','e','e','e','e','n','n','e',
            'e','e','e','e','e','e','e','e','ne','e','ne','ne','ne','ne','ne','ne','n','n','w','s','sw','ne','n','e',
            'n','n','n','n','n','n','n','n','n','n','nw','nw','nw','path','nw','n','n','n','nw','nw','n','n','gate',
            'w','n','nw','nw','n','e','e','e','s','s','s','s','gate','s','s','southeast','southeast','s','s','s','southeast','s','w','w',
            'w','nw','nw','n','gate','e','n','n','n','w','n','chapel'
        ]
        self.KOBOLD_PATH = [
            'out','south','east','south','south','south','west','gate','south','southeast','southeast','east',
            'east','east','southeast','southeast','southeast','south','south','south','south','south','east',
            'east','southeast','east','south','south','south','south','glowing portal','passage','mines',
            'down','n','n','n','n','ne','n','w','n','n','e','door','w','gully','up','boulder','up',
            'cave 3','ne','ne','n','s','up','e','se','cave','out']

        if self.character.level >= 9 and not self.is_character_class('Mag'):
            self.KOBOLD_PATH += ['slow_prepare', 'e', 'ne', 'door',
            # 'statue', 'down', 'down', 'down', 'down', 'hole', 'corridor', 'east', 'east', 'southeast', 'south', 'south'
            # 'south', 'south', 'east', 'cave', 'out', 'west', 'west', 'west', 'west', 'west', 'north', 'north', 'north',
            # 'north', 'north', 'east', 'passage', 'out', 'hole', 'up', 'up', 'up', 'up', 'out',
            'door', 'slow_prepare', 'sw','w']
            # Note: You can remove the following line of code to remove the kobold guards and priests fights.
            # Priests turn you very blue.  These fights may be difficult.
            # Also useful to test mobs who join in.
            # They're commented because kobolds are allowed when you're pale blue, which is one off of blue... and these guards
            # and priests are dangerous unless the bot decides on his own to engage.  Todo: check aura here (if health is
            # high enough,) and go in if all's good.  Even fight the priests - because the more 'good' we can get the
            # more chalices we can farm.
        self.KOBOLD_PATH += [
            'ladder','cave','out','sw','w',
            # 'cave', 'out',  # Comment out insane kobold (TODO: check level here)
            'sw','se','nw','w','out','down','boulder','down','down','e','door','w','s','s','e','s','sw','s','s','s',
            's','gully','glowing portal','passage','coral','north','north','north','north','west','northwest','west','west',
            'north','north','north','north','north','northwest','northwest', 'northwest', 'west', 'west', 'west',
            'northwest','northwest', 'north', 'gate', 'east', 'north', 'north', 'north','west', 'north', 'chapel'
        ]
        self.CORAL_ALLEY_PATH = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','se','se','se','s','s','s','s','w','alley',
            's','s','door','stairs', #angry hooker should be avoided unless lvl 5.
            #'do 3', 'ou',
            'stairs','out','s',
            'w','e', #for zombies
            # noticed drunken troublemakers arrive one east
            # red axer lvl 2 dropped studded leather collarse
            'n','n','n','n','e','n','n','n','n','nw','nw','nw','w','w','w','nw','nw','n','gate','e','n','n','n','w',
            'n','chapel'
        ]
        self.FORT_PATH = [
            'out','n','n', 'w','gate','n','n','n','n','n','gate','n','n','w','s','s','e','e','n',"door", "door",
            'n','w','s','s','gate', 's','s','s','s','s','gate','w','sw','s','s','s','e','e','e','e','n','w','n','chap'
        ]
        self.MUGGER_PATH = [
            'ou','s','w','w','w','s','alley','w','alley','e','e','e','e','e','n','w','n','chap'
        ]
        self.NORTHERN_BANDITS_PATH = [
            'out','n','n','w','gate','n','n','n','n','n','gate','n','n','gate','n','nw','nw','sw','sw','sw','sw','s',
            'sw','sw','w','w','sw','sw','sw','sw','sw','sw','w','w','w','w','nw','w','w','nw','sw','nw','w','w','w',
            'nw','w','w','w','w','south','s','s','n','n','n','e','e','e','e','se','e','e','e','se','ne','se','e','e',
            'se','e','e','e','e','ne','ne','ne','ne','ne','ne','e','e','ne','ne','n','ne','ne','ne','ne','se','se','s',
            'gate','s','w','e','s','gate','s','s','s','s','s','gate','e','s','s','chapel'
        ]
        self.DWARVEN_FIELD_WORKERS_PATH = ['out', 'south', 'east', 'south', 'south',
            'south', 'west', 'gate', 'south', 'southeast', 'southeast',
            'east', 'east', 'east', 'pathway', 'northwest', 'north', 'north',
            'north', 'southeast', 'east', 'east', 'gate', 'east', 'building',
            'out', 'east', 'east', 'southeast', 'field', 'road', 'southeast',
            'southeast', 'southeast', 'field', 'stile', 'stile', 'road',
            'northwest', 'northwest', 'northwest', 'northwest', 'west', 'west',
            'west', 'gate', 'west', 'west', 'northwest', 'south', 'south', 'south',
            'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest',
            'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel'
        ]
        #both gates close at night unforunately...
        self.FIELD_WORKERS_PATH = [
            'out', 'south', 'east', 'south', 'south', 'south','west',
            'gate', 'south', 'southeast', 'southeast', 'east', 'east',
            'east', 'pathway', 'northwest', 'north', 'north', 'north',
            'northwest', 'northwest', 'north', 'north', 'gate', 'west',
            'north', 'northwest', 'northwest', 'north', 'gate', 'west',
            'west', 'southwest', 'southwest', 'west', 'west', 'west',
            'southwest', 'southwest', 'southeast', 'southeast', 'south',
            'gate', 'stile', 'northwest', 'southeast', 'southwest',
            'northeast', 'stile', 'gate', 'north', 'northwest', 'northwest',
            'west', 'west', 'gate', 'south', 'west', 'west', 'west', 'north', 'chapel'
        ]
        #Contains lvl 2&3 mobs (stacker, furniture maker, sawmill operator, mill worker) and lvl 6 mobs (saw)?mill supervisor
        self.MILL_WORKERS = [
            'out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate',
            'south', 'south', 'south', 'south', 'south', 'southwest', 'south',
            'southeast', 'southwest', 'south', 'south', 'southeast', 'south',
            'south', 'southwest', 'bridge', 'south', 'southwest', 'west', 'canal',
            'south', 'south', 'south', 'east', 'east', 'west', 'south', 'east',
            'west', 'north', 'north', 'east', 'south', 'south', 'southwest', 'office', 'out', 'out',
            'west', 'north', 'north', 'north', 'north', 'north', 'northwest',
            'northeast', 'north', 'north', 'north', 'northeast', 'northeast',
            'northeast', 'northeast', 'north', 'north', 'gate', 'east', 'north',
            'north', 'north', 'west', 'north', 'chapel'
        ]
        self.RANCHER_SENTRY = [
            'out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate',
            'south', 'southeast', 'southeast', 'east', 'east', 'east', 'pathway',
            'northwest', 'north','north', 'north', 'northwest', 'northwest', 'north',
            'north', 'gate', 'northeast', 'north', 'northeast', 'north', 'gate',
            'east', 'east', 'east', 'north', 'north', 'northeast', 'north',
            'northeast', 'gate', 'arch', 'north', 'east', 'north', 'northwest',
            'gate', 'north', 'east', 'east', 'south', 'east', 'north', 'south',
            'west', 'west', 'west', 'gate', 'southwest', 'south', 'east', 'south',
            'arch', 'gate', 'southwest', 'south', 'southwest', 'south', 'south', 'west',
            'west', 'west', 'gate', 'south', 'southwest', 'south', 'southwest', 'gate',
            'south', 'south', 'southeast', 'southeast', 'south', 'south', 'south',
            'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest',
            'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel'
        ]
        #aid418, 1975, 1979, 1951, 415, 45

        # These area numbers are unfortunately for a different database... (except "2")

        # need to fix this!
        # self.SPIDER_FOREST = ['out', 'north', 'north', 'west', 'north gate', 'north', 'north', 'north', 'north',
        #  'north', 'gate', 'north', 'north', 'gate', 'north', 'northwest', 'northwest', 'southwest', 'southwest', 
        #  'southwest', 'southwest', 'south', 'southwest', 'southwest', 'west', 'west', 'southwest', 'southwest', 
        #  'southwest', 'southwest', 'southeast', 'southeast', 'southeast', 'southeast', 'southeast', 'south', 
        #  'south', 'forest', 'south', 'southwest', 'southeast', 'northeast', 'north', 'southwest', 'southeast',
        #  'east', 'northeast', 'northwest', 'west', 'southwest', 'southwest', 'northeast', 'east', 'northeast', 
        #  'northwest', 'west', 'northwest', 'north', 'fields', 'north', 'north', 'northwest', 'northwest', 
        #  'northwest', 'northwest', 'northwest', 'northeast', 'northeast', 'northeast', 'northeast', 'east', 
        #  'east', 'northeast', 'northeast', 'north', 'northeast', 'northeast', 'northeast', 'northeast', 
        #  'southeast', 'southeast', 'south', 'gate', 'south', 'south', 'gate', 'south', 'south', 'south', 
        #  'south', 'south', 'gate', 'east', 'south', 'south', 'chapel']

        self.SPIDER_FOREST = ['areaid1886','areaid2355','areaid1886','areaid2355', 'areaid2']

        #The following areas repeat a bit because the spawns are fast
        self.KNIGHTS = [
            'out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'south', 'southwest', 'southwest',
            'southwest', 'southwest', 'south', 'south', 'south', 'southwest', 'southeast', 'south', 'south', 'south',
            'south', 'south', 'east', 'east', 'east', 'southeast', 'south', 'east', 'east', 'east', 'east', 'east',
            'northeast', 'northwest', 'northwest', 'northwest', 'northwest', 'north', 'east', 'east', 'east', 'south',
            'southeast', 'east', 'east', 'northeast', 'north', 'red tent', 'out', 's', 'w', 'w', 'w', 'e', 'e', 'e',
            'sw', 'w', 'w', 'nw', 'n', 'n', 'ne', 'stands', 'stand', 'out', 'stand 2', 'out', #'stand 3', 'out' #Tario
            'e', 'se', 'w', 'w', 'w', 'e', 'e', 'e', 's', 'red tent', 'out', 'south', 'southwest', 'west', 'west',
            'northwest', 'north', 'west', 'west', 'west', 'south', 'southeast', 'southeast', 'southeast', 'southeast',
            'southwest', 'west', 'west', 'west', 'west', 'west', 'north', 'northwest', 'west', 'west', 'west', 'north',
            'north', 'north', 'north', 'north', 'northwest', 'northeast', 'north', 'north', 'north', 'northeast',
            'northeast', 'northeast', 'northeast', 'north', 'north', 'gate', 'east', 'north', 'north', 'north',
            'west', 'north', 'chapel'
        ]

        self.GNOLL_CAMP = ['think']

        # self.GNOLL_CAMP = ['out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'southeast',
        #  'southeast', 'east', 'east', 'east', 'southeast', 'southeast', 'southeast', 'south', 'south', 'south', 'south',
        #   'south', 'south', 'south', 'south', 'south', 'south', 'south', 'south', 'southwest', 'southwest', 'southwest',
        #    'southwest', 'brush', 'west', 'west', 'south', 'southwest', 'southwest', 'tent', 'out', 'north', 'southeast',
        #    'southeast', 'out', 'north', 'east', 'north', 'east', 'northwest', 'northeast', 'northeast', 'northeast',
        #    'northeast', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north',
        #    'north', 'north', 'northwest', 'northwest', 'northwest', 'west', 'west', 'west', 'northwest', 'northwest',
        #    'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel']

        self.GNOLL_CAVE = ['out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'southeast', 'southeast',
        'east', 'east', 'east', 'southeast', 'southeast', 'southeast', 'south', 'south', 'south', 'south', 'south', 'south', 'south',
        'south', 'south', 'south', 'south', 'south', 'southwest', 'southwest', 'southwest', 'southwest', 'brush', 'south',
        'southeast', 'east', 'trail', 'up', 'north', 'east', 'fissure', 'cleft', 'west', 'down', 'west',  'west',
        #gnoll jailer + barracks
        'shaft', 'door 2', 'south', 'out', 'south', 'east', 'door', 'out', 'door 2', 'out', 'east', 'west', 'west', 'north', 'north', 'out',
        #gnoll sub chiefs + Gnardu
        'west', 'opening', 'southwest', 'southwest', 'bridge', 'north', 'passage', 'northeast', 'east',
        'west', 'passage', 'southwest', 'bridge', 'south', 'northeast', 'opening', 'northeast',
        'northeast', 'east', 'east', 'south', 'up', 'up', 'out', 'north', 'west', 'southwest', 'down', 'down', 'west', 'northwest', 'north',
        'northwest', 'northeast', 'northeast', 'northeast', 'northeast', 'north', 'north', 'north', 'north', 'north', 'north',
        'north', 'north', 'north', 'north', 'north', 'north', 'northwest', 'northwest', 'northwest', 'west', 'west', 'west',
        'northwest', 'northwest', 'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel']

        self.CATHEDRAL = ['out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'south',
         'southwest', 'southwest', 'southwest', 'southwest', 'south', 'south', 'south', 'southwest', 'southeast',
         'south', 'south', 'south', 'south', 'south', 'south', 'south', 'south', 'south', 'south', 'cathedral',
         'doors', 'east', 'east', 'south', 'north', 'east', 'door', 'door', 'west', 'west', 'west', 'out',
         'street', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north',
         'northwest', 'northeast', 'north', 'north', 'north', 'northeast', 'northeast', 'northeast', 'northeast',
         'north', 'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel'
         ]

        self.ZOMBIES = ['out', 'south', 'east','east','east','north', 'try_gate',
        'east', 'east', 
        #McDermotts farm
        'northeast', 'northeast', 'north', 'north', 'north', 'gate', 'north', 'east', 'east', 'southeast', 'east', 'southeast', 'southeast', 'southeast', 'trail', 'woods', 'deeper',
        'out', 'trail', 'field', 'path', 'northwest', 'northwest', 'west', 'northwest', 'west', 'west', 'south', 'gate', 'south', 'south', 'south', 'sw', 'sw',
        #Malbon farm
        'southeast', 'southeast', 'south', 'gate', 'stile', 'northwest', 'southeast', 'southwest', 'northeast', 'stile', 'south', 'south',
        'north', 'north', 'gate', 'north', 'northwest', 'northwest',
        'ne', 'ne', 'east', 'east', 'east',
        #Calmor farmstop
        #'southeast', 'south', 'southeast', 'southeast', 'gate', 'southwest', 'sty', 'yard',
        'northeast', 'northeast',
        #into zombie farm
        'northeast', 'north', 'northeast', 'north', 'gate', 'compound', 'west', 'northwest', 'run', 'out', 'northeast', 'east', 'south', 'south',
        #out of zombie farm and into highmarket
        'path', 'gate', 'south', 'southwest', 'south', 'southwest', 'east', 'east', 'gate',
        #from highmarket back to chapel
        'south', 'southeast', 'southeast', 'south', 'east', 'gate', 'south', 'south', 'southeast', 'southeast', 'south', 'south',
        'south', 'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest', 'north', 'gate', 'east', 'north', 'north',
        'north', 'west', 'north', 'chapel']
        #Farmer's gate / Dragon Road

        # self.BANDIT_CAMP = ['out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'south',
        # 'southwest', 'southwest', 'southwest', 'trail', 'northwest', 'northwest', 'west', 'west',
        # ]

        self.PATH_TO_SKIP_WITH = ['think']

    def do_go_hooks(self, exit_str):
        # magentaprint(str(self.character.AREA_ID) + ", " + exit_str, False)
        if exit_str == "slow_prepare":
            self.sleep(5)
            self.command_handler.process("prepare")
            return True
        elif exit_str == "try_gate":
            curArea = int(self.character.AREA_ID)
            self.command_handler.process("go gate")
            self.sleep(3)
            if (curArea == int(self.character.AREA_ID)):
                magentaprint("failed to go through the gate probably", False)
                self.direction_list = ['oops','s','w','w','w','n','chapel']
            return True
        elif exit_str == "think":
            return True
        else:
            return super().do_go_hooks(exit_str)

    def do_pre_go_actions(self):
        self.rest_and_check_aura()
        self.check_weapons()
        self.check_armour()

        if self.has_buff_ability():
            if self.use_buff_ability():
                self.use_extra_buff_items()
        else:
            pass
            # Need a timer for this...
            # self.use_extra_buff_items()

    def has_buff_ability(self):
        return len(self.character._class.buff_skills) > 0

    def use_extra_buff_items(self):
        self.use_extra_bless_item()
        self.use_extra_steel_bottle()

    def decide_where_to_go(self):
        magentaprint("Inside decide_where_to_go", False)

        if self.character.AREA_ID != 2:
            return ['areaid2']

        magentaprint("next path = " + str(self.__nextpath), False)

        if self.character.DEAD:
            self.character.DEAD = False
            self.character.DEATHS += 1
            # magentaprint("Died: Pulling up my bootstraps and starting again", False)
            magentaprint("Died: stopping bot thread.", False)
            self.stop()
            return self.LIMBO_TO_CHAPEL[:]

        self.__nextpath = (self.__nextpath + 1) % self.__TOTALPATHS

        # return self.track_builder(self.ZOMBIES, 9, 20, -1)

        if self.__nextpath % 4 == 0:
            # self.inventory.get_inventory()
            magentaprint(str(int(len(self.inventory.sellable()))) + " items to sell - threshold is " + str(self.loot_threshold) + '.')
            if len(self.inventory.sellable()) > self.loot_threshold:
                magentaprint("Trackgrind pawning/dropping!!!")
                return self.SHOP_AND_TIP_PATH[:]
            else:
                magentaprint("Trackgrind skipped pawning/dropping!!!")
        elif self.__nextpath == 1:
            return self.track_builder(self.THEATRE_PATH, 1, 20, 0)
        elif self.__nextpath == 3:
            return self.track_builder(self.MARKET_PATH, 1, 20, 0)
        elif self.__nextpath == 5:
            return self.track_builder(self.MILITIA_SOLDIERS_PATH, 1, 20, 0)
        elif self.__nextpath == 7:
            return self.track_builder(self.KOBOLD_PATH, 4, 20, -1)
        elif self.__nextpath == 9:
            return self.track_builder(self.CORAL_ALLEY_PATH, 1, 6, -1)
        elif self.__nextpath == 11:
            return self.track_builder(self.FORT_PATH, 1, 20, 1)
        elif self.__nextpath == 13:
            return self.track_builder(self.NORTHERN_BANDITS_PATH, 1, 20, -1)
        elif self.__nextpath == 15:
            return self.track_builder(self.ZOMBIES, 6, 20, 0)
        elif self.__nextpath == 17:
            return self.track_builder(self.DWARVEN_FIELD_WORKERS_PATH, 9, 20, 0)
        elif self.__nextpath == 19:
            return self.track_builder(self.MILL_WORKERS, 9, 20, 0)
        elif self.__nextpath == 21:
            return self.track_builder(self.MUGGER_PATH, 9, 20, -1)
        elif self.__nextpath == 23:
            return self.track_builder(self.RANCHER_SENTRY, 10, 20, 1)
        elif self.__nextpath == 25:
            return self.track_builder(self.GNOLL_CAVE, 12, 20, -1)
        elif self.__nextpath == 27:
            return self.track_builder(self.KNIGHTS, 12, 20, 1)
        elif self.__nextpath == 29:
            return self.track_builder(self.CATHEDRAL, 15, 20, 1)
        elif self.__nextpath == 31:
            return self.track_builder(self.SPIDER_FOREST, 12, 20, -1)
        else:
            magentaprint("Unexpected case in decide_where_to_go, nextpath==" + str(self.__nextpath))
            return list(self.PATH_TO_SKIP_WITH[:])
        return list(self.PATH_TO_SKIP_WITH[:])

    def track_builder(self, track, min_level, max_level, track_aura):
        level_range = range(min_level, max_level)        

        character_aura = Aura(self.character.AURA)
        aura_acceptable = True

        #too evil shouldn't fight good (+1)
        #too good shouldn't fight evil (-1)
        if (character_aura < self.character.preferred_aura and track_aura == 1) or \
           (character_aura > self.character.preferred_aura and track_aura == -1):
            aura_acceptable = False

        if self.character.level in level_range and aura_acceptable:
            return track[:]
        else:
            self.__nextpath = self.__nextpath + 1
            return self.PATH_TO_SKIP_WITH[:]

    def stop(self):
        super().stop()

# Just thinking about changing top level...

# I don't like this version because mobs will leave and arrive while in
# combat.  It makes more sense to recheck list every time I enter combat...
# right?  That means doing a look between every mob.  I want to avoid the
# complication of multiple threads, I want the two threads to interact only
# via flag handshakes... so I don't want MUD_read to edit monster_list.
# How about MUD_read sets a flag when a mob arrives or leaves and I update
# monster list only when I have to?  Still doing the unnecessary look although
# not very often.  Maybe its okay to edit monster_list in the case of
# arriving mobs... and leaving mobs?  Seems like a bad idea.  However, when
# do I react to a guard arriving?  I think that I need a list that MUD_read
# will edit and I need to keep a local copy.  Hey I'm already doing it.

# Okay.  So monster_list is the local copy, and MUD_read will edit
# MONSTER_LIST relatively freely:
#   - Full update when MONSTER_CHECK_FLAG is set high by bot.
#   - one-by-one additions if monsters arrive (no flag)
# Then I can check for arrived monsters in the bot by checking if the
# lists are different.
# However, that is for later.  I wanted to make it possible to implement later
# fleeing when a guard arrives, but I won't be doing that yet.

# New approach is to keep a mob list up to date (with mob arrivals and
# departures, ideally,) and then changing logic to say, decide on WHICH
# mob to kill.  That also doubles as deciding whether to engage.  Its a
# sensible way to check for guards.

# You can't.  Its broken.  (Means the bot ran out of weapons.)
