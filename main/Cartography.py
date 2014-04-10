
import time
import sys

from Exceptions import *
from BotReactions import *
from misc_functions import replace_newlines_with_spaces, my_list_search
from Database import *
import re

class Cartography(BotReaction):

    def __init__(self, mudReaderHandler, commandHandler, character):
        self.area_with_mobs = "(.*\n\r)(\n\rObvious exits: .*)\n\r(You see .*)?"
        self.db = db

        database = SqliteDatabase('map.db', check_same_thread=False)
        db.initialize(database)
        db.connect()
        create_tables()
        db.close()

        super(Cartography, self).__init__([self.area_with_mobs])

        self.mudReaderHandler = mudReaderHandler
        self.commandHandler = commandHandler
        self.Character = character

        self.good_MUD_timeout = 0.2
        self.__waiter_flag = False
        self.__stopping = False
        self.mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex == self.area_with_mobs:
            matched_groups = M_obj.groups()

            area_title = str(matched_groups[0]).strip()
            area_description = None
            exit_list = self.parse_exit_list(matched_groups[1])
            monster_list = self.parse_monster_list(matched_groups[2])

            self.Character.AREA_TITLE = area_title #title
            self.Character.EXIT_LIST = exit_list #exits
            self.Character.MONSTER_LIST = monster_list#monster_list #mob list
            self.Character.SUCCESSFUL_GO = True

            db.connect()
            area = self.draw_map(area_title, exit_list)
            self.catalog_monsters(area, monster_list)
            db.close()

            self.Character.CURRENT_AREA = area.id

    def draw_map(self, area_title, exit_list):
        direction_list = []
        area = Area(name=str(area_title))

        for exit in exit_list:
            direction = DirectionType(name=str(exit))
            direction.map()
            direction_list.append(direction)

        area.map(direction_list)#self.Character.CURRENT_AREA, self.Character.LAST_DIRECTION_MOVED

        return area

    def catalog_monsters(self, area, monster_list):
        return

    def parse_exit_list(self, MUD_exit_str):
        try:
            MUD_exit_str = MUD_exit_str.strip()
            my_exit_regex = r"Obvious exits: (.*)\."
            match_exits = re.match(my_exit_regex, MUD_exit_str)
            E_LIST = [x.strip() for x in match_exits.group(1).split(',')]
            #technique above is referred to as list comprehension see:
            #http://stackoverflow.com/questions/501308/problem-in-understanding-python-list-comprehensions/501323#501323
        except Exception:
            E_LIST = []
            magentaprint("Parse exit Exception: " + str(sys.exc_info()[0]), False)

        return E_LIST


    def parse_monster_list(self, MUD_mob_str):
        try:
            if (MUD_mob_str is None):
                magentaprint("Mob match: " + str(MUD_mob_str))
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
            magentaprint("Parse exit Exception: " + str(sys.exc_info()[0]), False)
            M_LIST = []

        return M_LIST