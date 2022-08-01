
from bots.GrindThread import GrindThread
from misc_functions import magentaprint, get_timeint
from Aura import Aura
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

        self.track_abandons = 0
        self.abandoned_last_track = False
        self.on_track = False
        self.last_track = None
        self.starting_path = starting_path
            # len(self.tracks) = 24
        # elif self.character.level <= 10:
        #     len(self.tracks) = 20 # start the fort and bandits at lvl 8
        # elif self.character.level > 12:
        #     len(self.tracks) = 24
        # else:
        #     len(self.tracks) = 22 # start the fort and bandits at lvl 8

        self.LIMBO_TO_CHAPEL = ["ame", "out", "w", "n", "chapel"]

        self.SHOP_AND_TIP_PATH = ["areaid2",
            "out", "south", "west", 'west', 'west', 'south', 'south', "shop",
            "sell_items","out", "southeast", 'east', 'east', 'east', 'east', "northeast", "tip",
            "drop_items","out", 'north', 'north', 'west', 'west', 'west', 'north', "chapel"
        ]
        self.smart_theatre_path = ['areaid14', "theatre", "stairs","cubby", "out", "box", "out", "box 2",
            "out", "down", "swing", "seat", "out", "down", "seat", "out", "door", "office", "out",
            "stage","side 2","backstage", "door", "out", "door 2", "out", "curtain", "stage",
            "side", "door","up", "out", "out"]
        self.THEATRE_PATH = ["areaid2",
            "out", "s", "w", "w", "w", "s", "theat", "stairs","cubby", "out", "box", "out", "box 2",
            "out", "down", "swing", "seat", "out", "down", "seat", "out", "door", "office", "out",
            "stage","side 2","backstage", "door", "out", "door 2", "out", "curtain", "stage",
            "side", "door","up", "out", "out", "n", "e","e", "e", "n", "chapel"
        ]
        self.smart_market_path = ['areaid113','w', 'w', 'office', 'out', 'n', 'n','s', 'w', 'e', 's', 'w', 's', 'n', 'w', 'e', 'n',
            's', 'e', 'e', "out"]
        self.MARKET_PATH = ["areaid2", 
            "out", 's', 'e', 'e', 'e', 'n', 'w', 'w', 'office', 'out', 'n', 'n','s', 'w', 'e', 's', 'w', 's', 'n', 'w', 'e', 'n',
            's', 'e', 'e', "out", 's', 'w', 'w', 'w', 'n',"chapel"
        ]
        self.smart_militia_path = ['areaid524','s','s','s','s','s','s','w','doo','stor','ou','ou','w','w','w','n','n','s','s','e','e','e','e','n','n','e',
            'e','e','e','e','e','e','e','e','ne','e','ne','ne','ne','ne','ne','ne','n','n','w','s','sw','ne','n','e',
            'n','n','n','n','n','n','n','n','n','n','nw','nw','nw','path','nw','n','n','n','nw','nw','n','n']
        self.MILITIA_SOLDIERS_PATH = ["areaid2", 
            'out','s','e','s','s','s','w','gate','s','s','sw','sw','sw','sw','s','s','s','sw','southeast','s','s','s','s',
            's','s','s','s','s','w','doo','stor','ou','ou','w','w','w','n','n','s','s','e','e','e','e','n','n','e',
            'e','e','e','e','e','e','e','e','ne','e','ne','ne','ne','ne','ne','ne','n','n','w','s','sw','ne','n','e',
            'n','n','n','n','n','n','n','n','n','n','nw','nw','nw','path','nw','n','n','n','nw','nw','n','n','gate',
            'w','n','nw','nw','n','e','e','e','s','s','s','s','gate','s','s','southeast','southeast','s','s','s','southeast','s','w','w',
            'w','nw','nw','n','gate','e','n','n','n','w','n','chapel'
        ]
        self.smart_kobold_path = ['areaid1165','glowing portal','passage','mines',
            'down','n','n','n','n','ne','n','w','n','n','e','door','w','gully','up','boulder','up',
            'cave 3','ne','ne','n','s','up','e','se','cave','out','ladder','cave','out','sw','w',
            'sw','se','nw','w','out','down','boulder','down','down','e','door','w','s','s','e','s','sw','s','s','s',
            's','gully','glowing portal']
        self.KOBOLD_PATH = ["areaid2",
            'out','south','east','south','south','south','west','gate','south','southeast','southeast','east',
            'east','east','southeast','southeast','southeast','south','south','south','south','south','east',
            'east','southeast','east','south','south','south','south','glowing portal','passage','mines',
            'down','n','n','n','n','ne','n','w','n','n','e','door','w','gully','up','boulder','up',
            'cave 3','ne','ne','n','s','up','e','se','cave','out']

        # if self.character.level >= 9 and not self.is_character_class('Mag'):
        #     self.KOBOLD_PATH += ['slow_prepare', 'e', 'ne', 'door',
        #     # 'statue', 'down', 'down', 'down', 'down', 'hole', 'corridor', 'east', 'east', 'southeast', 'south', 'south'
        #     # 'south', 'south', 'east', 'cave', 'out', 'west', 'west', 'west', 'west', 'west', 'north', 'north', 'north',
        #     # 'north', 'north', 'east', 'passage', 'out', 'hole', 'up', 'up', 'up', 'up', 'out',
        #     'door', 'slow_prepare', 'sw','w']
        #     # Note: You can remove the following line of code to remove the kobold guards and priests fights.
        #     # Priests turn you very blue.  These fights may be difficult.
        #     # Also useful to test mobs who join in.
        #     # They're commented because kobolds are allowed when you're pale blue, which is one off of blue... and these guards
        #     # and priests are dangerous unless the bot decides on his own to engage.  Todo: check aura here (if health is
        #     # high enough,) and go in if all's good.  Even fight the priests - because the more 'good' we can get the
        #     # more chalices we can farm.
        self.KOBOLD_PATH += [
            'ladder','cave','out','sw','w',
            # 'cave', 'out',  # Comment out insane kobold (TODO: check level here)
            'sw','se','nw','w','out','down','boulder','down','down','e','door','w','s','s','e','s','sw','s','s','s',
            's','gully','glowing portal','passage','coral','north','north','north','north','west','northwest','west','west',
            'north','north','north','north','north','northwest','northwest', 'northwest', 'west', 'west', 'west',
            'northwest','northwest', 'north', 'gate', 'east', 'north', 'north', 'north','west', 'north', 'chapel'
        ]
        self.CORAL_ALLEY_PATH = ["areaid2",
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
        self.smart_fort_path = ['areaid314', 'n','n','w','s','store','out','s','e','e','n',"door", "door",
            'n','w','s','s']
        self.FORT_PATH = [
            'out','n','n', 'w','gate','n','n','n','n','n','gate','n','n','w','s','store','out','s','e','e','n',"door", "door",
            'n','w','s','s','gate', 's','s','s','s','s','gate','w','sw','s','s','s','e','e','e','e','n','w','n','chap'
        ]
        self.OLD_MAN_JAMES = ['areaid611', 'out', 'west', 'north', 'smithy']
        # self.GOOURD = [
        #     'areaid1899'
        # ]
        self.MUGGER_PATH = ["areaid2",
            'ou','s','w','w','w','s','alley','w','alley','e','e','e','e','e','n','w','n','chap'
        ]
        self.smart_northern_bandits_path = ['areaid421','south','s','s','n','n','n']
        self.NORTHERN_BANDITS_PATH = ["areaid2", 
            'out','n','n','w','gate','n','n','n','n','n','gate','n','n','gate','n','nw','nw','sw','sw','sw','sw','s',
            'sw','sw','w','w','sw','sw','sw','sw','sw','sw','w','w','w','w','nw','w','w','nw','sw','nw','w','w','w',
            'nw','w','w','w','w','south','s','s','n','n','n','e','e','e','e','se','e','e','e','se','ne','se','e','e',
            'se','e','e','e','e','ne','ne','ne','ne','ne','ne','e','e','ne','ne','n','ne','ne','ne','ne','se','se','s',
            'gate','s','w','e','s','gate','s','s','s','s','s','gate','e','s','s','chapel'
        ]

        self.smart_dwarven_path = ['areaid1082', 'east', 'building', 'kitchen', 'out',
            'out', 'hall', 'out', 'east', 'east', 'forge', 'out', 'southeast', 'field', 'road', 'field 2', 'road', 'southeast',
            'southeast', 'field', 'road', 'southeast', 'field', 'stile', 'stile', 'road',
            'southeast', 'field', 'road', 'southeast', 'station']
        self.DWARVEN_FIELD_WORKERS_PATH = ["areaid2",'out', 'south', 'east', 'south', 'south',
            'south', 'east', 'west', 'west', 'gate', 'south', 'southeast', 'southeast',
            'east', 'east', 'east', 'pathway', 'northwest', 'north', 'north',
            'north', 'southeast', 'east', 'east', 'gate', 'east', 'building', 'kitchen', 'out',
            'out', 'hall', 'out', 'east', 'east', 'forge', 'out', 'southeast', 'field', 'road', 'field 2', 'road', 'southeast',
            'southeast', 'field', 'road', 'southeast', 'field', 'stile', 'stile', 'road',
            'southeast', 'field', 'road', 'southeast', 'station', 'out', 'northwest', 'northwest',
            'northwest', 'northwest', 'northwest', 'northwest', 'west', 'west',
            'west', 'gate', 'west', 'west', 'northwest', 'south', 'south', 'south',
            'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest',
            'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel'
        ]
        #both gates close at night unforunately...
        self.FIELD_WORKERS_PATH = ["areaid2",
            'out', 'south', 'east', 'south', 'south', 'south', 'east', 'west', 'west',
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
        self.smart_mill_path = ['areaid515', 'areaid518', 'areaid1450', 'areaid541', 'areaid1452']
        #Contains lvl 2&3 mobs (stacker, furniture maker, sawmill operator, mill worker) and lvl 6 mobs (sawmill / mill supervisors)
        self.MILL_WORKERS = ["areaid2",
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
        self.smart_rancher_path = ['areaid1517', 'arch', 'north', 'east', 'north', 'northwest',
            'gate', 'north', 'east', 'east', 'south', 'east', 'north', 'south',
            'west', 'west', 'west']
        self.RANCHER_SENTRY = ["areaid2",
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

        self.SPIDER_FOREST = ['areaid1886','areaid2355','areaid1886','areaid2355']

        #The following areas repeat a bit because the spawns are fast
        self.smart_knights_path = ['areaid1053', 'south',
            'southeast', 'east', 'east', 'northeast', 'north', 'red tent', 'out', 's', 'w', 'w', 'w', 'e', 'e', 'e',
            'sw', 'w', 'w', 'nw', 'n', 'n', 'ne', 'stands', 'stand', 'out', 'stand 2', 'out', #'stand 3', 'out' #Tario
            'e', 'se', 'w', 'w', 'w', 'e', 'e', 'e', 's', 'red tent']
        self.KNIGHTS = ["areaid2",
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

        self.smart_gnoll_cave = ['areaid1763', 'west', 'down', 'west',  'west',
        #gnoll jailer + barracks
        'shaft', 'door 2', 'south', 'out', 'south', 'east', 'door', 'out', 'door 2', 'out', 'east', 'west', 'west', 'north', 'north', 'out',
        #gnoll sub chiefs
        'west', 'opening', 'southwest', 'southwest', 'bridge', 'north', 'passage', 'northeast']
        self.GNOLL_CAVE = ["areaid2",'out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'southeast', 'southeast',
        'east', 'east', 'east', 'southeast', 'southeast', 'southeast', 'south', 'south', 'south', 'south', 'south', 'south', 'south',
        'south', 'south', 'south', 'south', 'south', 'southwest', 'southwest', 'southwest', 'southwest', 'brush', 'south',
        'southeast', 'east', 'trail', 'up', 'north', 'east', 'fissure', 'cleft', 'west', 'down', 'west',  'west',
        #gnoll jailer + barracks
        'shaft', 'door 2', 'south', 'out', 'south', 'east', 'door', 'out', 'door 2', 'out', 'east', 'west', 'west', 'north', 'north', 'out',
        #gnoll sub chiefs
        'west', 'opening', 'southwest', 'southwest', 'bridge', 'north', 'passage', 'northeast']
        
        if self.character.level >= 15:
            # Gnardu the Warlord, also gnoll warriors block this path
            self.GNOLL_CAVE += [
            'east', 'west' 
            ]
            self.smart_gnoll_cave += [
            'east', 'west' 
            ]
        
        self.GNOLL_CAVE += [
        'passage', 'southwest', 'bridge', 'south', 'northeast', 'opening', 'northeast',
        'northeast', 'east', 'east', 'south', 'up', 'up', 'out', 'north', 'west', 'southwest', 'down', 'down', 'west', 'northwest', 'north',
        'northwest', 'northeast', 'northeast', 'northeast', 'northeast', 'north', 'north', 'north', 'north', 'north', 'north',
        'north', 'north', 'north', 'north', 'north', 'north', 'northwest', 'northwest', 'northwest', 'west', 'west', 'west',
        'northwest', 'northwest', 'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel']

        self.CATHEDRAL = ["areaid2",'out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'south',
         'southwest', 'southwest', 'southwest', 'southwest', 'south', 'south', 'south', 'southwest', 'southeast',
         'south', 'south', 'south', 'south', 'south', 'south', 'south', 'south', 'south', 'south', 'cathedral',
         'doors', 'east', 'east', 'south', 'north', 'east', 'door', 'door', 'west', 'west', 'west', 'out',
         'street', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north', 'north',
         'northwest', 'northeast', 'north', 'north', 'north', 'northeast', 'northeast', 'northeast', 'northeast',
         'north', 'north', 'gate', 'east', 'north', 'north', 'north', 'west', 'north', 'chapel'
         ]

        self.ZOMBIES = ['areaid113', 'try_gate',
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
        'northeast', 'north', 'northeast', 'north', 'gate', 'compound', 'west', 'barn', 'out', 'northwest', 'run', 'out', 'northeast', 'east', 'south', 'south',
        #out of zombie farm and into highmarket
        'path', 'gate', 'south', 'southwest', 'south', 'southwest', 'east', 'east', 'gate',
        #from highmarket back to chapel
        # 'south', 'southeast', 'southeast', 'south', 'east', 'gate', 'south', 'south', 'southeast', 'southeast', 'south', 'south',
        # 'south', 'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest', 'north', 'gate', 'east', 'north', 'north',
        # 'north', 'west', 'north', 'chapel'
        ]
        #Farmer's gate / Dragon Road

        # self.BANDIT_CAMP = ['out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'south',
        # 'southwest', 'southwest', 'southwest', 'trail', 'northwest', 'northwest', 'west', 'west',
        # ]

        self.FOUNDRY = ['areaid1231', 'out', 'down', 'east', 'east', 'east', 'south']
        self.ALCHEMISTS = ['areaid999', 'areaid2967']
        self.EGAN_TRENT = ['areaid1999']
        self.ORCS = ['areaid747', 'areaid749']
        self.OLMER = ['areaid297']
        self.CHERYN = ['areaid1380']
        self.ARTIFICERS = ['areaid1350', 'areaid1008']
        self.SILKEN_ALLEY = ['areaid686', 'areaid706', 'areaid705', 'areaid698', 'areaid699', 'areaid700']
        self.CORELLAN = ['areaid713']
        self.JERREK_TAG = ['areaid977', 'areaid979']
        self.MANIC_ELDER = ['areaid1899', 'areaid1465', 'areaid1491']
        self.VILADIN_CAL = ['areaid1498', 'areaid247', 'path', 'hut']
        self.DALLA_DOUVAN = ['areaid2449', 'areaid2430']
        self.ALDO_BROTAIN = ['areaid1254', 'areaid1226']
        self.PLOVERS = ['areaid1564', 'areaid1600']
        self.FLOOR_MANAGER = ['areaid1147']
        self.TARDAN = ['areaid1378']
        self.RIMARK = ['areaid1231']
        self.HORBUK = ['areaid1265']
        self.DOJO = ['areaid917']
        self.DINI = ['areaid629']
        # self.WHITEBLADE_LYRON = ['areaid2110', 'areaid2097']
        # self.LYRON = ['areaid2097', ] -- too much dmg

        # Old Man James
        # Dini Stonehammer
        # Thereze
        # Olmer
        # Goourd
        # cooper
        # Farmer Calmor
        # Kelluran
        # Rimark ?
        # Tag

        self.GNOMES = ['areaid2113', 'areaid2099', 'areaid2104', 'areaid2106', 'areaid2138', 'areaid2138', 'areaid2093', 'areaid2094', 'areaid2095']

        self.PATH_TO_SKIP_WITH = ['think']

        self.setup_tracks()
        
        if isinstance(self.starting_path, int) and self.starting_path < len(self.tracks):
            self.__nextpath = self.starting_path
        else:
            self.__nextpath = random.randrange(0, len(self.tracks))

    def create_zombies_path(self):
        path = ['out', 'south', 'east','east','east','north', 'try_gate',
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
        'northeast', 'north', 'northeast', 'north', 'gate', 'compound', 'west', 'barn', 'out', 'northwest', 'run', 'out', 'northeast', 'east', 'south', 'south',
        #out of zombie farm and into highmarket
        'path', 'gate', 'south', 'southwest', 'south', 'southwest', 'east', 'east', 'gate',
        #from highmarket back to chapel
        'south', 'southeast', 'southeast', 'south', 'east', 'gate', 'south', 'south', 'southeast', 'southeast', 'south', 'south',
        'south', 'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest', 'north', 'gate', 'east', 'north', 'north',
        'north', 'west', 'north', 'chapel']

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

    def setup_tracks(self):
        self.tracks = [
            Track("Theatre", self.smart_theatre_path, 0, 20, 0),
            Track("Market", self.smart_market_path, 0, 14, 0),
            Track("Militia Soldiers", self.smart_militia_path, 0, 14, 0),
            Track("Kobolds", self.smart_kobold_path, 0, 10, -1), #sentries are suuuper tough
            Track("Coral Alley", self.CORAL_ALLEY_PATH, 0, 6, -1),
            Track("Fort", self.smart_fort_path, 9, 20, 0),
            Track("North Bandits", self.smart_northern_bandits_path, 9, 14, -1),
            Track("Eastern Zombies", self.ZOMBIES, 8, 20, -1),
            Track("Shop and Tip 1",self.SHOP_AND_TIP_PATH,0,20,9),
            Track("Dwarven Field Workers", self.smart_dwarven_path, 9, 20, 0),
            Track("Mill Workers", self.smart_mill_path, 9, 20, 0),
            # Track("Muggers", self.MUGGER_PATH, 9, 15, -1),
            # Track("Old Man James", self.OLD_MAN_JAMES, 9, 20, 0),
            Track("Gnolls", self.smart_gnoll_cave, 11, 20, -1),
            Track("Olmer", self.OLMER, 11, 20, -1),
            Track("Cheryn", self.CHERYN, 11, 15, -1),
            Track("Orcs", self.ORCS, 11, 20, -1),
            Track("Artificers", self.ARTIFICERS, 11, 20, -1),
            # Track("Foundry", self.FOUNDRY, 16, 20, 0), #Rimark joins in, not enough mobs actually are there by default
            Track("Rancher Sentries", self.smart_rancher_path, 12, 20, 1),
            Track("Knights", self.smart_knights_path, 10, 20, 1),
            # Track("Cathedral", self.CATHEDRAL, 10, 16, 1), # lay priest damage rolls too high
            Track("Large Spider Forest", self.SPIDER_FOREST, 12, 20, -1),
            Track("Egan and Trent", self.EGAN_TRENT, 12, 20, -1),
            Track("Tardan", self.TARDAN, 15, 20, 0),
            Track("Rimark", self.RIMARK, 15, 20, 1),
            Track("Dojo", self.DOJO, 15, 20, 1),
            Track("Dini", self.DINI, 11, 15, 0),
            Track("Horbuk", self.HORBUK, 15, 20, 1),
            Track("Shop and Tip 2",self.SHOP_AND_TIP_PATH,0,20,9),
            Track("Silken Alley", self.SILKEN_ALLEY, 11, 20, 0),
            # Track("Corellan", self.CORELLAN, 16, 20, 0),
            Track("Jerrek and Tag", self.JERREK_TAG, 11, 20, -1),
            Track("Gnomes", self.GNOMES, 10, 12, 1),
            Track("Goourd, Manic and Elder", self.MANIC_ELDER, 10, 13, 0),
            Track("Viladin and Cal", self.VILADIN_CAL, 12, 20, 1),
            # Track("Plovers", self.PLOVERS, 12, 20, 1),
            Track("Floor Manager", self.FLOOR_MANAGER, 12, 20, -1),
            # Track("Dalla and Douvan", self.DALLA_DOUVAN, 11, 20, 1), # Dalla overheals and is too dangerous
            Track("Aldo and Brotain", self.ALDO_BROTAIN, 11, 20, 1),
            Track("Shop and Tip 3",self.SHOP_AND_TIP_PATH,0,20, 9)
        ]
    
    def decide_where_to_go(self):
        magentaprint("Inside decide_where_to_go", False)

        # if self.character.AREA_ID != 2:
        #     return ['areaid2']

        magentaprint("next path = " + str(self.__nextpath), False)

        if self.character.DEAD:
            # crash
            self.character.DEAD = False
            self.character.DEATHS += 1
            magentaprint("Died; Pulling up my bootstraps and starting again", False)
            return self.LIMBO_TO_CHAPEL[:]

        if self.character.NEEDS_TO_SELL:
            magentaprint("Character needs to sell - going to sell path", False)
            self.character.NEEDS_TO_SELL = False
            self.character.MONSTER_KILL_LIST = []
            return self.SHOP_AND_TIP_PATH[:]
        # else:
        #     magentaprint("Character doesn't need to sell", False)

        nextpath = None
        if self.last_track is not None and self.abandoned_last_track:
            magentaprint("abandoned last track so we're re-running it", False)
            nextpath = self.evaluate_track(self.last_track)
        else:
            self.__nextpath = (self.__nextpath + 1) % len(self.tracks)
            nextpath = self.evaluate_track(self.tracks[self.__nextpath])
    
        self.abandoned_last_track = False

        return nextpath

    def evaluate_track(self, track):
        level_range = range(track.min_level, track.max_level)        

        character_aura = Aura(self.character.AURA)
        aura_acceptable = character_aura == self.character.preferred_aura

        if track.track_aura == 9:
            return track.track[:]

        #too evil shouldn't fight good (+1)
        #too good shouldn't fight evil (-1)
        if (not aura_acceptable and track.track_aura == 0) or \
           (character_aura < self.character.preferred_aura and track.track_aura == 1) or \
           (character_aura > self.character.preferred_aura and track.track_aura == -1):
            magentaprint("{0} isn't acceptable to us due to aura".format(track.name), False)
            return self.PATH_TO_SKIP_WITH[:]

        if self.character.level in level_range:
            magentaprint("{0} is our chosen track".format(track.name), False)
            if self.character.current_track is not None:
                self.end_track()
            self.start_track(track)
            
            return track.track[:]
        else:
            magentaprint("{0} isn't acceptable to us due to level".format(track.name), False)
            # self.__nextpath = self.__nextpath + 1 #skips the next path
            return self.PATH_TO_SKIP_WITH[:]

    def start_track(self, track):
        self.track_start_time = get_timeint()
        self.character.start_track(track)
        self.last_track = track
        self.on_track = True

    def end_track(self):
        self.track_end_time = get_timeint()
        track_time = (self.track_end_time - self.track_start_time).total_seconds()
        self.character.TRACK_TIME += track_time
        self.character.add_to_track_param('completes', 1)
        self.character.add_to_track_param('duration', track_time)
        self.character.end_track()
        self.on_track = False
        magentaprint("ending track", False)

    def stop(self):
        super().stop()

class Track():
    def __init__(self, name, track, min_level, max_level, track_aura):
        self.name = name
        # setup the track with a buffer at the end so that last node mobs don't get misattributed to the next track
        track.append("think")
        self.track = track
        self.last_run = 0
        self.min_level = min_level
        self.max_level = max_level
        self.track_aura = track_aura
        self.runs = 0
        self.abandons = 0
        self.completes = 0
        self.kills = 0
        self.exp = 0
        self.duration = 0
    
    def start(self):
        self.last_run = int(round(get_timeint().timestamp()))

    def toJson(self):
        return {
            "name": self.name,
            "last_run": self.last_run,
            "min_level": self.min_level,
            "max_level": self.max_level,
            "track_aura": self.track_aura,
            "runs": self.runs,
            "abandons": self.abandons,
            "completes": self.completes,
            "kills": self.kills,
            "exp": self.exp,
            "duration": self.duration
        }

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
