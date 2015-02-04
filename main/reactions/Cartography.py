
import time
import sys

from collections import Counter
from Exceptions import *
from BotReactions import *
from misc_functions import *
from Database import *
from MudMap import *
from MudItem import *
from MudMob import *
import re

class Cartography(BotReaction):

    def __init__(self, mudReaderHandler, commandHandler, character):
        #             Title     Description        Exit list                    Monsters (opt)                    Items (opt)
        self.area = "(.+?\n\r)((?:\n\r.+)*)?(\n\rObvious exits: .+?[\n\r]?.+?\.)\n\r(You see .+?[\n\r]?.+?\.)?[\n\r]?(You see .+?[\n\r]?.+?\.)?"
        self.too_dark = "It's too dark to see\."
        s_numbered = " ?([\d]*?1st|[\d]*?2nd|[\d]*?3rd|[\d]*th)?"
        the = " ?(?:The|the)?" #named mobs have no "The/the"
        self.you_see_the = "You see" + the + s_numbered + " (.+?)\.\n\r(.+?)\n\r(.+?)\n\r(.+?(?:\.|!))"
        self.mob_aura_check = the + s_numbered + " (.+?) glows with a (.+?) aura\."
        self.blocked_path = the + s_numbered + " (.+?) blocks your exit\."
        self.please_wait = "Please wait [\d]* more seconds?\."
        self.cant_go = "You can't go that way\."
        self.no_exit = "I don't see that exit\."
        self.class_prohibited = "Your class prohibits you from entering there\."
        self.level_too_low = "You must be at least level [\d]* to go that way\."
        self.not_invited = "You have not been invited in\."
        self.not_open_during_day = "That exit is not open during the day\."
        self.not_open_during_night = "That exit is closed for the night\."
        self.no_items_allowed = "You cannot bring anything through that exit\."
        self.door_locked = "It's locked\."
        self.no_right = "You have not earned the right to pass this way!"
        self.in_tune = "That way may only be taken by those in tune with the world!"
        self.not_authorized = "You are not authorised to enter here\."
        self.no_force = "You cannot force yourself to go through there\."
        self.not_here = "You don't see that here\."
        self.loot_blocked = "The" + s_numbered + " (.+?) won't let you take anything\."#The spiv won't let you take anything.
        self.teleported_away = "### (.+?)'s body is teleported away to be healed\."
        self.store_list = "You may buy:\n((?:.+\n?)*)"
        self.store_item_list = "(?:[\s]*)(?:A |An |Some )?(.+?)(?:[\s]*)(?:(\(.\))?(?:[\s]*))?Cost: ([\d]*)" #well do a re.findall on the list above to iterate through, don't add this to the array below

        self.regexes = [self.area,
            self.too_dark,
            self.blocked_path,
            self.please_wait,
            self.cant_go,
            self.no_exit,
            self.class_prohibited,
            self.level_too_low,
            self.not_invited,
            self.not_open_during_day,
            self.not_open_during_night,
            self.no_items_allowed,
            self.door_locked,
            self.no_right,
            self.not_authorized,
            self.no_force,
            self.not_here,
            self.loot_blocked,
            self.teleported_away,
            self.in_tune,
            self.you_see_the,
            self.mob_aura_check,
            self.store_list
            ]

        self.mudReaderHandler = mudReaderHandler
        self.commandHandler = commandHandler
        self.character = character

        self.good_MUD_timeout = 1.5
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex == self.too_dark:            
            if self.character.AREA_ID is not None:
                guessed_area = self.guess_location(self.character.AREA_ID, self.character.LAST_DIRECTION)            

                if guessed_area is not None:
                    self.character.AREA_ID = guessed_area.area.id
                    self.character.AREA_TITLE = guessed_area.area.name
                    self.character.EXIT_LIST = guessed_area.area_exits
                    self.character.MUD_AREA = guessed_area
                else:
                    self.character.AREA_ID = None
                    self.character.AREA_TITLE = None
                    self.character.MUD_AREA = None
                    self.character.EXIT_LIST = []

            self.character.MONSTER_LIST = []
            self.character.SUCCESSFUL_GO = True
            self.mudReaderHandler.MudReaderThread.CHECK_GO_FLAG = 0
            self.character.CAN_SEE = False
            self.character.CONFUSED = False
        elif regex == self.area:
            matched_groups = M_obj.groups()

            area_title = str(matched_groups[0]).strip()
            area_description = str(matched_groups[1]).strip() #eat the description - doesn't give the full text
            exit_list = self.parse_exit_list(matched_groups[2])
            self.character.EXIT_REGEX = self.create_exit_regex_for_character(exit_list)

            monster_list = self.parse_monster_list(matched_groups[3])

            self.character.AREA_TITLE = area_title #title
            self.character.EXIT_LIST = exit_list #exits
            self.character.MONSTER_LIST = monster_list#monster_list #mob list
            self.character.MONSTER_LIST.sort()

            self.character.SUCCESSFUL_GO = True #successful go should be true everytime the area parses
            self.mudReaderHandler.MudReaderThread.CHECK_GO_FLAG = 0
            self.character.CAN_SEE = True
            self.character.CONFUSED = False

            if (self.character.TRYING_TO_MOVE): #we only want to map when user input to move has been registered
                self.character.TRYING_TO_MOVE = False #we've moved so we're not trying anymore
                if (exit_list is not []):
                    area = self.draw_map(area_title, area_description, exit_list)
                    self.catalog_monsters(area, monster_list)

                    self.character.AREA_ID = area.id

                    self.catalog_monsters(area, monster_list)
                else:
                    self.character.AREA_ID = None
        elif regex == self.blocked_path:
            mob_name = M_obj.group(2)
            self.character.GO_BLOCKING_MOB = mob_name
            self.character.SUCCESSFUL_GO = False
            self.mudReaderHandler.MudReaderThread.CHECK_GO_FLAG = 0
            magentaprint("Path blocked by: " + mob_name)
            self.catalog_path_blocker(mob_name)
        elif regex == self.loot_blocked:
            loot_blocker = M_obj.group(2)
            magentaprint("loot blocker blocking pickup by: " + loot_blocker)
            self.catalog_loot_blocker(loot_blocker)
        elif regex == self.please_wait:
            magentaprint("Cartography: unsuccessful go| (please wait) dir="  + str(self.character.LAST_DIRECTION))  
            magentaprint("Cartography: unsuccessful go| is trying to move?= "  + str(self.character.TRYING_TO_MOVE))  
            if (self.character.TRYING_TO_MOVE):
                self.character.GO_PLEASE_WAIT = True
                self.character.SUCCESSFUL_GO = False
                self.mudReaderHandler.MudReaderThread.CHECK_GO_FLAG = 0
        elif regex == self.cant_go:
            # This one is pretty problematic... as it should never happen.
            # Means we're off course.
            magentaprint("Cartography: unsuccessful go (can't go that way): " + str(self.character.LAST_DIRECTION))
            self.set_area_exit_as_unusable(regex)
            self.character.SUCCESSFUL_GO = False
            self.mudReaderHandler.MudReaderThread.CHECK_GO_FLAG = 0
        elif (regex == self.class_prohibited or
                regex == self.level_too_low or
                regex == self.not_invited or
                regex == self.not_open_during_day or
                regex == self.not_open_during_night or
                regex == self.no_items_allowed or
                regex == self.door_locked or
                regex == self.no_right or
                regex == self.not_authorized or
                regex == self.no_force or
                regex == self.in_tune):
            self.set_area_exit_as_unusable(regex)
            self.character.SUCCESSFUL_GO = False
            self.mudReaderHandler.MudReaderThread.CHECK_GO_FLAG = 0
        elif (regex == self.you_see_the):
            name = M_obj.group(2)
            description = M_obj.group(3)
            health = M_obj.group(4)
            level = M_obj.group(5)

            self.catalog_monster_bio(name, description, level)
        elif (regex == self.mob_aura_check):
            name = M_obj.group(2)
            aura = M_obj.group(3)

            #magentaprint("{" + M_obj.group(0) + "}", False)
            #magentaprint("{" + regex + "}", False)
            #magentaprint("'" + name + "' => '" + aura + "'",False)

            self.catalog_monster_aura(name, aura)
        elif (regex == self.not_here or regex == self.no_exit):
            #The state is confusion is usually caused by bad processing of good data (i.e. bugs)
            #The following is a set of work arounds to smoothe things out until those bugs are fixed
            if self.character.ACTIVELY_BOTTING:
                if self.character.CONFUSED:
                    if (not self.character.CAN_SEE):
                        self.commandHandler.process('c light') #look around to stop the "you don't see that here bug"

                    #clear the attacking list
                    self.character.MOBS_ATTACKING = []

                    self.commandHandler.process('l') #look around to stop the "you don't see that here bug"
                else:
                    self.character.CONFUSED = True

            if regex == self.no_exit:
                self.character.GO_NO_EXIT = True

            self.character.SUCCESSFUL_GO = False
            self.character.TRYING_TO_MOVE = False
            self.mudReaderHandler.MudReaderThread.CHECK_GO_FLAG = 0
        #elif regex == self.teleported_away:
            #self.character.DEAD = True
        elif (regex == self.store_list):
            item_list = re.findall(self.store_item_list, M_obj.group(0))
            #magentaprint("{" + M_obj.group(0) + "}", False)
            #magentaprint("items: " + str(item_list), False)
            for item in item_list:
                item_name = item[0]
                item_size = item[1]
                item_value = item[2]

                area_item = self.catalog_item(item_name, item_size, item_value)
                self.catalog_area_store_item(area_item, self.character.MUD_AREA.area)
        else:
            magentaprint("Cartography case missing for regex: " + str(regex))

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

    #This is used when the map is complete and we already know the last_area led to this current one from the direction travelled
    def discern_location(self, area, direction_list, area_from_id, direction_from):
        discerned_area = None

        if self.character.MUD_AREA is not None:
            exit_type = ExitType.get_exit_type_by_name_or_shorthand(direction_from)

            if exit_type is None:
                exit_type = ExitType(name=direction_from)

            #if isNewExit: - this is logic we can implement once we have exit_type mapping completely bullet proof

            #magentaprint("discerning: " + str(self.character.MUD_AREA) + " against " + str(area))

            curMudArea = self.character.MUD_AREA.get_area_to_from_exit(exit_type)

            if curMudArea is not None:
                if curMudArea.compare_to_area_and_exit_list(area, direction_list):
                    self.character.MUD_AREA = curMudArea
                    discerned_area = curMudArea.area

        return discerned_area

    def draw_map(self, area_title, area_description, exit_list):
        direction_list = []
        area = Area(name=str(area_title), description=str(area_description))

        for exit in exit_list:
            exit_type = ExitType(name=str(exit))
            exit_type.map()
            direction_list.append(exit_type)

        area_from = self.character.AREA_ID
        direction_from = self.character.LAST_DIRECTION

        discerned_area = self.discern_location(area, direction_list, area_from, direction_from)

        magentaprint("cataloging: " + str(area_from) + " " + str(direction_from) + str(area))

        if discerned_area is not None:
            area = discerned_area
            magentaprint("discerned_area to be: " + str(discerned_area))
            self.character.MUD_AREA = MudArea(area)
        else:
            if area_from is not None and direction_from is not None: #if we have an area we're coming from
                area_from = Area.get_area_by_id(self.character.AREA_ID)
                direction_from = ExitType.get_exit_type_by_name_or_shorthand(direction_from)

                magentaprint(str(area_from) + " " + str(direction_from))
                
                area.map(direction_list, area_from, direction_from)
            else:
                area.map(direction_list)

            area_exits = AreaExit.get_area_exits_from_area(area)
            self.character.MUD_AREA = MudArea(area, area_exits)

        return area

    def set_area_exit_as_unusable(self, regex):
        self.character.GO_NO_EXIT = True
        self.character.SUCCESSFUL_GO = False
        self.CHECK_GO_FLAG = 0

        if self.character.ACTIVELY_MAPPING:
            try:
                area_from = self.character.AREA_ID
                exit_type = self.character.LAST_DIRECTION

                magentaprint("setting from & direction as unusable" + str(area_from) + " " + str(exit_type))
                if area_from is not None and exit_type is not None:
                    area_from = Area.get_area_by_id(area_from)
                    exit_type = ExitType.get_exit_type_by_name_or_shorthand(exit_type)
                    area_exit = AreaExit.get_area_exit_by_area_from_and_exit_type(area_from, exit_type)

                    if area_exit is not None:
                        area_exit.is_useable = False
                        area_exit.note = str(regex)
                        area_exit.save()
            except Exception:
                magentaprint("Tried to make an area exit unusuable but failed")

    def catalog_monsters(self, area, monster_list):
        try:
            for monster in monster_list:
                mob = Mob(name=monster)
                mob.map()

                # if (self.character.ACTIVELY_BOTTING):
                #     if (mob.approximate_level == None):
                #         self.commandHandler.process('l ' + monster)

                magentaprint(str(mob))

                mob_location = MobLocation(area=area, mob=mob)
                mob_location.map()

                magentaprint(str(mob_location))
        except Exception:
            magentaprint("Problem cataloging monsters", False)

    def catalog_monster_bio(self, name, description, level):
        try:
            mob = Mob(name=name)
            mob.map()
            mob.description = description.strip()

            if mob.level is None: #don't overwrite levels
                for regex in self.character.LEVEL_LIST:
                    if (re.match(regex, level)):
                        level_index = self.character.LEVEL_LIST.index(regex) - 4
                        if (level_index == -4 or level_index == 4):
                            mob.approximate_level = self.character.level + level_index
                        else:
                            mob.level = self.character.level + level_index
                            mob.approximate_level = self.character.level + level_index

                mob.save()
        except Exception:
            magentaprint("Problem cataloging monster bio")

    def catalog_monster_aura(self, name, aura):
        mob = Mob(name=name)
        mob.map()
        mob.aura = self.character.AURA_LIST.index(aura)

        mob.save()

    def catalog_path_blocker(self, path_blocker_name):
        mob = Mob(name=path_blocker_name)
        mob.map()

        if not mob.blocks_exit:
            magentaprint("Catalogged new path blocker", False)
            mob.blocks_exit = True
            mob.save()

    def catalog_loot_blocker(self, loot_blocker_name):
        mob = Mob(name=loot_blocker_name)
        mob.map()

        if not mob.blocks_pickup:
            magentaprint("Catalogged new loot blocker", False)
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
                magentaprint("Exit match: " + str(MUD_mob_str))
                return []

            MUD_exit_str = MUD_exit_str.strip()
            my_exit_regex = r"Obvious exits: (.*[\n\r]?.*)\." #added clause if the exits break onto two lines - likely this will ahve to happen for mobs too
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

        for key, value in exit_count.items():
            #magentaprint(str(key) + " : " + str(value), False)
            if (value > 1):
                count = 1
                for i,s in enumerate(exit_list):
                    if (exit_list[i] == key):
                        if count is not 1:
                            exit_list[i] += " " + str(count)
                            #magentaprint(exit_list[i], False)
                        count += 1 #I miss my i++

        return exit_list 

    def create_exit_regex_for_character(self, E_LIST):
        exit_regex = "(NEVERMATCHTHISEVEREVER)"
        if (E_LIST is not None):
            exit_regex = "(?:go )?(!?"

            for i,s in enumerate(E_LIST):
                exit_regex += "(" + str(s) + ")"

                if (i < len(E_LIST) - 1):
                    exit_regex += "|"

            exit_regex +=")"

        return exit_regex

    def parse_monster_list(self, MUD_mob_str):
        try:
            if (MUD_mob_str is None):
                return []

            MUD_mob_str = replace_newlines_with_spaces(MUD_mob_str)
            my_monster_regex = r"You see (.*)\."
            
            match_monsters = re.match(my_monster_regex, MUD_mob_str)

            if (match_monsters is None):
                magentaprint("Match monsers: " + str(match_monsters), False)
                return self.character.MONSTER_LIST

            M_LIST = [x.strip() for x in match_monsters.group(1).split(',')]

            # Trim the preceding "a" or "some" or "two," s well as the
            # trailing comma, and the 's' if it was plural and there's an 's'
            for i in range(0, len(M_LIST)):
                #M_LIST[i].ljust(0)  # this isn't doing what I thought.
                if (re.match("a ", M_LIST[i])):
                    M_LIST[i] = M_LIST[i][2:]
                elif (re.match("an ", M_LIST[i])):
                    M_LIST[i] = M_LIST[i][3:]
                elif (re.match("The ", M_LIST[i])):
                    M_LIST[i] = M_LIST[i][4:]
                elif (re.match("two ", M_LIST[i])):
                    M_LIST[i] = M_LIST[i][4:]
                    if (M_LIST[i][len(M_LIST[i]) - 3:] == "ses"):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 2]
                    elif (M_LIST[i][len(M_LIST[i]) - 1] == 's'):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 1]
                    elif (M_LIST[i][len(M_LIST[i]) - 8:] == "children"):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 3]
                    M_LIST.append(M_LIST[i])
                elif (re.match("three ", M_LIST[i])):
                    M_LIST[i] = M_LIST[i][6:]
                    if (M_LIST[i][len(M_LIST[i]) - 3:] == "ses"):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 2]
                    elif (M_LIST[i][len(M_LIST[i]) - 1] == 's'):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 1]
                    elif (M_LIST[i][len(M_LIST[i]) - 8:] == "children"):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 3]
                    for j in range(1, 3):
                        M_LIST.append(M_LIST[i])
                elif (re.match("four ", M_LIST[i])):
                    M_LIST[i] = M_LIST[i][5:]
                    if (M_LIST[i][len(M_LIST[i]) - 3:] == "ses"):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 2]
                    elif (M_LIST[i][len(M_LIST[i]) - 1] == 's'):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 1]
                    elif (M_LIST[i][len(M_LIST[i]) - 8:] == "children"):
                        M_LIST[i] = M_LIST[i][0:len(M_LIST[i]) - 3]
                    for j in range(1, 4):
                        M_LIST.append(M_LIST[i])
                commaindex = M_LIST[i].find(',')
                if (commaindex != -1):
                    M_LIST = M_LIST[:commaindex]
        except Exception:
            magentaprint("Parse monster Exception: " + str(sys.exc_info()[0]), False)
            M_LIST = []

        return M_LIST








