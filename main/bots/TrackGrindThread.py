
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
            self.__TOTALPATHS = 16 # used to do bandits at level 7
        elif self.character.level <= 10:
            self.__TOTALPATHS = 22
        elif self.character.level <= 14:
            self.__TOTALPATHS = 77 
        elif self.character.level <= 15:
            self.__TOTALPATHS = 91
        elif self.character.level <= 16:
            self.__TOTALPATHS = 103
        else:
            self.__TOTALPATHS = 103

        if isinstance(starting_path, int) and starting_path < self.__TOTALPATHS:
            self.nextpath = starting_path
        else:
            self.nextpath = 0

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
            # Brocolli wants to get ALL the kobolds in one shot... even the chief? Yeahh.
            # This route is optimal travel and isn't picky about order
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
            # 'e','e','se','w','w','w','sw','s','w','s','s','se','n','n','n','e',
            # 'e','s','w','s','s','e','e','n','e','s','n','e','cave',# unlock trap key; trap; out
            # 'out','n','nw','n','sw','s','w','s','s','se','n','n','n','e','s','s','s','e','n','n','e','s','s','e','n','e','cave',
            # 'out'
            'door', 'prepare', 'sw','w',
            'ladder','cave','out', # champion
            'sw','w',
            # 'cave', 'out', #insane (maybe don't take that fight in case both hammers are gonzo)
            'sw','se',# shaman
            'nw','w','out','down','boulder','down','down','e','door','w','s','s','e','s','sw','s','s','s',
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
            'out','n','n', 'w','gate','n','n','n','n','n','gate',
            'n','n','w','s','s','e','e','n','n','w','s','s','gate',
            's','s','s','s','s','gate','w','sw','s','s','s','e','e','e','e','n','w','n','chap'
        ]
        self.NORTHERN_BANDITS_PATH = [
            'out','n','n','w','gate','n','n','n','n','n','gate','n','n','gate','n','nw','nw','sw','sw','sw','sw','s',
            'sw','sw','w','w','sw','sw','sw','sw','sw','sw','w','w','w','w','nw','w','w','nw','sw','nw','w','w','w',
            'nw','w','w','w','w','s','s','s','n','n','n','e','e','e','e','se','e','e','e','se','ne','se','e','e','se',
            'e','e','e','e','ne','ne','ne','ne','ne','ne','e','e','ne','ne','n','ne','ne','ne','ne','se','se','s',
            'gate','s','w','e','s','gate','s','s','s','s','s','gate','e','s','s','chapel'
        ]
        self.MUGGER_PATH = [
            'ou','s','w','w','w','s','alley','w','alley','e','e','e','e','e','n','w','n','chap'
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
            # 'se','field','road', # Comment out - I think this part of the path is wrong
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
        self.RANCHER_SENTRY = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','pathway','nw','n','n','n','nw','nw','n',
            'n','gate','ne','n','ne','n','gate','e','e','e','n','n','ne','n','ne','gate','arch','n','e','n','nw','gate',
            'n','e','e','s','e','n','s','w','w','w','gate','sw','s','e','s','arch','gate','sw','s','sw','s','s','w','w',
            'w','gate','s','sw','s','sw','gate','s','s','se','se','s','s','s','se','s','w','w','w','nw','nw','n','gate',
            'e','n','n','n','w','n','chapel'
        ]
        #both gates close at night unforunately...
        self.FIELD_WORKERS_PATH = [
            'out','s','e','s','s','s','w','gate','s','se','se','e','e','e','pathway','nw','n','n','n','nw','nw','n',
            'n','gate','w','n','nw','nw','n','gate','w','w','sw','sw','w','w','w','sw','sw','se','se','s','gate',
            'stile','nw','se','sw','ne','stile','gate','n','nw','nw','w','w','gate','s','w','w','w','n','chapel'
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
        self.nextpath = (self.nextpath + 1) % (self.__TOTALPATHS + 1)
        magentaprint("next path = " + str(self.nextpath), False)

        if self.character.AREA_ID != 2:
            magentaprint("CAUTION: decide_where_to_go called when we should be in the chapel! AREA_ID is {}.".format(self.character.AREA_ID))
            self.command_handler.process("l")
            return ['areaid2']

        if self.character.DEAD:
            self.character.DEAD = False
            self.character.DEATHS += 1
            # magentaprint("Died: Pulling up my bootstraps and starting again", False)
            magentaprint("Died: stopping bot thread.", False)
            self.stop()
            return self.LIMBO_TO_CHAPEL[:]

        if self.nextpath % 2 == 0:
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
                return self.PATH_TO_SKIP_WITH[:] # don't call .skip() because we don't want to double increment nextpath
        elif self.nextpath == 1:
            return self.THEATRE_PATH[:]
        elif self.nextpath == 3:
            return self.MARKET_PATH[:]
        elif self.nextpath == 5:
            return self.MILITIA_SOLDIERS_PATH[:]
        elif self.nextpath == 7:
            if not self.cast.aura or (self.cast.aura and self.cast.aura >= Aura('pale blue') and self.cast.aura <= self.character.preferred_aura):
                if self.character.level in [1,2,3,4,5]:
                    magentaprint("Not going to do kobolds - aura unknown and level too low.")
                    return self.skip()
                elif self.character.level in [6,7]:
                    return self.KOBOLDS1[:]
                elif self.character.level in [8,9]:
                    return self.kobold_guards_and_insane[:]
                elif self.character.level in [10,11,12]:
                    # So this will throw the balance of the track at level 10
                    return self.kobold_priests[:]
                else:
                    return self.kobold_massacre[:]
            # Track-based aura fixing (skipping track if aura is too blue)
            # elif (self.character.level >= 4 or self.cast.aura < Aura('pale blue')) or \
            #     self.cast.aura <= self.character.preferred_aura:
            elif self.cast.aura > self.character.preferred_aura:
                    magentaprint("Not going to do kobolds - too blue right now")
                    return self.skip()
            else:
                # # magentaprint("Not going to do kobolds. Current aura, and preferred, comparison: %s,  %s, %s" %
                # #              (str(self.cast.aura), str(self.character.preferred_aura), str(self.cast.aura <= self.character.preferred_aura)))
                # return self.skip()
                if self.character.level in [1,2,3,4,5]:
                    return self.KOBOLDS1[:]
                elif self.character.level in []:
                    return self.kobold_guards_and_insane[:]
                elif self.character.level in [6,7,8,9,10,11]:
                    return self.kobold_priests[:]
                else:
                    return self.kobold_massacre[:]
        elif self.nextpath == 9:
            # hookers ... I would avoid the drunken trouble makers, but I don't
            # quite remember where they are and don't want to go through Amber
            # Also I think it's safe enough in the dark... maybe just lvl 4
            # there are thugs
            if self.character.level <= 6:
                return self.CORAL_ALLEY_PATH[:]
            else:
                magentaprint("Skipping coral alley (level: {})".format(self.character.level))
                return self.skip()
        elif self.nextpath == 11:
            return self.FORT_PATH[:]
        elif self.nextpath == 13:
            if not self.cast.aura:
                if self.character.level >= 8:
                    return self.NORTHERN_BANDITS_PATH[:]
                else:
                    magentaprint("Not going to do bandits - aura unknown.")
                    return self.skip()
            elif (self.character.level >= 8 or self.cast.aura < Aura('pale blue')) and \
                self.cast.aura <= self.character.preferred_aura:
                # Can handle bandits even if blue if level is high enough
                # However, don't do them if aura is bluer than preferred
                return self.NORTHERN_BANDITS_PATH[:]
            else:
                magentaprint("Not going to do northern bandits. (Level %s, current aura %s, and preferred %s.)" %
                             (self.character.level, self.cast.aura, self.character.preferred_aura))
                return self.skip()
        elif self.nextpath == 15:
            if self.character.level >= 5 and (not self.cast.aura or self.cast.aura <= self.character.preferred_aura):
                return self.MUGGER_PATH[:]
            else:
                magentaprint("Not going to do muggers. (Level %s, current aura %s, and preferred %s.)" %
                             (self.character.level, self.cast.aura, self.character.preferred_aura))
                return self.skip()
        elif self.nextpath == 17:
            return self.DWARVEN_FIELD_WORKERS_PATH[:]
        elif self.nextpath == 19:
            return self.MILL_WORKERS[:]
        elif self.nextpath == 21:
            if self.cast.aura and self.cast.aura <= self.character.preferred_aura:
                return self.BANDITS1[:]
            else:
                return self.skip()
        elif self.nextpath == 23:
            if self.cast.aura and self.cast.aura <= self.character.preferred_aura:
                return self.BANDITS2[:]
            else:
                return self.skip()
        elif self.nextpath == 25:
            if self.cast.aura and self.cast.aura <= self.character.preferred_aura:
                return self.BANDITS3[:]
            else:
                return self.skip()
        elif self.nextpath == 27:
            if self.cast.aura and self.cast.aura <= self.character.preferred_aura:
                return self.BANDITS4[:]
            else:
                return self.skip()
        elif self.nextpath == 29:
            return self.RANCHER_SENTRY[:]
        # elif self.nextpath == 23:
        #     return self.get_path_with_all_mobs('Olmer') # Doesn't fight - something about the bright wallposter I think...
        elif self.nextpath == 31:
            return self.get_path_to_and_from_mob("Brotain")
        elif self.nextpath == 33:
            return self.get_path_to_and_from_mob("Aldo")
        elif self.nextpath == 35:
            return self.get_path_to_and_from_mob("Jerrek") 
            # He gets fought occasionally but we should fight him before Tag
            # This can spend some time if he's not in the kill list
        elif self.nextpath == 37:
            return self.get_path_to_and_from_mob("Tag")
        elif self.nextpath == 39:
            return self.get_path_to_and_from_mob("Olmer")
        elif self.nextpath == 41:
            return self.get_path_with_all_mobs('Dini Stonehammer')
            # Viladin
            # Douvan would be good but isn't on my map
            # Servant of the Night
            # Trent the Merchant
        elif self.nextpath == 43:
            return self.get_path_to_and_from_mob("sonneteer")
        elif self.nextpath == 45:
            return self.get_path_with_all_mobs('Thereze')
        elif self.nextpath == 47:
            return self.get_path_with_all_mobs('Rancher Renstone')
        elif self.nextpath == 49:
            return self.get_path_with_all_mobs('artificer')
        elif self.nextpath == 51:
            return self.get_path_with_all_mobs('enchantress') 
            # Higher level but needs to be done right after artificer
            # Maybe she's too blue though
        elif self.nextpath == 53:
            return self.get_path_with_all_mobs("mine manager") # tough path
        elif self.nextpath == 55:
            return self.get_path_with_all_mobs('refinery supervisor')
            # tough path
            # oremaster steel collar (m) and (l), granite rods in keep list right now
            # stevedore
            # forge worker
            # steel collar
        # CHARACTER 13 / MOBS 9
        elif self.nextpath == 57:
            return self.get_path_with_all_mobs('Elder Barthrodue')
        elif self.nextpath == 59:
            return self.MUGGER_PATH[:] # Clear the muggers so we don't run out of mana later
        elif self.nextpath == 61:
            return self.get_path_with_all_mobs('director')
        # CHARACTER 14 / MOBS 10
        elif self.nextpath == 63:
            return self.get_path_with_all_mobs('Dame Brethil')
            # makeup kits don't sell well
        elif self.nextpath == 65:
            return self.get_path_with_all_mobs('Kelluran')
        elif self.nextpath == 67:
            return self.get_path_with_all_mobs('Master of Ceremonies')
            # Remove silver knight if you don't want to fight him
            # Also there will be tourney organiser and other things on this path
            # He seems to have a long spawn time
        elif self.nextpath == 69:
            return self.get_path_with_all_mobs('war horse')
            # white knights on this path
        elif self.nextpath == 71:
            return self.FORT_PATH[:] # fort sergeant prefight
        elif self.nextpath == 73:
            return self.get_path_with_all_mobs('Commander Rilmenson') # hastes
        elif self.nextpath == 75:
            return self.get_path_with_all_mobs('Rimark') # This guy is like a guard, right?
        elif self.nextpath == 77:
            return self.get_path_with_all_mobs('dwarven blacksmith')
            # barbarian cook
            # shaman's assistant
        # CHARACTER 15 / MOBS 11
        elif self.nextpath == 79:
            return self.get_path_with_all_mobs('minstrel')
        elif self.nextpath == 81:
            return self.get_path_with_all_mobs('Brotain')
        elif self.nextpath == 83:
            # Pre-fights (sawmill people) can make this harder
            # Maybe do path -1
            return self.get_path_to_previous_node('Gregor')
        elif self.nextpath == 85:
            return self.get_path_with_all_mobs('Gregor')
        elif self.nextpath == 87:
            return self.get_path_with_all_mobs('Bertram Dalram') # Longer respawn?
        elif self.nextpath == 89:
            return self.get_specific_path_to_and_from_mob('brother', 0) # throwing stars
        # elif self.nextpath == 85:
        #     return self.get_specific_path_to_and_from_mob('brother', 1) # Didn't have a brother waiting there
        # CHARACTER 16 / MOBS 12
        elif self.nextpath == 91:
            return self.get_path_with_all_mobs('Horbuk')
        # elif self.nextpath == 89:
        #     return self.get_path_with_all_mobs('Horbuk') 
        #    Do twice in case a mine manager was there... hoping engage controls are high (?)
        #    Actually they got cleared in one pass, on the mine manager path, so never mind this double
        elif self.nextpath == 93:
            # Remember to check character level restriction
            return self.get_path_with_all_mobs('Tardan') # he got me to 0 mana somehow but didn't potion
            # He also made me run like a chicken at [1 HP 1 MP]... so let's wait for level 16
            # Did he have a +1 war hammer (1250 gold)
        elif self.nextpath == 95:
            # Prefight some dwarven travellers? Was 5 hp
            return self.get_path_with_all_mobs('Boris Ironfounder')
            # He is also in another path...
            # He does respawn though
        elif self.nextpath == 97:
            return self.get_path_to_previous_node('Hurn the Smith') # swordsman
        elif self.nextpath == 99:
            return self.get_path_with_all_mobs('Hurn the Smith') # 600 exp, 202-290g, easy peasy
        elif self.nextpath == 101:
            return self.get_path_with_all_mobs('Gorban')
            # Golden potion, but seems hard, could be rng
        elif self.nextpath == 103:
            return self.get_path_with_all_mobs('floor manager') # About the same as Tardan
        elif self.nextpath == 105:
            return self.get_path_with_all_mobs('Shaldena the Red') # Burstflame might cause some characters problems
        elif self.nextpath == "XXX":
            # Watch out for mob targetting bug (ranch foreman hitting Rancher Plover!)
            return self.get_path_with_all_mobs('ranch foreman')
        elif self.nextpath == "XXX":
            # Via rancher plover!!
            return self.get_path_with_all_mobs('Annette Plover') # Seemed harder
            # Has novice prefight
            # Maybe do theatre goers first
            # fishermans spouse
            # hobo
            # village elder lvl 1
            # scared trawlerman 33 exp 53 gold
        # elif self.nextpath == 49:
        #     return self.SPIDER_FOREST[:]
        # elif self.nextpath == 51:
        #     return self.GNOLL_CAMP[:]
        # elif self.nextpath == 53:
        #     return self.KNIGHTS[:]
        # Human paladin likes steel collars (oremaster) steel armour (Rimark) steel mask (spiv) rings (bandits, sawmill, minstrel)
        else:
            magentaprint("Unexpected case in decide_where_to_go, nextpath==" + str(self.nextpath))
        return self.skip()

    def skip(self):
        self.nextpath = self.nextpath + 1 # So that we don't go selling
        # I think I'm getting double increments... (infinite loop)... maybe when skipping selling
        # Ok I spotted it - need to return in that case without calling .skip
        # .skip adds one to to total adding 2, which works for skipping a grind path but not for skipping selling
        # since % 2 is true again
        # Also I have a trackno print in heal_up as well as a trackno print here
        # So all integers do get printed
        # Right... return self.skip() 
        return self.PATH_TO_SKIP_WITH[:]

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
