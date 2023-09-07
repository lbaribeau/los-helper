
from bots.GrindThread import GrindThread
from misc_functions import magentaprint, get_timeint, get_timeint_from_int
from Aura import Aura
import db.Area
from db.Mob import Mob
import random, re, time

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
        self.skipped_last_track = False
        self.on_track = False
        self.last_track = None
        self.starting_path = 1
            # len(self.tracks) = 24
        # elif self.character.level <= 10:
        #     len(self.tracks) = 20 # start the fort and bandits at lvl 8
        # elif self.character.level > 12:
        #     len(self.tracks) = 24
        # else:
        #     len(self.tracks) = 22 # start the fort and bandits at lvl 8

        self.LIMBO_TO_CHAPEL = ["ame", "out", "w", "n", "chapel"]

        self.SHOP_AND_TIP_PATH = ["areaid2",
            "sell_items"
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
        self.BERTRAM = ["areaid109"]
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
        self.smart_kobold_path = ['areaid1165','glowing portal','mines',
            'down','n','n','n','n','ne','n','w','n','n','e','door','w','gully','up','boulder','up',
            'cave 3','ne','ne','n','s','up','e','se','cave','out','ladder','cave','out','sw','w',
            'sw','se','nw','w','out','down','boulder']
            # ,'down','down','e','door','w','s','s','e','s','sw','s','s','s',
            # 's','gully','glowing portal']
        self.KOBOLD_PATH = ["areaid2",
            'out','south','east','south','south','south','west','gate','south','southeast','southeast','east',
            'east','east','southeast','southeast','southeast','south','south','south','south','south','east',
            'east','southeast','east','south','south','south','south','glowing portal','passage','mines',
            'down','n','n','n','n','ne','n','w','n','n','e','door','w','gully','up','boulder','up',
            'cave 3','ne','ne','n','s','up','e','se','cave','out']

        # if self.character.level >= 9 and not self.is_character_class('Mag'):
        self.KOBOLD_PATH += ['slow_prepare', 'e', 'ne', 'door',
        'statue', 'down', 'down', 'down', 'down', 'hole', 'corridor', 'east', 'east', 'southeast', 'south', 'south'
        'south', 'south', 'east', 'cave', 'out', 'west', 'west', 'west', 'west', 'west', 'north', 'north', 'north',
        'north', 'north', 'east', 'passage', 'out', 'hole', 'up', 'up', 'up', 'up', 'out',
        'door', 'slow_prepare', 'sw','w']
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
            'northwest','northwest', 'north', 'gate', 'east', 'north', 'north', 'north','west', 'north', 'chapel']
        # Since kobolds are so far, we won't do what we did with bandits
        self.KOBOLDS1 = [
            # For somewhat low level characters (this is pretty safe)
            # Also go fight the children first, we don't want to miss out on them
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','se','se','se','s','s','s','s','s','e','e',
            'se','e','s','s','s','s','glowing portal','passage','mines','down','n','n','n','n','ne','n','w','n','n',
            'e','door','w','gully','up','boulder','up','cave 3','ne','ne','n','s','up','e','cave','out', # child large
            'se','cave','out', # large kobolds (danger?)
            #'prepare', 'e', 'ne', 'door', 'door', 'prepare', 'sw','w',
            'ladder','cave','out', # champion
            'sw','w',
            # 'cave', 'out',  # Comment out insane kobold
            'sw','se',# shaman
            'nw','w','out','down','boulder','down','down','e','door','w','s','s','e','s','sw','s','s','s',
            's','gully','glowing portal','passage','coral','n','n','n','n','w','nw','w','w','n','n','n','n','n','nw',
            'nw', 'nw', 'w', 'w', 'w','nw','nw', 'n', 'gate', 'e', 'n', 'n', 'n','w', 'n', 'chapel'
        ]
        self.kobold_guards_and_insane = [
            # Take the scenic route so we fight in the safest order (some auras can choose not to fight)
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','se','se','se','s','s','s','s','s','e','e',
            'se','e','s','s','s','s','glowing portal','passage','mines','down','n','n','n','n','ne','n','w','n','n',
            'e','door','w','gully','up','boulder','up','cave 3','ne','ne',#'n','s',
            'up','e','se',
            'prepare', 'e', 'ne', # guards
            #'door', 'door', # priests
            'prepare', 'sw','w', 
            'ladder','sw','w','cave','out', # insane 1st after guards
            'sw','se', # shaman
            'nw','ne','e','ne','cave','out', # champion
            'ladder','cave','out', # 2 large
            'nw','cave','out', # child large
            'w','d','n','s', # family
            'sw','sw','out',
            'down','boulder','down','down','e','door','w','s','s','e','s','sw','s','s','s',
            's','gully','glowing portal','passage','coral','n','n','n','n','w','nw','w','w','n','n','n','n','n','nw',
            'nw', 'nw', 'w', 'w', 'w','nw','nw', 'n', 'gate', 'e', 'n', 'n', 'n','w', 'n', 'chapel'
        ] 
        self.kobold_priests = self.kobold_guards_and_insane[0:59] + ['door','door'] + self.kobold_guards_and_insane[60:]
            # Priests turn you very blue.  These fights may be difficult.
            # Also useful to test mobs who join in.
            # They're optional because kobolds are allowed when you're pale blue, which is one off of blue... and these guards
            # and priests are dangerous unless the bot decides on his own to engage.  Todo: check aura here (if health is
            # high enough,) and go in if all's good.  Even fight the priests - because the more 'good' we can get the
            # more chalices we can farm.
        self.kobold_massacre = [
            "areaid2",
            # Brocolli wants to get ALL the kobolds in one shot... even the chief? Yeahh.
            # This route is optimal traval and isn't picky about order
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','se','se','se','s','s','s','s','s','e','e',
            'se','e','s','s','s','s','glowing portal','passage','mines','down','n','n','n','n','ne','n','w','n','n',
            'e','door','w','gully','up','boulder','up','cave 3','ne','ne','n','s','up','e','cave','out', # child, large
            'se','cave','out', # large kobolds
            'prepare', 'e', 'ne', 'door', 
            'stat','d','d','d','d','hole','room','out','corr',
            's','sw','s','w','s','s','se','n','n','n','e','s','s','s','e','n','n','e',#temple
            's','s','e','n','e','cave', # unlock trap key; trap; out;
            'out','n','nw','n','n','w','n','w','passage','out','hole',
            'u','u','u','u','out',
            # First try convoluted (after corridor)
            'e','e','se','w','w','w','sw','s','w','s','s','se','n','n','n','e',
            'e','s','w','s','s','e','e','n','e','s','n','e','cave',# unlock trap key; trap; out
            'out','n','nw','n','sw','s','w','s','s','se','n','n','n','e','s','s','s','e','n','n','e','s','s','e','n','e','cave',
            'out'
            'door', 'prepare', 'sw','w',
            'ladder','cave','out', # champion
            'sw','w',
            # 'cave', 'out', #insane (maybe don't take that fight in case both hammers are gonzo)
            'sw','se',# shaman
            'nw','w','out','down','boulder','down','down','e','door','w','s','s','e','s','sw','s','s','s',
            's','gully','glowing portal','passage','coral','n','n','n','n','w','nw','w','w','n','n','n','n','n','nw',
            'nw', 'nw', 'w', 'w', 'w','nw','nw', 'n', 'gate', 'e', 'n', 'n', 'n','w', 'n', 'chapel'
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
        self.smart_fort_path = ['areaid314', 'gate', 'n','n','w','s','store','out','s','e','e','n',"door", "door",
            'n','w','s','s']
        self.FORT_PATH = [
            'out','n','n', 'w','gate','n','n','n','n','n','gate','n','n','w','s','store','out','s','e','e','n',"door", "door",
            'n','w','s','s','gate', 's','s','s','s','s','gate','w','sw','s','s','s','e','e','e','e','n','w','n','chap'
        ]
        self.OLD_MAN_JAMES = ['areaid611', 'out', 'west', 'north', 'smithy']
        # self.GOOURD = [
        #     'areaid1899'
        # ]
        # self.MUGGER_PATH = ["areaid2",
        #     'ou','s','w','w','w','s','alley','w','alley','e','e','e','e','e','n','w','n','chap'
        # ]
        self.smart_northern_bandits_path = ['areaid421','south','s','s','n','n','n']
        self.NORTHERN_BANDITS_PATH = ["areaid2", 
            'out','n','n', 'w','gate','n','n','n','n','n','gate',
            'n','n','w','s','s','e','e','n','n','w','s','s','gate',
            's','s','s','s','s','gate','w','sw','s','s','s','e','e','e','e','n','w','n','chap'
        ]

        self.smart_dwarven_path = ['areaid1082', 'east', 'building', 'kitchen', 'out',
            'out', 'hall', 'out', 'east', 'east', 'forge', 'out', 'southeast', 'field', 'road', 'field 2', 'road', 'southeast',
            'southeast', 'field', 'road', 'southeast', 'field', 'stile', 'stile', 'road',
            'southeast', 'field', 'road', 'southeast', 'station']
        self.BORIS_IRONFOUNDER = ['areaid1087']
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
        
        self.SMART_MUGGER_PATH = [
            'areaid14','alley','w','alley','e','e'
        ]
        self.DWARVEN_FIELD_WORKERS_PATH = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','pathway','nw','n','n','n','se','e','e',
            'gate',
            'sty','out','stable','out', # nothing
            'e','e','w','building', # See Boris before going in to fight cooks etc.
            'kitchen','out', # dwarven cooks
            'out',
            'hall','out',#nothing
            'e','barn','out','s','n',#nothing
            'e','shed','out','hut','out','forge','out',# blacksmith 380 exp war hammer
            'se','field','road','field 2','road',
            'se','se','field','road','se',
            'field','stile','stile','road','se',
            'se','field','road',
            'se','station',
            'room','hall', # nothing
            'cellar','up','out','nw','nw','nw','nw','nw','nw','w','w','w','gate',
            'w','w','nw','s','s','s','se','s','w','w','w','nw','nw','n','gate',
            'e','n','n','n','w','n','chapel'
            # So this path seemed wrong
            # So I did a complete depth first path
            # Not sure if I should reorder the nodes... strongest 1st I suppose
            # Dwarven shephards are dangerous... (join in)
            # Brocolli won't care
            # I'm not sure if I used to do something sensitively here
            # This will be a test of the ready-for-combat checks
            # 'e','se','field','road','se','se','field','road','se',
            # 'sw','se','field','stile','stile','road',
            # 'nw','nw','nw','nw','w','w','w','gate','w','w','nw','s','s','s','se','s','w','w','w','nw','nw','n','gate',
            # 'e','n','n','n','w','n','chapel'
        ]
        self.MILL_WORKERS = [
            'out','s','e','s','s','s','w','gate','s','s','s','s','s','sw','s','se','sw','s','s','se','s','s','sw',
            'bridge','s','sw','w','canal','s','s','s','e','e','w','s','e','w','n','n','e','s','s','sw','out','w','n',
            'n','n','n','n','nw','ne','n','n','n','ne','ne','ne','ne','n','n','gate','e','n','n','n','w','n','chapel'
        ]#Contains lvl 2&3 mobs (stacker, furniture maker, sawmill operator, mill worker) and lvl 6 mobs (saw)?mill supervisor
        self.BANDITS1 = [ # Could be safer with secret exit
            'out','s','e','s','s','s','w','gate','s','s','sw','sw','sw','trail',
            'nw','nw','w','w','e','e','se','se','road',
            'ne','ne','ne','n','n','gate','e','n','n','n','w','n','chapel'
        ]
        self.BANDITS2 = self.BANDITS1 # second responders to alarm
        self.BANDITS3 = [
            'out','s','e','s','s','s','w','gate','s','s','sw','sw','sw','trail',
            'nw','nw','w','w','n','n','s','s','s','s','n','n',
            'e','e','se','se','road',
            'ne','ne','ne','n','n','gate','e','n','n','n','w','n','chapel']
        self.BANDITS4 = [
            'out','s','e','s','s','s','w','gate','s','s','sw','sw','sw','trail','nw','nw','w','w',
            'w','s','n','w','s','hut 3','out','hut','out','n','n','hut 2','out','s','hill',# cave level < 13
            'down','e','e','e','e','se','se','road',
            'ne','ne','ne','n','n','gate','e','n','n','n','w','n','chapel'
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
            'southeast', 'east', 'east', 'northeast', 'north', 'red tent', 'out', 'w','w','w','e','e','e', 's', 'w', 'w', 'w', 'e', 'e', 'e',
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

        self.LADY_DENLISE = ['areaid1079']
        self.LORD_TAMARAN = ['areaid1074']

        # self.GNOLL_CAMP = ['think']
        self.GNOLL_CAMP = [
            'areaid986', 'brush', 'west', 'west', 'south', 'southwest', 'southwest', 'tent', 'out', 'north', 'southeast',
            'southeast', 'out'
        ]
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

        self.MARTIN_MARIE = ['areaid11', 'try_arch', 'areaid4429', 'glamp', 'areaid4433', 'glamp']
        self.ZOMBIES = ['areaid113', 'try_gate',
        'east', 'east']
        #McDermotts farm
        if self.character.level >= 8:
            self.ZOMBIES += [
            'northeast', 'northeast', 'north', 'north', 'north', 'gate', 'north', 'east', 'east', 'southeast', 'east', 'southeast', 'southeast', 'southeast', 'trail', 'woods', 'deeper',
            'out', 'trail', 'field', 'path', 'northwest', 'northwest', 'west', 'northwest', 'west', 'west', 'south', 'gate', 'south', 'south', 'south', 'sw', 'sw']
        #Malbon farm
        self.ZOMBIES += [
        'southeast', 'southeast', 'south', 'gate', 'stile', 'northwest', 'southeast', 'southwest', 'northeast', 'stile', 'south', 'south',
        'north', 'north', 'gate', 'north', 'northwest', 'northwest',
        'ne', 'ne', 'east', 'east', 'east',
        #Calmor farmstop
        #'southeast', 'south', 'southeast', 'southeast', 'gate', 'southwest', 'sty', 'yard',
        'northeast', 'northeast']
        # if self.character.level >= 8:
        #     self.ZOMBIES += [
        #     #into zombie farm
        #     'northeast', 'north', 'northeast', 'north', 'gate', 'compound', 'west', 'barn', 'out', 'northwest', 'run', 'out', 'northeast', 'east', 'south', 'south',
        #     #out of zombie farm and into highmarket
        #     'path', 'gate', 'south', 'southwest', 'south', 'southwest', 'east', 'east', 'gate',
        #from highmarket back to chapel
        # 'south', 'southeast', 'southeast', 'south', 'east', 'gate', 'south', 'south', 'southeast', 'southeast', 'south', 'south',
        # 'south', 'southeast', 'south', 'west', 'west', 'west', 'northwest', 'northwest', 'north', 'gate', 'east', 'north', 'north',
        # 'north', 'west', 'north', 'chapel'
        # ]
        self.ZOMBIES += [
            'east', 'east', 'gate'
        ]
        #Farmer's gate / Dragon Road

        # self.BANDIT_CAMP = ['out', 'south', 'east', 'south', 'south', 'south', 'west', 'gate', 'south', 'south',
        # 'southwest', 'southwest', 'southwest', 'trail', 'northwest', 'northwest', 'west', 'west',
        # ]

        self.FOUNDRY = ['areaid1231', 'out', 'down', 'east', 'east', 'east', 'south']
        self.EGAN_TRENT = ['areaid1999']
        self.BARBS = ['areaid1421', 'west', 'out','nw','ne','tent','out','east','se','s','sw','w','nw','tent','out']
        self.ORCS = ['areaid747', 'areaid749']
        self.OLMER = ['areaid297']
        self.CHERYN = ['areaid1380']
        self.ARTIFICERS = ['areaid1350', 'areaid1008']
        self.HAELYN = ['areaid999'] #Haelyn
        self.ESRHAE = ['areaid2967'] #Esrhae
        self.SILKEN_ALLEY = ['areaid686', 'areaid706', 'areaid705', 'areaid698', 'areaid699', 'areaid700']
        self.QIMOTH = ['areaid686']
        self.GORBAN = ['areaid699']
        self.CORELLAN = ['areaid713']
        self.JERREK_TAG = ['areaid977', 'areaid979', 'areaid3857']
        self.MANIC_ELDER = ['areaid1899', 'areaid1465', 'areaid1491']
        self.VILADIN_CAL = ['areaid1498', 'areaid247', 'path', 'hut']
        self.DALLA_DOUVAN = ['areaid2449', 'areaid2430']
        self.ALDO_BROTAIN = ['areaid1254', 'areaid1226']
        self.HURN = ['areaid220']
        self.PLOVERS = ['areaid1564', 'areaid1600', 'door', 'east', 'east', 'door']
        self.FLOOR_MANAGER = ['areaid1147']
        self.TARDAN = ['areaid1378']
        self.RIMARK = ['areaid1231']
        # self.SHALDENA = ['areaid1621'] #she has really tough nukes
        self.HORBUK = ['areaid1265']
        self.DOJO = ['areaid917']
        self.HORSEMASTER = ['areaid2340'] #pathing sucks to/from here
        self.DINI = ['areaid629']
        self.BARDS1 = ['areaid1214'] #sonneteer 8 and minstrel 11
        self.MONKS1 = ['areaid1311', 'out', 'e', 'w', 'w', 's'] #brother 11, 2x seeker 5
        self.BLADEMASTER = ['areaid622', 'ne', 'e', 'se', 's', 's'] #warrior 8, 3x veteran 5
        self.GARBO = ['areaid2099']
        # self.WHITEBLADE_LYRON = ['areaid2110', 'areaid2097']
        # self.LYRON = ['areaid2097', ] # too much dmg

        self.GNOMES = ['areaid2113', 'areaid2099', 'areaid2104', 'areaid2106', 'areaid2138', 'areaid2138', 'areaid2093', 'areaid2094', 'areaid2095']
        self.FORGE_THIEVES = ['areaid1240', 'conveyor', 'east', 'plank', 'east', 'west', 'out', 'west', 'door']
        self.MASSIVE_SWAMP_TROLL = ["areaid2157"]
        self.MINOR_SWAMP_TROLLS = ["areaid3436", "n", "ne", "nw", "sw", "se"]
        self.BARBARIN_SHAMAN = ["areaid450"]
        self.KNIGHTS_TENT_CAMP = ["areaid1068", "glamp", "glamp", "glamp", "check_aura"]
        self.HOLY_SISTER_CAMP = ["areaid1363", "glamp", "glamp", "glamp", "check_aura"]
        self.GNOLL_SUB_CHIEF_CAMP = ["areaid2363", "glamp", "glamp", "glamp"]
        self.GNOLL_CHAPLAIN_CAMP = ["areaid1737", "glamp", "glamp", "glamp", "check_aura"]
        self.WAY_STATION_GLAMP = ["areaid1107", "glamp", "glamp", "glamp"]
        self.CHIARU = ["areaid3096"]
        self.WHITEBLADE = ["areaid2109"]
        self.MAYOR_DEMLIN = ["areaid19"]
        self.THOMAS_IRONHEART = ["areaid189"]
        self.MINERS = ['areaid1265', 'areaid1273', 'areaid1280', 'areaid1182', 'areaid1291', 'areaid1289', 'areaid1265']
        self.GOBLINS = ['areaid250', 'slow_prepare', 'areaid1615', 'north', 'camp', 'west', 'east', 'south', 'areaid2381', 'slow_prepare', 'up']
        self.HEF = ['areaid533', 'trail', 'areaid1678', 'door'] #'areaid2170', 'unlock panel key', 'panel', 'get all'
        self.AMBER_GUARDS = ['areaid575', 'areaid590', 'areaid552', 'areaid563', 'areaid585', 'areaid1338', 'areaid1359']
        self.REMISARA = ['areaid4338']
        self.MAYA = ['areaid4339']
        self.CHOORGA = ['areaid3440', 'areaid2389']

        self.FETCH_TIGER_EYE = ["has_item the head of Choorga", "areaid2097", "trade_item the head of Choorga to Lyron"]
        self.FETCH_RUSTY_KEY = ["has_item diamantium cross", "areaid2430", "trade_item diamantium cross to Douvan"]

        self.GRANITE_GOLEM = ["has_item tiger eye gem", "areaid3072", "invoke_item tiger eye gem",
          "north", "north", "north", "north", "glamp", "south","south","south","south","cubicle","ladder"
        ]

        self.PATH_TO_SKIP_WITH = ['think']

        self.setup_tracks()
        
        if isinstance(self.starting_path, int) and self.starting_path < len(self.tracks):
            self.__nextpath = self.starting_path
        else:
            self.__nextpath = 0#random.randrange(0, len(self.tracks))

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

    def do_glamp_actions(self):
        done_glamping = False
        self.do_regular_actions()
        if not self.ready_for_combat():
            done_glamping = True
        return done_glamping

    def check_for_item(self, input, pattern):
        M_obj = re.search(pattern, input)

        # magentaprint("M_obj: " + str(M_obj), False)
        # magentaprint("checking for item: <" + str(M_obj.group(1)) + ">", False)
        # magentaprint("checking for target: <" + str(M_obj.group(2)) + ">", False)

        if M_obj and M_obj.group(1):
            item = M_obj.group(1)
            # magentaprint("M_obj: " + str(M_obj), False)
            # magentaprint("checking for item: <" + item + ">", False)

            if self.character.inventory.has(item):
                return True, item, M_obj

        return False, "", M_obj

    def do_go_hooks(self, exit_str):
        # magentaprint(str(self.character.AREA_ID) + ", " + exit_str, False)
        if exit_str == "raise":
            raise Exception("Manual exception to crash the bot raised!!!")
        elif exit_str == "slow_prepare":
            magentaprint("prearing to move to trapped area", False)
            self.sleep(2)
            self.command_handler.process("prepare")
            self.sleep(2)
            magentaprint("waiting after prepare to take a breath", False)
            return True
        elif exit_str.startswith("try_"):
            exitCommand = exit_str.replace("try_", "")
            curArea = int(self.character.AREA_ID)
            self.command_handler.process("go " + exitCommand)
            self.sleep(3)
            if (curArea == int(self.character.AREA_ID)):
                magentaprint("failed to go through the " + exitCommand + " probably", False)
                self.direction_list = ['areaid2']
            return True
        elif exit_str == "check_aura":
            magentaprint("checking aura, run kills: " + str(self.run_kills), False)
            # check kills since last aura check - if <5 then don't bother
            magentaprint("kills since last aura check: " + str(self.run_kills - self.last_aura_refresh_kills), False)
            if self.run_kills > self.last_aura_refresh_kills:
                self.update_aura(force=True)
            return True
        elif exit_str == "glamp":
            magentaprint("glamping for 20 seconds...", False)
            # camp for 20 seconds
            self.persistently_take_action(self.do_glamp_actions)
            
            return True
        elif exit_str == "think":
            return True
        elif exit_str == "tap":
            magentaprint("waiting for mob to engage us", False)
            self.persistently_take_action(self.do_regular_actions, 10)
            magentaprint("tap function completed", False)
            return True
        elif exit_str == "sell_items":
            # if we're in the pawn shop then sell stuff
            # check the current area - is it a pawn shop? If not then path to the pawn shop

            if self.character.MUD_AREA.area.is_pawn_shop:
                self.sell_items()
            else:
                self.direction_list = ["think", "areaid130", "sell_items", "areaid266", "drop_items"] # pawn shop

            return True
        elif exit_str == "drop_items":

            if self.character.MUD_AREA.area.is_tip:
                self.drop_items()
            else:
                self.direction_list = ["think", "areaid266", "drop_items"] # tip

            return True
        # if "has <pattern>" in exit_str:
        elif exit_str.startswith("has_item "):
            has_item, item_name, M_obj = self.check_for_item(exit_str, "has_item (.+)")
            if has_item:
                magentaprint("has <" + item_name + ">, continuing track", False)
                return True
            else:
                magentaprint("no <" + item_name + ">, continuing track", False)
                self.direction_list = []
                return True

        elif exit_str.startswith("invoke_item "):
            has_item, item_name, M_obj = self.check_for_item(exit_str, "invoke_item (.+)")
            if has_item:
                # magentaprint("has <" + item_name + ">, invoking", False)
                item_ref = self.character.inventory.get_first_reference(item_name)
                self.command_handler.process("invoke " + str(item_ref))
                time.sleep(1)
                self.character.inventory.get_inventory()
                return True
            else:
                magentaprint("no <" + str(item_name) + ">, this shouldn't be happening", False)
                self.direction_list = []
                return True

        elif exit_str.startswith("trade_item "):
            has_item, item_name, M_obj = self.check_for_item(exit_str, "trade_item (.+?) to (.+)")

            # magentaprint("has_item: " + str(has_item), False)
            # magentaprint("trade_item: " + item_name, False)
            # magentaprint("target: " + str(M_obj.group(1)), False)
            # magentaprint("target: " + str(M_obj.group(2)), False)
            if has_item:
                # magentaprint("has <" + item_name + ">, trading", False)
                item_ref = self.character.inventory.get_first_reference(item_name)
                mob_ref = M_obj.group(2).split(' ')[0]
                self.command_handler.process("trade " + str(item_ref) + " " + str(mob_ref))
                time.sleep(1)
                self.character.inventory.get_inventory()
                return True
            else:
                magentaprint("no <" + str(item_name) + ">, this shouldn't be happening", False)
                self.direction_list = []
                return True
        else:
            return super().do_go_hooks(exit_str)

    def do_pre_go_actions(self):
        self.rest_and_check_aura()
        self.check_weapons()
        self.check_armour()

        # if self.has_buff_ability():
        #     if self.use_buff_ability():
        #         self.use_extra_buff_items()
        # else:
        #     pass
            # Need a timer for this...
            # self.use_extra_buff_items()

    def has_buff_ability(self):
        return len(self.character._class.buff_skills) > 0

    def use_extra_buff_items(self):
        self.use_extra_bless_item()
        self.use_extra_steel_bottle()

    def aura_updated_hook(self):
        # too evil
        if self.character.AURA < self.character.preferred_aura:
            self.tracks.sort(key=lambda x: x.track_aura)
        # too good
        elif self.character.AURA > self.character.preferred_aura:
            self.tracks.sort(key=lambda x: x.track_aura, reverse=True)
        # just right
        else:
            self.tracks.sort(key=lambda x: (x.min_level - abs(x.track_aura)), reverse=True)
        
        magentaprint("aura updated hook", False)
        magentaprint("tracks: " + str(self.tracks), False)
        self.abandoned_last_track = False
        self.skipped_last_track = False

        # restart the paths
        self.__nextpath = 0

    def setup_tracks(self):
        self.tracks = [
            Track("Shop and Tip 0",self.SHOP_AND_TIP_PATH,0,20,9, has_cooldown=False),
            Track("Check Aura",["check_aura"],0,20,9, has_cooldown=False),
            # Aura intensive stuff all up front
            Track("Gorban", self.GORBAN, 17, 20, 0, requires_ready=True, target_kills=1, mob_name="Gorban"),
            Track("Silken Alley", self.SILKEN_ALLEY, 11, 17, 0, requires_ready=True),
            Track("Lady Denlise", self.LADY_DENLISE, 17, 20, 1, True, 7, 18, target_kills=1, mob_name="Lady Denlise"),
            Track("Lord Tamaran", self.LORD_TAMARAN, 17, 20, 1, True, 7, 18, True, target_kills=1, mob_name="Lord Tamaran"),
            Track("Cathedral", self.CATHEDRAL, 10, 20, 1, True, 7, 18, skip_if_ready=True),
            Track("Holy Sister Aura Fix", self.HOLY_SISTER_CAMP, 12, 20, 2, False, 7, 18, is_glamping=True, skip_if_ready=True),
            # grey and minor aura tracks
            Track("Theatre Farm", self.smart_theatre_path, 0, 14, 0, has_cooldown=False),
            Track("Theatre Bertram", self.BERTRAM, 14, 17, 0, target_kills=1, skip_if_ready=True),
            Track("Market", self.smart_market_path, 0, 15, 0, has_cooldown=False),
            Track("Militia Soldiers", self.smart_militia_path, 0, 14, 0, has_cooldown=False),
            Track("Kobolds", self.smart_kobold_path, 0, 9, -1, has_cooldown=False), #sentries are suuuper tough
            Track("Kobolds", self.kobold_massacre, 10, 17, -2, has_cooldown=False), #sentries are suuuper tough
            #Track("Coral Alley", self.CORAL_ALLEY_PATH, 0, 6, -1),
            Track("Fort Farm", self.smart_fort_path, 9, 14, 0, has_cooldown=False, requires_ready=False),
            Track("Fort Commander", ["areaid850"], 14, 16, 0, requires_ready=True, target_kills=1, mob_name="Commander Rilmenson"),
            Track("Veterans", self.BLADEMASTER, 8, 12, 0, has_cooldown=False),
            Track("North Bandits", self.smart_northern_bandits_path, 9, 14, -1, has_cooldown=False),
            # Track("Eastern Zombies Farm", self.ZOMBIES, 6, 12, 0, has_cooldown=False),
            # Track("Eastern Farmers", self.ZOMBIES, 13, 16, 0, requires_ready=True),
            # Track("Shop and Tip 1",self.SHOP_AND_TIP_PATH, 0, 20, 9),
            Track("Dwarven Field Workers", self.smart_dwarven_path, 9, 15, 0, has_cooldown=False),
            Track("Miners", self.MINERS, 10, 16, 0, has_cooldown=False),
            Track("Boris Ironfounder", self.BORIS_IRONFOUNDER, 15, 17, 0, requires_ready=True, target_kills=1, allows_caster=False, mob_name="Boris Ironfounder"),
            Track("Mill Workers", self.smart_mill_path, 7, 14, 0, has_cooldown=False),
            Track("Muggers", self.SMART_MUGGER_PATH, 9, 15, -1, has_cooldown=False),
            Track("Old Man James", self.OLD_MAN_JAMES, 9, 12, 0, target_kills=1),
            Track("Olmer", self.OLMER, 11, 14, -1),
            Track("Cheryn", self.CHERYN, 11, 20, -1, requires_ready=False, target_kills=1),
            Track("Orcs", self.ORCS, 11, 16, -1),
            Track("Artificers", self.ARTIFICERS, 11, 14, -1),
            # Haelyn is dusty blue but we want to priorize him for farming purposes
            Track("Haelyn", self.HAELYN, 16, 20, 0, requires_ready=True, target_kills=1, allows_caster=False, mob_name="Haelyn"),
            Track("Esrhae", self.ESRHAE, 18, 20, 0, requires_ready=True, target_kills=1, allows_caster=False, mob_name="Esrhae"),
            Track("Foundry", self.FOUNDRY, 16, 20, 0), #Rimark joins in, not enough mobs actually are there by default
            Track("Rancher Sentries", self.smart_rancher_path, 12, 15, 1, has_cooldown=False),
            Track("Large Spider Forest", self.SPIDER_FOREST, 12, 15, -1, has_cooldown=False),
            Track("Trent", self.EGAN_TRENT, 12, 17, -1, requires_ready=False, target_kills=1, mob_name="Trent the Merchant"),
            Track("Combat Master / barbs", self.BARBS, 8, 14, 0),
            Track("Tardan", self.TARDAN, 15, 17, 0, requires_ready=True, target_kills=1, mob_name="Tardan"),
            Track("Hurn", self.HURN, 15, 17, 1, requires_ready=True, target_kills=1, mob_name="Hurn the Smith"),
            Track("Rimark", self.RIMARK, 15, 17, 1, requires_ready=True, target_kills=1, mob_name="Rimark"),
            Track("Dojo", self.DOJO, 16, 20, 1, requires_ready=True, target_kills=1, mob_name="Dojo Administrator"),
            Track("HORSEMASTER", self.HORSEMASTER, 17, 20, 1, requires_ready=True, target_kills=1, mob_name="Th'kit the HorseMaster"),
            Track("Dini", self.DINI, 11, 15, 0, target_kills=1),
            Track("Horbuk", self.HORBUK, 15, 17, 1, requires_ready=True, target_kills=1, mob_name="Horbuk"),
            # Track("Shaldena the Red", self.SHALDENA, 15, 20, 1),
            # Track("Shop and Tip 2",self.SHOP_AND_TIP_PATH,8,20,9, has_cooldown=False),
            # Track("Corellan", self.CORELLAN, 16, 20, 0),
            Track("Jerrek and Tag", self.JERREK_TAG, 11, 17, -1, requires_ready=True, target_kills=1, mob_name="Jerrek"),
            # Track("Jerrek and Tag", self.JERREK_TAG, 16, 20, -1, target_kills=1),
            Track("Gnomes", self.GNOMES, 10, 12, 1, has_cooldown=False),
            Track("Garbo", self.GARBO, 13, 15, 1, target_kills=1),
            Track("Goourd, Manic and Elder", self.MANIC_ELDER, 10, 17, 0, requires_ready=False, target_kills=1),
            Track("Goourd, Manic and Elder", self.MANIC_ELDER, 17, 20, 0, requires_ready=True, target_kills=1, mob_name="Manic Soothsayer"),
            Track("Viladin and Cal", self.VILADIN_CAL, 12, 17, 1, requires_ready=True, target_kills=1, mob_name="Cal the Hermit"),
            Track("Plovers", self.PLOVERS, 15, 17, 1, requires_ready=True, target_kills=1, mob_name="Annette Plover"),
            # Track("Bards", self.BARDS1, 11, 16, 1, requires_ready=True), #minstrels are a hazard
            Track("Brother monk", self.MONKS1, 9, 17, 0, requires_ready=True),
            Track("Floor Manager", self.FLOOR_MANAGER, 12, 17, -1, requires_ready=True, target_kills=1, mob_name="Floor Manager"),
            # Track("Dalla and Douvan", self.DALLA_DOUVAN, 11, 20, 1), # Dalla overheals and is too dangerous
            Track("Aldo and Brotain", self.ALDO_BROTAIN, 11, 17, 1, requires_ready=True, target_kills=1),
            # Track("Halwyn Bugbears",) # has a pit which could cause issues
            # Track("Forge / weapon thieves",self.FORGE_THIEVES,14,20,-1),
            Track("Minor swamp trolls", self.MINOR_SWAMP_TROLLS, 15, 20, -1, False, 0, 9, skip_if_ready=True, mob_name="swamp troll", allows_caster=False), # too aggressive and multiple spawn
            Track("Massive swamp troll", self.MASSIVE_SWAMP_TROLL, 15, 17, -1, requires_ready=True, target_kills=1, mob_name="massive swamp troll"),
            # Track("Shop and Tip 3",self.SHOP_AND_TIP_PATH,10,20, 9,has_cooldown=False),
            # Track("Barbarian shaman", self.BARBARIN_SHAMAN, 15, 20, 0), # some pretty big nuke spells, maybe not worth it
            Track("WAY_STATION_GLAMP", self.WAY_STATION_GLAMP, 10, 14, 0, False, is_glamping=True),
            # Track("CHIARU", self.CHIARU, 18, 20, 1, requires_ready=True, target_kills=1), # causes granite usage
            # Track("THOMAS_IRONHEART", self.THOMAS_IRONHEART, 18, 20, 0, requires_ready=True, target_kills=1), # causes granite usage
            # Track("Hef the Bandit Chief", self.HEF, 12, 13, -1, allows_caster=False),
            Track("Gnoll Camp", self.GNOLL_CAMP, 15, 20, -1, False, 0, 9, skip_if_ready=True),
            Track("Gnoll Cave", self.smart_gnoll_cave, 10, 20, -1, False, 0, 9, skip_if_ready=True),
            Track("Knights Aura Fix", self.KNIGHTS_TENT_CAMP, 15, 20, 2, False, 7, 18, is_glamping=True, skip_if_ready=True),
            Track("Gnoll Chaplain Aura Fix", self.GNOLL_CHAPLAIN_CAMP, 15, 20, -2, False, 0, 9, is_glamping=True, skip_if_ready=True),
            Track("Goblins", self.GOBLINS, 16, 20, -2, False, 0, 9, requires_ready=False, allows_caster=False),
            Track("Amber Guards", self.AMBER_GUARDS, 15, 20, 1, has_cooldown=False, skip_if_ready=True),
            Track("Knights", self.smart_knights_path, 7, 20, 1, False, 7, 18, skip_if_ready=True),
            # Track("CHOORGA", self.CHOORGA, 18, 20, 0, requires_ready=True, has_cooldown=False, mob_name="Choorga the swamp troll"),
            Track("Head trade",self.FETCH_TIGER_EYE, 18, 20, 0, has_cooldown=True, mob_name="", cooldown=600),
            Track("Granite Golem",self.GRANITE_GOLEM, 18, 20, 0, has_cooldown=True, target_kills=1, cooldown=8000, mob_name="granite golem", prime_cooldown=True),
            Track("Qimoth", self.QIMOTH, 18, 20, 0, requires_ready=True, target_kills=1, mob_name="Qimoth"),
            Track("WHITEBLADE", self.WHITEBLADE, 17, 20, 0, requires_ready=True, target_kills=1, mob_name="Whiteblade the Barbarian"), # meh?
            Track("MAYOR_DEMLIN", self.MAYOR_DEMLIN, 18, 20, 0, requires_ready=True, target_kills=1, mob_name="Mayor Demlin"),
            Track("Egan", self.EGAN_TRENT, 18, 20, 0, requires_ready=True, target_kills=1, mob_name="Teamleader Egan"),
            Track("REMISARA", self.REMISARA, 18, 20, 1, requires_ready=True, target_kills=1, mob_name="Remisara"), # doesn't seem to have drops
            Track("Maya", self.MAYA, 18, 20, 1, requires_ready=True, target_kills=1, mob_name="Maya"),
            Track("MARTIN", self.MARTIN_MARIE, 14, 20, 0, True, requires_ready=False, mob_name="Martin"),
            Track("MARIE", self.MARTIN_MARIE, 14, 20, 0, True, requires_ready=False, mob_name="Marie"),
        ]
        
        # self.tracks = []
        # self.tracks = [Track("Granite Golem",self.GRANITE_GOLEM,18,20,0, has_cooldown=True, cooldown=8000, mob_name="granite golem", prime_cooldown=True),]

        # self.tracks = [Track("WAY_STATION_GLAMP", self.WAY_STATION_GLAMP, 10, 14, 0, False, is_glamping=True)]

        self.tracks = [x for x in self.tracks if self.character.level >= x.min_level and self.character.level < x.max_level]
        # sort the list of tracks by track_aura
        # track 0 is preferred so these should be first followed by -1 or 1 respectively
        self.tracks.sort(key=lambda x: abs(x.track_aura))
        
    def remove_tracks_outside_of_level_range(self):
        self.tracks = [x for x in self.tracks if self.character.level >= x.min_level and self.character.level < x.max_level]

    def decide_where_to_go(self):
        magentaprint("Inside decide_where_to_go", False)

        # if self.character.AREA_ID != 2:
        #     return ["areaid2"]

        magentaprint("next path = " + str(self.__nextpath), False)

        if self.character.DEAD:
            self.character.DEAD = False
            self.character.DEATHS += 1
            # magentaprint("Died: Pulling up my bootstraps and starting again", False)
            magentaprint("Died: stopping bot thread.", False)
            self.stop()
            return self.LIMBO_TO_CHAPEL[:]

        if self.character.NEEDS_TO_SELL:
            magentaprint("Character needs to sell - going to sell path", False)
            self.character.NEEDS_TO_SELL = False
            self.character.MONSTER_KILL_LIST = []
            return self.SHOP_AND_TIP_PATH[:]
        # else:
        #     magentaprint("Character doesn't need to sell", False)

        nextpath = None
        # removed abandoned_last_track check here
        # if self.last_track is not None and not self.skipped_last_track and self.abandoned_last_track and not self.last_track.is_glamping:
        #     magentaprint(f"abandoned last track ({str(self.abandoned_last_track)}) so we're re-running it", False)
        #     nextpath = self.evaluate_track(self.last_track)
        # else:
        #     # self.__nextpath = (self.__nextpath + 1) % len(self.tracks)
        nextpath = self.evaluate_track(self.tracks[self.__nextpath])
    
        self.abandoned_last_track = False

        return nextpath

    def evaluate_track(self, track):
        self.reset_kill_list()
        self.skipped_last_track = False
        level_range = range(track.min_level, track.max_level)

        character_aura = Aura(self.character.AURA)
        aura_acceptable = character_aura == self.character.preferred_aura

        # caster classes can run out of mana and then have a bad time since their main source of DPS is gone
        # alternatively these paths could have a lot of loot that casters cannot carry and that will leave items on the ground
        if not track.allows_caster and self.character._class.is_caster():
            magentaprint("{0} isn't acceptable to us due to caster class restriction".format(track.name), False)
            return self.skip_track()

        if track.requires_ready:
            if not aura_acceptable:
                magentaprint("{0} isn't acceptable to us due to aura".format(track.name), False)
                return self.skip_track()

            # if (track.mob_target is None or not self.is_mob_weak(track.mob_target, 4)) and 
            if not self.character.is_ready_for_tough_fight() and track.mob_target is not None:
                magentaprint("{0} isn't acceptable due to tough fight function".format(track.name), False)
                return self.skip_track()
            
            if track.mob_target is not None:
                if not self.is_mob_weak(track.mob_target, 5):
                    if not self.character.is_ready_for_tough_fight():
                        magentaprint("{0} isn't acceptable due to tough fight for specific mob {1}".format(track.name, track.mob_target.name), False)
                        return self.skip_track()

        # optimization for level 18s so they don't waste time on tracks that are too easy
        if track.skip_if_ready and self.character.info.level == 18:
            if self.character.is_ready_for_tough_fight() and aura_acceptable:
                return self.skip_track()

        if track.track_aura == 9:
            if self.character.level in level_range:
                self.__nextpath = (self.__nextpath + 1) % len(self.tracks)
                return track.track[:]
            else:
                return self.skip_track()

        # if the track has a cooldown and the last run was less than 15 minutes ago, skip it
        if track.last_run != 0:
            current_time = get_timeint()
            # seconds_since_last_run = (current_time - current_time).total_seconds()
            seconds_since_last_run = (current_time - get_timeint_from_int(track.last_run)).total_seconds()
            if track.has_cooldown and seconds_since_last_run < track.cooldown:
                magentaprint("{0} isn't acceptable to us due to cooldown".format(track.name), False)
                magentaprint("seconds since last run: " + str(seconds_since_last_run), False)
                magentaprint("cooldown: " + str(track.cooldown), False)
                return self.skip_track()
        # aura correction here is maybe more valuable than short term efficiency - seeing a lot of bots dangling near their incorrect aura
        # elif track.is_glamping and self.abandoned_last_track:
        #     magentaprint("{0} is a camping track so we won't re-run".format(track.name), False)
        #     return self.PATH_TO_SKIP_WITH[:]
        # else:
        #     magentaprint("{0} is acceptable to us due to cooldown > {1} and has_cooldown {2}".format(track.name, seconds_since_last_run, track.has_cooldown), False)

        if character_aura < track.min_aura or character_aura > track.max_aura:
            magentaprint("Character too good or evil for this track", False)
            return self.skip_track()

        #too evil shouldn't fight good (+1)
        #too good shouldn't fight evil (-1)
        # if (not aura_acceptable and track.track_aura == 0) or \
        if (character_aura < self.character.preferred_aura and track.track_aura == 1) or \
           (character_aura <= self.character.preferred_aura and track.track_aura == 2) or \
           (character_aura > self.character.preferred_aura and track.track_aura == -1) or \
           (character_aura >= self.character.preferred_aura and track.track_aura == -2):
            magentaprint("{0} unacceptable due to aura".format(track.name), False)
            return self.skip_track()

        if self.character.level in level_range:
            if self.character.current_track is not None:
                self.end_track()
            magentaprint("{0} is our chosen track".format(track.name), False)
            self.start_track(track)
            self.__nextpath = (self.__nextpath + 1) % len(self.tracks)
            if track.mob_target is not None:
                # set mob_target as the main kill list mob if we would kill it normally
                if track.mob_target.name in self.character.MONSTER_KILL_LIST:            
                    self.character.MONSTER_KILL_LIST = [track.mob_target.name]
            return track.track[:]
        else:
            magentaprint("{0} isn't acceptable to us due to level".format(track.name), False)
            # self.__nextpath = self.__nextpath + 1 #skips the next path
            return self.skip_track()

    def skip_track(self):
        self.abandoned_last_track = False
        self.skipped_last_track = True
        self.__nextpath = (self.__nextpath + 1) % len(self.tracks)
        return self.PATH_TO_SKIP_WITH[:]

    def start_track(self, track):
        self.track_start_time = get_timeint()
        track.start()
        self.character.start_track(track)
        self.last_track = track
        self.last_track_kills = getattr(track, "kills")
        self.on_track = True

    def reset_kill_list(self):
        pass

    def end_track(self):
        if self.last_track is not None:
            self.track_end_time = get_timeint()
            track_time = (self.track_end_time - self.track_start_time).total_seconds()
            self.character.TRACK_TIME += track_time
            self.character.add_to_track_param('completes', 1)
            self.character.add_to_track_param('duration', track_time)
            net_kills = getattr(self.last_track, "kills") - self.last_track_kills
            self.character.end_track()
            self.on_track = False
            magentaprint("ending track [{}] with {} kills".format(getattr(self.last_track, "name"), net_kills), False)
            self.run_kills += net_kills

            if net_kills >= self.last_track.target_kills:
                magentaprint("We done good so no need to go back", False)
                self.abandoned_last_track = False

            # if our net_kills > 0 then maybe unset track abandon?

    def stop(self):
        self.last_track = None
        super().stop()

    def get_path_to_previous_node(self, name):
        chapel_aid  = db.Area.Area.get_by_name("The Chapel of Healing").id
        # mob_aid     = db.MobLocation.MobLocation.get_locations_by_exact_mob_name(name)[0].area.id
        mob_locations = db.MobLocation.MobLocation.get_locations_by_exact_mob_name(name)
        paths = [self.mud_map.get_path(chapel_aid, mob_location.area.id) for mob_location in mob_locations]
        lengths = [len(p) for p in paths]
        # index = min([len(p) for p in paths])
        index_min = min(range(len(lengths)), key=lengths.__getitem__) # https://stackoverflow.com/questions/2474015/
        mob_aid = mob_locations[index_min].area.id
        magentaprint("TrackGrindThread get_path_to_and_from_mob chapel_aid {0} mob_aid {1}".format(chapel_aid,mob_aid))
        return self.mud_map.get_path(chapel_aid, mob_aid)[:-1] + self.mud_map.get_path(mob_aid, chapel_aid)[1:]
        # That does assume the return path is similar

    def get_specific_path_to_and_from_mob(self, name, index):
        #return ['areaid{0}'.format(MobLocation.get_locations_by_exact_mob_name(name)),
        # package.file.class.function
        chapel_aid    = db.Area.Area.get_by_name("The Chapel of Healing").id
        mob_aid     = db.MobLocation.MobLocation.get_locations_by_exact_mob_name(name)[index].area.id
        # mob_locations = db.MobLocation.MobLocation.get_locations_by_exact_mob_name(name)
        # paths = [self.mud_map.get_path(chapel_aid, mob_location.area.id) for mob_location in mob_locations]
        # lengths = [len(p) for p in paths]
        # index = min([len(p) for p in paths])
        # index_min = min(range(len(lengths)), key=lengths.__getitem__) # https://stackoverflow.com/questions/2474015/
        # mob_aid = mob_locations[index_min].area.id
        magentaprint("TrackGrindThread get_path_to_and_from_mob chapel_aid {0} mob_aid {1}".format(chapel_aid,mob_aid))
        return self.mud_map.get_path(chapel_aid, mob_aid) + self.mud_map.get_path(mob_aid, chapel_aid)

    def get_path_to_and_from_mob(self, name):
        #return ['areaid{0}'.format(MobLocation.get_locations_by_exact_mob_name(name)),
        # package.file.class.function
        chapel_aid    = db.Area.Area.get_by_name("The Chapel of Healing").id
        # mob_aid     = db.MobLocation.MobLocation.get_locations_by_exact_mob_name(name)[0].area.id
        mob_locations = db.MobLocation.MobLocation.get_locations_by_exact_mob_name(name)
        paths = [self.mud_map.get_path(chapel_aid, mob_location.area.id) for mob_location in mob_locations]
        lengths = [len(p) for p in paths]
        # index = min([len(p) for p in paths])
        index_min = min(range(len(lengths)), key=lengths.__getitem__) # https://stackoverflow.com/questions/2474015/
        mob_aid = mob_locations[index_min].area.id
        magentaprint("TrackGrindThread get_path_to_and_from_mob chapel_aid {0} mob_aid {1}".format(chapel_aid,mob_aid))
        return self.mud_map.get_path(chapel_aid, mob_aid) + self.mud_map.get_path(mob_aid, chapel_aid)
    
    def get_path_with_all_mobs(self, name):
        chapel_aid = db.Area.Area.get_by_name("The Chapel of Healing").id
        P = self.path_through_areas(
            [chapel_aid]+
            [ML.area.id for ML in db.MobLocation.MobLocation.get_locations_by_exact_mob_name(name)]+
            [chapel_aid])
        return P

    def path_through_areas(self, area_ids):
        path = []
        for i in range(1,len(area_ids)):
            path += self.mud_map.get_path(area_ids[i-1], area_ids[i])
        return path

class Track():
    def __init__(self, name, track, min_level, max_level, track_aura, has_cooldown=True,
                min_aura=0, max_aura=18, requires_ready=False, is_glamping=False, target_kills=99,
                allows_caster=True, mob_name="", skip_if_ready=False, cooldown=4000, prime_cooldown=False):
        self.name = name
        # setup the track with a buffer at the end so that last node mobs don't get misattributed to the next track
        track.append("think")
        self.track = track
        self.last_run = 0
        if prime_cooldown:
            self.last_run = int(round(get_timeint().timestamp()))
        self.min_level = min_level
        self.max_level = max_level
        self.track_aura = track_aura
        self.runs = 0
        self.abandons = 0
        self.completes = 0
        self.kills = 0
        self.exp = 0
        self.duration = 0
        self.min_aura = min_aura
        self.max_aura = max_aura
        self.has_cooldown = has_cooldown
        self.cooldown = cooldown
        self.requires_ready = requires_ready
        self.is_glamping = is_glamping
        self.target_kills = target_kills
        self.allows_caster = allows_caster
        self.skip_if_ready = skip_if_ready

        mob_target = None
        if mob_name != "":
            mob_target = Mob(name=mob_name)
            mob_target.map()

        self.mob_target = mob_target
    
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

    def to_string(self):
        return self.name + ", " + str(self.min_level) + " -> " + str(self.max_level) + ", " + str(self.track_aura) + ";"

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

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
