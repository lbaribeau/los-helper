
from bots.GrindThread import GrindThread
from misc_functions import magentaprint
from Aura import Aura
import db.Area

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
        elif self.character.level <= 10:
            self.__TOTALPATHS = 22
        else:
            # self.__TOTALPATHS = 28  # # Area ids unfortunately must be updated.
            #self.__TOTALPATHS = 30
            # self.__TOTALPATHS = 52 # Added some graph pathing
            self.__TOTALPATHS = 48 # Added some graph pathing
        # elif self.character.level <= 10:
        #     self.__TOTALPATHS = 20 # start the fort and bandits at lvl 8
        # elif self.character.level > 12:
        #     self.__TOTALPATHS = 24
        # else:
        #     self.__TOTALPATHS = 22 # start the fort and bandits at lvl 8

        if isinstance(starting_path, int) and starting_path < self.__TOTALPATHS:
            self.__nextpath = starting_path
        else:
            self.__nextpath = 0

        self.LIMBO_TO_CHAPEL = [
            'ame','out','w','n','chapel'
        ]

        self.SHOP_AND_TIP_PATH = [
            'out','s','w','w','w','s','s','shop','sell_items','out','se','e','e','e','e','ne','tip','drop_items',
            'out','n','n','w','w','w','n','chapel'
        ]
        self.THEATRE_PATH = [
            'out','s','w','w','w','s','theat','stairs','cubby','out','down','swing','seat','out','down','seat','out',
            'door','stage','side 2','backstage','door','out','curtain','stage','side','door','up','out','out','n','e',
            'e','e','n','chapel'
        ]
        self.MARKET_PATH = [
            'out','s','e','e','e','n','w','w','office','out','n','n','s','w','e','s','w','s','n','w','e','n','s','e',
            'e','out','s', 'w', 'w', 'w', 'n','chapel'
        ]
        self.MILITIA_SOLDIERS_PATH = [
            'out','s','e','s','s','s','w','gate','s','s','sw','sw','sw','sw','s','s','s','sw','se','s','s','s','s',
            's','s','s','s','s','w',
            'doo','stor','ou','ou',
            'w','w','w','n','n','s','s','e','e','e','e','n','n','e',
            'e','e','e','e','e','e','e','e','ne','e','ne','ne','ne','ne','ne','ne','n','n','w','s','sw','ne','n','e',
            'n','n','n','n','n','n','n','n','n','n','nw','nw','nw','path','nw','n','n','n','nw','nw','n','n','gate',
            'w','n','nw','nw','n','e','e','e','s','s','s','s','gate','s','s','se','se','s','s','s','se','s','w','w',
            'w','nw','nw','n','gate','e','n','n','n','w','n','chapel'
        ]
        self.KOBOLD_PATH = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','se','se','se','s','s','s','s','s','e','e',
            'se','e','s','s','s','s','glowing portal','passage','mines','down','n','n','n','n','ne','n','w','n','n',
            'e','door','w','gully','up','boulder','up','cave 3','ne','ne','n','s','up','e','se','cave','out',
            # Note: You can remove the following line of code to remove the kobold guards and priests fights.
            # Priests turn you very blue.  These fights may be difficult.
            # Also useful to test mobs who join in.
            # They're commented because kobolds are allowed when you're pale blue, which is one off of blue... and these guards
            # and priests are dangerous unless the bot decides on his own to engage.  Todo: check aura here (if health is
            # high enough,) and go in if all's good.  Even fight the priests - because the more 'good' we can get the
            # more chalices we can farm.
            # ()
            #'prepare', 'e', 'ne', 'door', 'door', 'prepare', 'sw','w',
            'ladder','cave','out','sw','w',
            # 'cave', 'out',  # Comment out insane kobold (TODO: check level here)
            'sw','se','nw','w','out','down','boulder','down','down','e','door','w','s','s','e','s','sw','s','s','s',
            's','gully','glowing portal','passage','coral','n','n','n','n','w','nw','w','w','n','n','n','n','n','nw',
            'nw', 'nw', 'w', 'w', 'w','nw','nw', 'n', 'gate', 'e', 'n', 'n', 'n','w', 'n', 'chapel'
        ]
        self.CORAL_ALLEY_PATH = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','se','se','se','s','s','s','s','w','alley',
            's','s','door','stairs', #angry hooker should be avoided unless lvl 5.
            #'do 3', 'ou',
            'stairs','out','s',
            #'w','e', #for zombies
            # noticed drunken troublemakers arrive one east
            # red axer lvl 2 dropped studded leather collar
            'n','n','n','n','e','n','n','n','n','nw','nw','nw','w','w','w','nw','nw','n','gate','e','n','n','n','w',
            'n','chapel'
        ]
        self.FORT_PATH = [
            'out','n','n', 'w','gate','n','n','n','n','n','gate','n','n','w','s','s','e','e','n','n','w','s','s','gate',
            's','s','s','s','s','gate','w','sw','s','s','s','e','e','e','e','n','w','n','chap'
        ]
        self.MUGGER_PATH = [
            'ou','s','w','w','w','s','alley','w','alley','e','e','e','e','e','n','w','n','chap'
        ]
        self.NORTHERN_BANDITS_PATH = [
            'out','n','n','w','gate','n','n','n','n','n','gate','n','n','gate','n','nw','nw','sw','sw','sw','sw','s',
            'sw','sw','w','w','sw','sw','sw','sw','sw','sw','w','w','w','w','nw','w','w','nw','sw','nw','w','w','w',
            'nw','w','w','w','w','s','s','s','n','n','n','e','e','e','e','se','e','e','e','se','ne','se','e','e','se',
            'e','e','e','e','ne','ne','ne','ne','ne','ne','e','e','ne','ne','n','ne','ne','ne','ne','se','se','s',
            'gate','s','w','e','s','gate','s','s','s','s','s','gate','e','s','s','chapel'
        ]
        self.DWARVEN_FIELD_WORKERS_PATH = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','pathway','nw','n','n','n','se','e','e',
            'gate','e','building','out','e','e','se','field','road','se','sw','se','field','stile','stile','road',
            'nw','nw','nw','nw','w','w','w','gate','w','w','nw','s','s','s','se','s','w','w','w','nw','nw','n','gate',
            'e','n','n','n','w','n','chapel'
        ]
        #both gates close at night unforunately...
        self.FIELD_WORKERS_PATH = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','pathway','nw','n','n','n','nw','nw','n',
            'n','gate','w','n','nw','nw','n','gate','w','w','sw','sw','w','w','w','sw','sw','se','se','s','gate',
            'stile','nw','se','sw','ne','stile','gate','n','nw','nw','w','w','gate','s','w','w','w','n','chapel'
        ]
        #Contains lvl 2&3 mobs (stacker, furniture maker, sawmill operator, mill worker) and lvl 6 mobs (saw)?mill supervisor
        self.MILL_WORKERS = [
            'out','s','e','s','s','s','w','gate','s','s','s','s','s','sw','s','se','sw','s','s','se','s','s','sw',
            'bridge','s','sw','w','canal','s','s','s','e','e','w','s','e','w','n','n','e','s','s','sw','out','w','n',
            'n','n','n','n','nw','ne','n','n','n','ne','ne','ne','ne','n','n','gate','e','n','n','n','w','n','chapel'
        ]
        self.RANCHER_SENTRY = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','pathway','nw','n','n','n','nw','nw','n',
            'n','gate','ne','n','ne','n','gate','e','e','e','n','n','ne','n','ne','gate','arch','n','e','n','nw','gate',
            'n','e','e','s','e','n','s','w','w','w','gate','sw','s','e','s','arch','gate','sw','s','sw','s','s','w','w',
            'w','gate','s','sw','s','sw','gate','s','s','se','se','s','s','s','se','s','w','w','w','nw','nw','n','gate',
            'e','n','n','n','w','n','chapel'
        ]
        #aid418, 1975, 1979, 1951, 415, 45

        # These area numbers are unfortunately for a different database... (except "2")
        self.SPIDER_FOREST = [
            'areaid418', 'areaid1975', 'areaid1979', 'areaid1951', 'areaid415', 'areaid2'
        ]
        #The following areas repeat a bit because the spawns are fast
        self.KNIGHTS = [
            'areaid1904', 'areaid1912', 'areaid1909', 'areaid1913','areaid1904', 'areaid1912', 'areaid1909',
            'areaid1913', 'areaid1904', 'areaid1912', 'areaid1909', 'areaid2'  # end with chapel
        ]
        self.GNOLL_CAMP = [
            'areaid1574', 'areaid800', 'areaid1574', 'areaid800', 'areaid1574', 'areaid2'
        ]
        self.PATH_TO_SKIP_WITH = ['out','chapel']

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

        if self.__nextpath % 2 == 0:
            # self.inventory.get_inventory()
            #magentaprint(str(int(len(self.inventory.sellable()))) + " items to sell - threshold is " + str(self.loot_threshold) + '.')
            # I see... sellable doesn't return a list now
            # Sellable is calling get_inventory, so better not call it too many times
            # len() on the return value interprets the return value as a list
            #
            if len(self.inventory.sellable()) > self.loot_threshold:
                magentaprint("Trackgrind pawning and dropping.")
                return self.SHOP_AND_TIP_PATH[:]
            else:
                magentaprint("Trackgrind skipped pawning/dropping.")
        elif self.__nextpath == 1:
            return self.THEATRE_PATH[:]
        elif self.__nextpath == 3:
            return self.MARKET_PATH[:]
        elif self.__nextpath == 5:
            return self.MILITIA_SOLDIERS_PATH[:]
        elif self.__nextpath == 7:
            if not self.cast.aura:
                if self.character.level >= 4:
                    return self.KOBOLD_PATH[:]
                else:
                    magentaprint("Not going to do kobolds - aura unknown.")
                    self.__nextpath = self.__nextpath + 1  # So that we don't go selling
                    return self.PATH_TO_SKIP_WITH[:]
            elif (self.character.level >= 4 or self.cast.aura < Aura('pale blue')) or \
                self.cast.aura <= self.character.preferred_aura:
                return self.KOBOLD_PATH[:]
            else:
                magentaprint("Not going to do kobolds. Current aura, and preferred, comparison: %s,  %s, %s" %
                             (str(self.cast.aura), str(self.character.preferred_aura), str(self.cast.aura <= self.character.preferred_aura)))
                self.__nextpath = self.__nextpath + 1  # So that we don't go selling
                return self.PATH_TO_SKIP_WITH[:]
        elif self.__nextpath == 9:
            # hookers ... I would avoid the drunken trouble makers, but I don't
            # quite remember where they are and don't want to go through Amber
            # Also I think it's safe enough in the dark... maybe just lvl 4
            # there are thugs
            if self.character.level <= 6:
                return self.CORAL_ALLEY_PATH[:]
            else:
                self.__nextpath = self.__nextpath + 1  # So that we don't go selling
                return self.PATH_TO_SKIP_WITH[:]
        elif self.__nextpath == 11:
            return self.FORT_PATH[:]
        elif self.__nextpath == 13:
            if not self.cast.aura:
                if self.character.level >= 8:
                    return self.NORTHERN_BANDITS_PATH[:]
                else:
                    magentaprint("Not going to do bandits - aura unknown.")
                    self.__nextpath = self.__nextpath + 1  # So that we don't go selling
                    return self.PATH_TO_SKIP_WITH[:]
            elif (self.character.level >= 8 or self.cast.aura < Aura('pale blue')) or \
                self.cast.aura <= self.character.preferred_aura:
                return self.NORTHERN_BANDITS_PATH[:]
            else:
                magentaprint("Not going to do bandits. Current aura, and preferred: %s,  %s" %
                             (self.cast.aura, self.character.preferred))
                self.__nextpath = self.__nextpath + 1   # So that we don't go selling
                return self.PATH_TO_SKIP_WITH[:]
        elif self.__nextpath == 15:
            return self.MUGGER_PATH[:]
        elif self.__nextpath == 17:
            return self.DWARVEN_FIELD_WORKERS_PATH[:]
        elif self.__nextpath == 19:
            return self.MILL_WORKERS[:]
        elif self.__nextpath == 21:
            return self.RANCHER_SENTRY[:]
        elif self.__nextpath == 23:
            return self.get_path_with_all_mobs('Olmer')
        elif self.__nextpath == 25:
            return self.get_path_to_and_from_mob("Brotain")
        elif self.__nextpath == 27:
            return self.get_path_to_and_from_mob("Aldo")
        elif self.__nextpath == 29:
            return self.get_path_to_and_from_mob("Jerrek")
        elif self.__nextpath == 31:
            return self.get_path_to_and_from_mob("Tag")
        elif self.__nextpath == 33:
            return self.get_path_with_all_mobs('Dini Stonehammer')
        elif self.__nextpath == 35:
            return self.get_path_to_and_from_mob("sonneteer")
        elif self.__nextpath == 37:
            return self.get_path_with_all_mobs('Thereze')
        elif self.__nextpath == 39:
            return self.get_path_with_all_mobs('Rancher Renstone')
        elif self.__nextpath == 41:
            return self.get_path_with_all_mobs('artificer')
        elif self.__nextpath == 43:
            return self.get_path_with_all_mobs("mine manager") # tough path
        elif self.__nextpath == 45:
            return self.get_path_with_all_mobs('refinery supervisor')
            # tough path
            # oremaster steel collar (m) and (l), granite rods in keep list right now
            # stevedore
            # forge worker
            # steel collar
        elif self.__nextpath == 47:
            return self.get_path_with_all_mobs('Elder Barthrodue')
            # fishermans spouse
            # hobo
            # village elder lvl 1
            # scared trawlerman 33 exp 53 gold
        # elif self.__nextpath == 49:
        #     return self.SPIDER_FOREST[:]
        # elif self.__nextpath == 51:
        #     return self.GNOLL_CAMP[:]
        # elif self.__nextpath == 53:
        #     return self.KNIGHTS[:]
        else:
            magentaprint("Unexpected case in decide_where_to_go, nextpath==" + str(self.__nextpath))
            return list(self.PATH_TO_SKIP_WITH[:])
        return list(self.PATH_TO_SKIP_WITH[:])

    def get_path_to_and_from_mob(self, name):
        #return ['areaid{0}'.format(MobLocation.get_locations_by_exact_mob_name(name)),
        # package.file.class.function
        chapel_aid = db.Area.Area.get_by_name("The Chapel of Healing").id
        mob_aid    = db.MobLocation.MobLocation.get_locations_by_exact_mob_name(name)[0].area.id
        get_path   = self.mud_map.get_path
        magentaprint("TrackGrindThread get_path_to_and_from_mob chapel_aid {0} mob_aid {1}".format(chapel_aid,mob_aid))
        return get_path(chapel_aid, mob_aid) + get_path(mob_aid, chapel_aid)
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
