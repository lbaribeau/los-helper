
import time
import sys

from collections import Counter
from Exceptions import *
from BotReactions import *
from misc_functions import replace_newlines_with_spaces, my_list_search
from MudMap import *
from Database import *
import re

class Cartography(BotReaction):

    def __init__(self, mudReaderHandler, commandHandler, character):
        #             Title     Description        Exit list                    Monsters (opt)                    Items (opt)
        self.area = "(.+?\n\r)(\n\r.+)*?(\n\rObvious exits: .+?[\n\r]?.+?\.)\n\r(You see .+?[\n\r]?.+?\.)?[\n\r]?(You see .+?[\n\r]?.+?\.)?"
        self.too_dark = "It's too dark to see\."
        s_numbered = "( 1st| 2nd| 3rd| 4th| 5th| 6th| 7th| 8th| 9th| 10th| 11th| 12th| 13th| 14th| 15th| 16th| 17th| 18th| 19th)?"
        self.blocked_path = "The" + s_numbered + " (.+?) blocks your exit\."
        self.please_wait = "Please wait 1 more second\."
        self.cant_go = "You can't go that way\."
        self.no_exit = "I don't see that exit\."
        self.class_prohibited = "Your class prohibits you from entering there\."
        self.level_too_low = "You must be at least level 2 to go that way\."
        self.not_invited = "You have not been invited in\."
        self.not_open_during_day = "That exit is not open during the day\."
        self.not_open_during_night = "That exit is closed for the night\."
        self.no_items_allowed = "You cannot bring anything through that exit\."
        self.door_locked = "It's locked\."
        
        self.db = db

        database = SqliteDatabase(databaseFile, threadlocals=True, check_same_thread=False)
        db.initialize(database)
        db.connect()
        create_tables()
        db.close()

        super(Cartography, self).__init__([self.area,
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
            self.door_locked])

        self.mudReaderHandler = mudReaderHandler
        self.commandHandler = commandHandler
        self.Character = character

        self.good_MUD_timeout = 1.5
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex == self.too_dark:
            self.Character.AREA_TITLE = ""
            self.Character.AREA_ID = None
            self.Character.LAST_DIRECTION = None
            self.Character.EXIT_LIST = []
            self.Character.MONSTER_LIST = []
            self.Character.SUCCESSFUL_GO = True
            self.CHECK_GO_FLAG = 0
            self.Character.CAN_SEE = False
        elif regex == self.area:
            matched_groups = M_obj.groups()

            area_title = str(matched_groups[0]).strip()
            area_description = matched_groups[1] #eat the description - doesn't give the full text
            exit_list = self.parse_exit_list(matched_groups[2])
            self.Character.EXIT_REGEX = self.create_exit_regex_for_character(exit_list)

            monster_list = self.parse_monster_list(matched_groups[3])

            self.Character.AREA_TITLE = area_title #title
            self.Character.EXIT_LIST = exit_list #exits
            self.Character.MONSTER_LIST = monster_list#monster_list #mob list

            self.Character.SUCCESSFUL_GO = True #successful go should be true everytime the area parses
            self.mudReaderHandler.MudReaderThread.CHECK_GO_FLAG = 0
            self.Character.CAN_SEE = True
            if (self.Character.TRYING_TO_MOVE): #we only want to map when user input to move has been registered
                self.Character.TRYING_TO_MOVE = False #we've moved so we're not trying anymore
                if (exit_list is not []):
                    area = self.draw_map(area_title, area_description, exit_list)
                    self.catalog_monsters(area, monster_list)

                    self.Character.AREA_ID = area.id

                    self.catalog_monsters(area, monster_list)
                else:
                    self.Character.AREA_ID = None
#self.blocked_path, self.please_wait, self.cant_go, self.no_exit
        elif regex == self.blocked_path:
            self.Character.GO_BLOCKING_MOB = M_obj.group(2)
            self.Character.SUCCESSFUL_GO = False
            self.CHECK_GO_FLAG = 0
        elif regex == self.please_wait:
            magentaprint("MudReader: unsuccessful go (please wait)")
            self.Character.GO_PLEASE_WAIT = True
            self.Character.SUCCESSFUL_GO = False
            self.CHECK_GO_FLAG = 0
        elif regex == self.cant_go:
            # This one is pretty problematic... as it should never happen.
            # Means we're off course.
            #magentaprint("MudReader: unsuccessful go (you can't go that way)")
            self.set_area_exit_as_unusable()

        elif (regex == self.class_prohibited or
                regex == self.level_too_low or
                regex == self.not_invited or
                regex == self.not_open_during_day or
                regex == self.not_open_during_night or
                regex == self.no_items_allowed,
                regex == self.door_locked):
            self.set_area_exit_as_unusable(regex)

    def draw_map(self, area_title, area_description, exit_list):
        direction_list = []
        area = Area(name=str(area_title), description=str(area_description))

        for exit in exit_list:
            exit_type = ExitType(name=str(exit))
            exit_type.map()
            direction_list.append(exit_type)

        area_from = self.Character.AREA_ID
        direction_from = self.Character.LAST_DIRECTION

        if area_from is not None and direction_from is not None: #if we have an area we're coming from
            magentaprint(str(area_from) + " " + str(direction_from))
            area_from = Area.get_area_by_id(self.Character.AREA_ID)
            direction_from = ExitType.get_exit_type_by_name_or_shorthand(direction_from)
            area.map(direction_list, area_from, direction_from)
        else:
            area.map(direction_list)

        area_exits = AreaExit.get_area_exits_from_area(area)
        self.Character.MUD_AREA = MudArea(area, area_exits)

        return area

    def set_area_exit_as_unusable(self, regex):
        try:
            self.Character.GO_NO_EXIT = True
            self.Character.SUCCESSFUL_GO = False
            self.CHECK_GO_FLAG = 0

            area_from = self.Character.AREA_ID
            exit_type = self.Character.LAST_DIRECTION

            magentaprint("setting from & direction as unusable" + str(area_from) + " " + str(exit_type), False)
            if area_from is not None and exit_type is not None:
                area_from = Area.get_area_by_id(area_from)
                exit_type = ExitType.get_exit_type_by_name_or_shorthand(exit_type)
                area_exit = AreaExit.get_area_exit_by_area_from_and_exit_type(area_from, exit_type)

                if area_exit is not None:
                    area_exit.is_useable = False
                    area_exit.note = str(regex)
                    area_exit.save()
        except Exception:
            magentaprint("Tried to make an area exit unusuable but failed", False)

    def catalog_monsters(self, area, monster_list):
        try:
            for monster in monster_list:
                mob = Mob(name=monster)
                mob.map()
                mob_location = MobLocation(area=area, mob=mob)
                mob_location.map()
        except Exception:
            magentaprint("Problem cataloging monsters", False)

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
            exit_regex += "(!?"

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
                return self.Character.MONSTER_LIST

            M_LIST = [x.strip() for x in match_monsters.group(1).split(',')]

            # Trim the preceding "a" or "some" or "two," s well as the
            # trailing comma, and the 's' if it was plural and there's an 's'
            for i in range(0, len(M_LIST)):
                #M_LIST[i].ljust(0)  # this isn't doing what I thought.
                if (re.match("a ", M_LIST[i])):
                    M_LIST[i] = M_LIST[i][2:]
                elif (re.match("an ", M_LIST[i])):
                    M_LIST[i] = M_LIST[i][3:]
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