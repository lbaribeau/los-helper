
import time
import sys
import re

from collections import Counter
from Exceptions import *
from reactions.BotReactions import *
from misc_functions import *
from db.Database import *
from db.MudMap import *
from db.MudArea import *
from db.MudItem import *
from db.MudMob import *
from comm import RegexStore as R
from Aura import Aura
from reactions.referencing_list import ReferencingList

class Cartography(BotReactionWithFlag):
    def __init__(self, mudReaderHandler, commandHandler, character):
        super().__init__() # threading.Event
        self.mudReaderHandler = mudReaderHandler
        self.commandHandler   = commandHandler
        self.character        = character

        self.store_item_list = "(?:[\s]*)(?:A |An |Some )?(.+?)(?:[\s]*)(?:(\(.\))?(?:[\s]*))?Cost: ([\d]*)" 
        # (Do a re.findall on the list above to iterate through, don't add this to the array below)
        self.regex_cart = [
            R.area,             
            R.too_dark,            
            R.no_exit,             
            R.blocked_path,     
            R.cant_go,          
            R.please_wait,
            R.class_prohibited, 
            R.level_too_low,
            R.level_too_high,
            R.not_invited,      
            R.not_open_during_day, 
            R.not_open_during_night,
            R.no_items_allowed, 
            R.locked,              
            R.no_right,         
            R.not_authorized,
            R.cannot_force,     
            R.not_here,            
            R.loot_blocked,     
            R.teleported,
            R.in_tune,          
            R.you_see_mob,         
            R.mob_aura,         
            R.store_list,
            R.mob_fled,         
            R.open_first,          
            R.washroom
        ]

        #self.__waiter_flag = False # Now using threading.Event
        self.__stopping = False
        # self.mudReaderHandler.register_reaction(self)
        mudReaderHandler.add_subscriber(self)

    # def wait_for_flag(self):
    #     magentaprint("Cartography.wait_for_flag()")
    #     super().wait_for_flag()

    def notify(self, regex, M):
        if regex in R.too_dark:
            self.too_dark(regex, M)
        elif regex in R.area:
            self.area(M)
        elif regex in R.blocked_path:
            self.blocked_path(regex, M)
        elif regex in R.loot_blocked:
            # loot_blocker = M.group(2)
            loot_blocker = self.character.mobs.read_match(M)
            magentaprint("Cartography loot blocker blocking pickup: " + loot_blocker)
            self.catalog_loot_blocker(loot_blocker)
        elif regex in R.please_wait:
            if self.character.TRYING_TO_MOVE:
                self.go_please_wait(regex, M)
        elif regex in R.cant_go:
            # This one is pretty problematic... as it should never happen.
            # Means we're off course.
            # (Erhm - never say never, this triggers all the time)
            # I think it triggers in regular play
            self.character.SUCCESSFUL_GO = False
            self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
            self.set_area_exit_as_unusable(regex)  # TODO: Seems a little harsh... 
            if self.character.TRYING_TO_MOVE:
                magentaprint("Cartography: unsuccessful go (can't go that way): " + str(self.character.LAST_DIRECTION))
                self.character.TRYING_TO_MOVE = False
        elif regex in R.class_prohibited      + R.level_too_low    + R.level_too_high + \
                      R.not_open_during_day   + R.no_items_allowed + R.locked   +       \
                      R.not_open_during_night + R.not_authorized   + R.no_right +       \
                      R.cannot_force          + R.not_invited      + R.washroom + R.in_tune:
            self.set_area_exit_as_unusable(M.group(0))
            self.character.SUCCESSFUL_GO = False
            self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
            self.character.TRYING_TO_MOVE = False
        elif regex in R.you_see_mob:
            #health = M.group(4)
            self.catalog_monster_bio(
                M.group(2), # name
                M.group(3), # description
                M.group(5)  # level
            )
        elif regex in R.mob_aura:
            # name = M.group(2)
            # aura = M.group(3)
            #magentaprint("{" + M.group(0) + "}", False)
            #magentaprint("{" + regex + "}", False)
            #magentaprint("'" + name + "' => '" + aura + "'",False)
            magentaprint("Cartography mob aura: " + self.character.mobs.read_match(M) + ', ' + M.group('aura'))
            self.catalog_monster_aura(self.character.mobs.read_match(M), M.group('aura'))
        elif regex in R.not_here + R.no_exit:
            #The state is confusion is usually caused by bad processing of good data (i.e. bugs)
            #The following is a set of work arounds to smoothe things out until those bugs are fixed
            if self.character.ACTIVELY_BOTTING:
                if self.character.CONFUSED:
                    if (not self.character.CAN_SEE):
                        self.commandHandler.process('c light') #look around to stop the "you don't see that here bug"

                    #clear the attacking list
                    self.character.MOBS_ATTACKING = []

                    # self.commandHandler.process('l') #look around to stop the "you don't see that here bug"
                else:
                    self.character.CONFUSED = True

            if regex in R.no_exit:
                self.character.GO_NO_EXIT = True

            self.character.SUCCESSFUL_GO = False
            self.character.TRYING_TO_MOVE = False
            self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
        elif regex in R.teleported:
            if M.group(1) == self.character.name:
                self.character.DEAD = True
                self.character.AREA_ID = 82  # TODO: this id is out of sync
                self.character.MUD_AREA = None
        elif regex in R.store_list:
            self.store_list(regex, M)
        else:
            # This is fine for a shut door - we just want the super().notify in that case.
            magentaprint("Cartography case missing for regex: " + str(regex)) # (mob_fled)
        magentaprint("Cartography notify done on: " + str(regex[:min(len(regex), 20)]) + '...')
        super().notify(regex, M) # threading.Event

    def too_dark(self, regex, M):
        magentaprint("Cartography receiving too_dark notification")
        C = self.character
        if C.AREA_ID is not None:
            guessed_area = self.guess_location(C.AREA_ID, C.LAST_DIRECTION)

            if guessed_area is not None:
                C.AREA_ID    = guessed_area.area.id
                C.AREA_TITLE = guessed_area.area.name
                C.EXIT_LIST  = guessed_area.area_exits
                C.MUD_AREA   = guessed_area
            else:
                C.AREA_ID    = None
                C.AREA_TITLE = None
                C.MUD_AREA   = None
                C.EXIT_LIST  = []

        C.mobs.list = ReferencingList([])
        C.mobs.attacking = []

        C.SUCCESSFUL_GO = True
        self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
        C.CAN_SEE = False
        C.CONFUSED = False

        if C.TRYING_TO_MOVE:
            C.TRYING_TO_MOVE = False

    def area(self, match):
        # magentaprint(M.group(0),False,False,True)
        C = self.character
        C.AREA_TITLE = match.group(1).strip()
        C.EXIT_LIST  = self.parse_exit_list(match.group(3))
        C.EXIT_REGEX = self.create_exit_regex_for_character(C.EXIT_LIST)
        C.mobs.list  = ReferencingList(self.parse_monster_list(match.group(4)))
        # This calls mobs.parse_monster_list
        magentaprint("Cartography.area set character.mobs.list: " + str(C.mobs.list))
        # magentaprint("Cartography set character.mobs.list.list: " + str(C.mobs.list.list))
        C.mobs.attacking = [] # TODO: match regex for entering an area where a mob is already attacking you

        C.CAN_SEE       = True
        C.CONFUSED      = False
        C.SUCCESSFUL_GO = True #successful go should be true everytime the area parses
        self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0

        if C.TRYING_TO_MOVE:
            # I think TRYING_TO_MOVE prevents multiple saves of the area
            #if C.EXIT_LIST is not []: 
            # Ehhh this was always true! ('is' tests for same object)
            # I don't think the regex will match without an exit list.
            if C.EXIT_LIST != []:
                # area = self.draw_map(area_title, area_description, C.EXIT_LIST)
                C.MUD_AREA = MudArea.map(
                    C.AREA_TITLE, 
                    match.group(2).strip(), # area description (eat the description - doesn't give the full text)
                    C.EXIT_LIST, 
                    C.AREA_ID, 
                    C.LAST_DIRECTION, 
                    C.MUD_AREA
                )
                magentaprint("Cartography area match: " + str(C.MUD_AREA.area))
                #magentaprint("Try [m for m in C.mobs.list.list] " + str([m for m in C.mobs.list.list]))
                #magentaprint("Try [str(m).lower() for m in C.mobs.list.list]" + str([str(m).lower() for m in C.mobs.list.list]))
                #magentaprint("Cartography monster list: " + str(C.mobs.list))
                self.catalog_monsters(
                    C.MUD_AREA.area, 
                    [str(m).lower() for m in C.mobs.list.list]
                )
                # I think we catalog in lower case?
                # Still don't know how m is a GameObject and we need str(m).lower() 
                # - (check ReferencingList.add - items/things are GameObjects)
                C.AREA_ID = C.MUD_AREA.area.id
            else:
                magentaprint("Cartography warning: exit list was empty???")
                C.AREA_ID = None
            C.TRYING_TO_MOVE = False

    def blocked_path(self, regex, M):
        # mob_name = M.group('mob_name')
        mob_name = self.character.mobs.read_match(M)
        magentaprint("Cartography blocking mob name: " + mob_name)
        self.character.GO_BLOCKING_MOB = mob_name
        self.character.SUCCESSFUL_GO = False
        self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
        self.catalog_path_blocker(mob_name)
        if self.character.TRYING_TO_MOVE:  
            self.character.TRYING_TO_MOVE = False

    def go_please_wait(self, regex, M):
        magentaprint("Cartography: unsuccessful go| (please wait) dir="  + str(self.character.LAST_DIRECTION))  
        magentaprint("Cartography: unsuccessful go| is trying to move?= "  + str(self.character.TRYING_TO_MOVE))  
        self.character.GO_PLEASE_WAIT = True
        self.character.SUCCESSFUL_GO = False
        self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
        self.character.TRYING_TO_MOVE = False

    def store_list(self, regex, M):
        magentaprint(M.group('store_list'))
        # self.store_item_re = r"\s+(?P<item>[A-Za-z']+ )+\s+(\((?P<size>[sml])\)\s+)?Cost: (?P<cost>\d+)\r\n"  
        self.store_item_re = r"\s+(?P<item>([A-Za-z']+ )+)\s+(\((?P<size>[sml])\)\s+)?Cost: (?P<cost>\d+)[\r\n]{2}"  
        # for store_item_match in re.findall(self.store_item_re, M.group('store_list') + '\r\n'):
        for imatch in re.finditer(self.store_item_re, M.group('store_list') + '\r\n'):
            magentaprint('Parsed item: ' + self.character.inventory.remove_a_an_some(imatch.group('item').strip()) + ', size: ' + str(imatch.group('size')) + ', cost: ' + imatch.group('cost'))
            area_item = self.catalog_item(self.character.inventory.remove_a_an_some(imatch.group('item').strip()), str(imatch.group('size')), int(imatch.group('cost')))
            self.catalog_area_store_item(area_item, self.character.AREA_ID)
            # item_list = re.findall(self.store_item_list, M.group(0))
            # magentaprint("{" + M.group(0) + "}", False)
            # magentaprint("items: " + str(item_list), False)
            # for item in item_list:
            #     item_name = item[0]
            #     item_size = item[1]
            #     item_value = item[2]

    #Used if it's dark and / or the current area doesn't appear to be findable
    def guess_location(self, area_from_id, direction_from):
        guessed_area = None

        if self.character.MUD_AREA is not None:
            exit_type = ExitType.get_exit_type_by_name_or_shorthand(direction_from)

            if exit_type is None:
                exit_type = ExitType(name=direction_from)

            guessed_area = self.character.MUD_AREA.get_area_to_from_exit(exit_type)
            curMudArea = self.character.MUD_AREA.get_area_to_from_exit(exit_type)

            if curMudArea is not None:
                #check if curMudArea can be dark
                guessed_area = curMudArea

        return guessed_area

    def set_area_exit_as_unusable(self, regex):
        self.character.GO_NO_EXIT = True
        self.character.SUCCESSFUL_GO = False
        self.CHECK_GO_FLAG = 0

        if self.character.ACTIVELY_MAPPING:
            try:
                area_from = self.character.AREA_ID
                exit_type = self.character.LAST_DIRECTION

                MudArea.set_area_exit_as_unusable(regex, area_from, exit_type)
            except Exception:
                magentaprint("Tried to make an area exit unusuable but failed")

    def catalog_monsters(self, area, monster_list):
        try:
            for monster in monster_list:
                mob = Mob(name=monster)
                mob.map()

                if self.character.ACTIVELY_BOTTING:
                    if mob.approximate_level == None:
                        self.commandHandler.process('l ' + monster)

                # magentaprint(str(mob))

                mob_location = MobLocation(area=area, mob=mob)
                mob_location.map()

                magentaprint("Cartography catalog_monsters() mob_location id {0}, {1}".format(mob_location, mob.name))
        except Exception:
            magentaprint("Problem cataloging monsters", False)

    def catalog_monster_bio(self, name, description, level):
        try:
            mob = Mob(name=name)
            mob.map()
            mob.description = description.strip()

            if mob.level is None: #don't overwrite levels
                for regex in self.character.LEVEL_LIST:
                    if re.match(regex, level):
                        level_index = self.character.LEVEL_LIST.index(regex) - 4
                        if level_index == -4 or level_index == 4:
                            mob.approximate_level = self.character.level + level_index
                        else:
                            mob.level = self.character.level + level_index
                            mob.approximate_level = self.character.level + level_index

                mob.save()
        except Exception:
            magentaprint("Problem cataloging monster bio")

    def catalog_monster_aura(self, name, aura):
        if aura not in Aura.auras:
            # Deals with "the rod glows with a deep brown aura" bug
            return

        mob = Mob(name=name)
        mob.map()
        mob.aura = Aura.auras.index(aura)

        mob.save()

    def catalog_path_blocker(self, path_blocker_name):
        mob = Mob(name=path_blocker_name)
        mob.map()

        if not mob.blocks_exit:
            magentaprint("Cartography catalogged new path blocker", False)
            mob.blocks_exit = True
            mob.save()

    def catalog_loot_blocker(self, loot_blocker_name):
        mob = Mob(name=loot_blocker_name)
        mob.map()

        if not mob.blocks_pickup:
            magentaprint("Cartography catalogged new loot blocker", False)
            mob.blocks_pickup = True
            mob.save()

    def catalog_item(self, item_name, item_size, item_value):
        item = Item(name=item_name, value=item_value, description=item_size)
        item.map()

        return item

    def catalog_area_store_item(self, item, area):
        asitem = AreaStoreItem(area=area,item=item)
        asitem.map()

    def parse_exit_list(self, MUD_exit_str):
        try:
            if (MUD_exit_str is None):
                magentaprint("Cartography exit match: " + str(MUD_mob_str))
                return []

            MUD_exit_str = MUD_exit_str.strip()
            my_exit_regex = r"(?s)Obvious exits: (.+?)\." #added clause if the exits break onto two lines - likely this will ahve to happen for mobs too
            match_exits = re.match(my_exit_regex, MUD_exit_str)
            E_LIST = [x.strip() for x in match_exits.group(1).split(',')]
            #technique above is referred to as list comprehension see:
            #http://stackoverflow.com/questions/501308/problem-in-understanding-python-list-comprehensions/501323#501323

            E_LIST = self.number_exits(E_LIST)
        except Exception:
            E_LIST = []
            magentaprint("Parse exit Exception: " + str(sys.exc_info()[0]), False)
            raise

        return E_LIST

    def number_exits(self, E_LIST):
        exit_count = Counter(E_LIST) #collections function for finding duplicates
        exit_list = E_LIST

        for key,value in exit_count.items():
            #magentaprint(str(key) + " : " + str(value), False)
            if value > 1:
                count = 1
                for i,s in enumerate(exit_list):
                    if exit_list[i] == key:
                        if count != 1:
                            exit_list[i] += " " + str(count)
                            magentaprint('Cartography.number_exists found multiple {0}'.format(exit_list[i]), False)
                        count += 1 #I miss my i++

        return exit_list

    def create_exit_regex_for_character(self, E_LIST):
        exit_regex = "(NEVERMATCHTHISEVEREVER)"
        if E_LIST is not None:
            exit_regex = "(?:go )?(!?"

            for i,s in enumerate(E_LIST):
                exit_regex += "(" + str(s) + ")"

                if (i < len(E_LIST) - 1):
                    exit_regex += "|"

            exit_regex +=")"

        return exit_regex

    def parse_monster_list(self, MUD_mob_str):
        if MUD_mob_str is None:
            return []

        MUD_mob_str = MUD_mob_str.replace("\n\r", ' ')
        mob_match = re.match(r"(?s)You see (.+?)\.", MUD_mob_str)

        if mob_match is None:
            # return self.character.MONSTER_LIST
            return []
        else:
            #return self.character.mobs.parse_mob_string(mob_match.group(1).lower())
            return self.character.mobs.parse_mob_string(mob_match.group(1))

        # M_LIST = [m.strip() for m in mob_match.group(1).split(',')]
        # singles = ['a ', 'an ', 'The ']
        # numbers = ['two ', 'three ', 'four ', 'five ', 'six ', 'seven ',
        #            'eight ', 'nine ', 'ten ', 'eleven ', 'twelve ', 'thirteen ', 'fourteen ',
        #            'fifteen ' , 'sixteen ', 'seventeen ', 'eighteen ', 'nineteen ', 'twenty ']
        # numbers.extend([str(i) + " " for i in range(21, 200)])

        # # return [Mobs.remove_plural(m.strip()) for m in mob_match.group(1).split(',')]

        # m_list = []
        # for m in M_LIST:
        #     if any([m.startswith(s) for s in singles]):
        #         # m_dict[m.partition(' ')[2]] = 1
        #         m_list.extend([m.partition(' ')[2]])
        #         continue
        #     # number_check = [m.startswith(n) for n in numbers]

        #     m = Mobs.remove_plural(m)

        #     for n in range(0, len(numbers)):
        #         if m.startswith(numbers[n]):
        #             # m_dict[m.partition(' ')[2]] = n + 2
        #             m_list.extend([m.partition(' ')[2]] * (n + 2))
        #             break

        # # return list(m_dict.keys())
        # return m_list

        #     # commaindex = M_LIST[i].find(',')
        #     # if commaindex != -1:
        #     #     M_LIST = M_LIST[:commaindex]

        # # except Exception:
        # #     magentaprint("Parse monster Exception: " + str(sys.exc_info()[0]), False)
        # #     M_LIST = []

        # # return M_LIST








