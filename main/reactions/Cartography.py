
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
            # R.go_where # maybe add this
            R.blocked_path,
            R.cant_go,
            R.open_first,
            R.please_wait, # there are more please wait regexes
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
            R.in_tune,
            R.washroom,
            R.cliff, # new... I think... cartography doesn't have to do anything... just stop waitin
            # R.occupied_area, # maybe add this
            R.not_here,
            R.loot_blocked,
            R.teleported,
            R.you_see_mob,
            R.mob_aura,
            R.store_list
            # R.ze_mob_fled,
        ]

        #self.__waiter_flag = False # Now using threading.Event
        self.__stopping = False
        # self.mudReaderHandler.register_reaction(self)
        mudReaderHandler.add_subscriber(self)

    # def wait_for_flag(self):
    #     magentaprint("Cartography.wait_for_flag()")
    #     super().wait_for_flag()

    def notify(self, regex, M):
        C=self.character
        if regex in R.too_dark:
            self.too_dark(regex, M)
        elif regex in R.area:
            self.area(M)
        elif regex in R.blocked_path:
            self.blocked_path(regex, M)
        elif regex in R.loot_blocked:
            # loot_blocker = M.group(2)
            loot_blocker = C.mobs.read_mob_name_from_regex_match(M)
            magentaprint("Cartography loot blocker blocking pickup: " + loot_blocker)
            self.catalog_loot_blocker(loot_blocker)
        elif regex in R.please_wait:
            if C.TRYING_TO_MOVE:
                self.go_please_wait(regex, M)
        elif regex in R.cant_go:
            # This one is pretty problematic... as it should never happen.
            # Means we're off course.
            # (Erhm - never say never, this triggers all the time)
            # I think it triggers in regular play
            C.SUCCESSFUL_GO = False
            self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
            self.set_area_exit_as_unusable(regex)  # TODO: Seems a little harsh... 
            if C.TRYING_TO_MOVE:
                magentaprint("Cartography: unsuccessful go (can't go that way): " + str(C.LAST_DIRECTION))
                C.TRYING_TO_MOVE = False
        elif regex in R.class_prohibited      + R.level_too_low    + R.level_too_high + \
                      R.not_open_during_day   + R.no_items_allowed + R.locked   +       \
                      R.not_open_during_night + R.not_authorized   + R.no_right +       \
                      R.cannot_force          + R.not_invited      + R.washroom + R.in_tune:
            self.set_area_exit_as_unusable(M.group(0))
            C.SUCCESSFUL_GO = False
            self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
            C.TRYING_TO_MOVE = False
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
            magentaprint("Cartography mob aura: " + C.mobs.read_mob_name_from_regex_match(M) + ', ' + M.group('aura'))
            self.catalog_monster_aura(C.mobs.read_mob_name_from_regex_match(M), M.group('aura'))
        elif regex in R.not_here + R.no_exit:
            #The state is confusion is usually caused by bad processing of good data (i.e. bugs)
            #The following is a set of work arounds to smoothe things out until those bugs are fixed
            if C.ACTIVELY_BOTTING:
                if C.CONFUSED:
                    if not C.CAN_SEE:
                        self.commandHandler.process('c light') #look around to stop the "you don't see that here bug"

                    #clear the attacking list
                    C.MOBS_ATTACKING = []
                    # self.commandHandler.process('l') #look around to stop the "you don't see that here bug"
                else:
                    C.CONFUSED = True

            if regex in R.no_exit:
                C.GO_NO_EXIT = True

            C.SUCCESSFUL_GO = False
            C.TRYING_TO_MOVE = False
            self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
        elif regex in R.teleported:
            if M.group(1) == C.name:
                C.DEAD = True
                C.AREA_ID = 82  # TODO: this id is out of sync
                C.MUD_AREA = None
        elif regex in R.store_list:
            self.store_list(regex, M)
        else:
            # This is fine for a shut door - we just want the super().notify in that case.
            magentaprint("Cartography case missing for regex: " + str(regex)) # (ze_mob_fled)
        # magentaprint("Cartography notify done on text: " + str(regex[:min(len(regex), 20)]) + '...')
        # magentaprint("Cartography notify done, got C.AREA_ID: "+str(C.AREA_ID)+", MUD_AREA: "+str(C.MUD_AREA))
        magentaprint("Cartography notify done, got C.AREA_ID: "+str(C.AREA_ID))
        super().notify(regex, M) # threading.Event

    def too_dark(self, regex, M):
        C = self.character
        magentaprint("Cartography receiving too_dark notification, previous area: " + str(C.AREA_ID)+", previous MUD_AREA:"+str(C.MUD_AREA))
        if C.AREA_ID != None:
            guessed_area = self.guess_location(C.AREA_ID, C.LAST_DIRECTION) # Ehrm this is wrong if we fled
            magentaprint("Cartography guessed area (too dark): " +str(guessed_area))

            if guessed_area != None:
                C.AREA_ID    = guessed_area.area.id
                C.AREA_TITLE = guessed_area.area.name
                C.EXIT_LIST  = guessed_area.area_exits
                C.MUD_AREA   = guessed_area
            else:
                C.AREA_ID    = None
                C.AREA_TITLE = None
                C.MUD_AREA   = None
                C.EXIT_LIST  = []

        C.mobs.list = ReferencingList([]) # Will have to deal with unknown mobs list
        C.mobs.attacking = []
        if C.mobs.chase:
            C.mobs.list.add(C.mobs.chase)
            C.mobs.attacking = [C.mobs.chase]
            # Cartography is a place that gets the notification that it's dark, and it's not the Go object,
            # so it's currently a good place to make this correction
            # The bot should now see ok a mob is attacking and there is a mob here and it can base decisions on that like
            # Ok let's fight the attacking mob then
            # By the way it also has code regarding chasing specifically
            # But we could just unset C.mobs.chase and have the bot decide ok there's an attacker
            # Better though is for it to know it chased
            # I think that by default I might make the Go object do this or we could have a Go handler and a go-between for more state handling
            # Anyway, this should help us to know if we chased into a dark room
            # But why wouldn't a chase happen in a dark room?

        C.SUCCESSFUL_GO  = True
        self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0
        C.CAN_SEE        = False
        C.CONFUSED       = False
        C.TRYING_TO_MOVE = False

    def area(self, match):
        # This is what we do when area regex matches in notify(), we are given "match" which is the regex matched text

        # magentaprint(M.group(0),False,False,True)
        magentaprint("Cartography got area match... area title: " + str(match.group(1).strip()) + 
            "\n... exit list: " + str(self.parse_exit_list(match.group(3)))+
            "\n... (number of match groups: " + str(len(match.groups()))+")"+
            "\n... group(1): " + str(match.group(1))+
            # "\n... group(2): " + str(match.group(2))+
            # "\n... group(3): " + str(match.group(3))+
            "\n... group(3): " + str(self.parse_exit_list(match.group(3))) +
            # "\n... group(4): " + str(match.group(4))+
            "\n... mobs list: " + str(ReferencingList(self.parse_monster_list(match.group(4))))+\
            # "\n... mobs group match (group(4)): " + str(match.group(4))+
            "\n... group(5): " + str(match.group(5)))
            # "\n... group(6): " + str(match.group(6))+
        C            = self.character
        C.AREA_TITLE = match.group(1).strip() 
        # Area title sometimes has issues if TRYING_TO_MOVE was set prematurely and we get rubbish prepended
        C.EXIT_LIST  = self.parse_exit_list(match.group(3))
        C.EXIT_REGEX = self.create_exit_regex_for_character(C.EXIT_LIST)
        C.mobs.list  = ReferencingList(self.parse_monster_list(match.group(4)))
        # This calls mobs.parse_mob_string
        # magentaprint("Cartography.area (id is {}) set character.mobs.list: {}".format(C.))
        # magentaprint("Cartography set character.mobs.list.list: " + str(C.mobs.list.list))
        # C.mobs.attacking = [] # TODO: match regex for entering an area where a mob is already attacking you
        ref_of_attacking_mob = C.mobs.get_ref_of_attacking_mob(match)
        if ref_of_attacking_mob:
            magentaprint("Cartography got attacking mob: " + ref_of_attacking_mob)
            C.mobs.attacking = [ref_of_attacking_mob] # Works if only one mob is attacking, and works on "look" not on "go"

        C.CAN_SEE       = True
        C.CONFUSED      = False
        C.SUCCESSFUL_GO = True #successful go should be true everytime the area parses - here we are setting it as we see Go worked
        # Better way is that "Go" command object exists now... not sure if it's used
        self.mudReaderHandler.mudReaderThread.CHECK_GO_FLAG = 0

        # C.TRYING_TO_MOVE=False # Getting DB lock error atm

        if C.TRYING_TO_MOVE:
            # I think TRYING_TO_MOVE prevents multiple saves of the area
            # Yes, and ensures that variables related to the 'from' area are present
            #if C.EXIT_LIST != []: 
            # Ehhh this was always true! ('is' tests for same object)
            # I don't think the regex will match without an exit list.
            if C.EXIT_LIST != []:
                # area = self.draw_map(area_title, area_description, C.EXIT_LIST)
                C.MUD_AREA = MudArea.map(
                    C.AREA_TITLE, 
                    match.group(2).strip(), # area description (eat the description - doesn't give the full text)
                    C.EXIT_LIST, 
                    C.AREA_ID, 
                    C.LAST_DIRECTION, # command_handler user_move() picks up to where we issued a go command
                    C.MUD_AREA # Here we are giving the PREVIOUS C.MUD_AREA, which should be a record of where we WERE
                    # This will use the direction we went and from where to find out where we are now
                ) # Creates a "MudArea" object... also interfaces with the DB... MudArea object is a bit more than an "Area" from the DB table
                # Maybe we can handle two kinds of descriptions.... hmmmm
                # Can MudArea.map handle that?
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
        mob_name = self.character.mobs.read_mob_name_from_regex_match(M)
        # magentaprint("Cartography blocking mob name: " + mob_name)
        # # self.character.GO_BLOCKING_MOB = mob_name
        self.character.GO_BLOCKING_MOB = self.character.mobs.get_ref_of_attacking_mob(M) 
            # Use a "ref" instead of a mob name (ie. which mob is attacking specifically)
            # Note: invalidated on mob arrival or departure
            # "Go" should be doing this, right? 
            # Or "Mobs?"
            # Don't worry about it...
            # But what maintains it? Let "mobs" maintain it. 
            # Letting "mobs" do other mob arrival/departure but keeping setting it here
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
        # TODO: This code should make a new item and areastoreitem if there is armour of a different size (or solve armour sizing another way) (I am entering data manually)
        magentaprint(M.group('store_list'))
        # self.store_item_re = r"\s+(?P<item>[A-Za-z']+ )+\s+(\((?P<size>[sml])\)\s+)?Cost: (?P<cost>\d+)\r\n"  
        self.store_item_re = r"\s+(?P<item>([A-Za-z']+ )+)\s+(\((?P<size>[sml])\)\s+)?Cost: (?P<cost>\d+)[\r\n]{2}"  
        # for store_item_match in re.findall(self.store_item_re, M.group('store_list') + '\r\n'):
        for imatch in re.finditer(self.store_item_re, M.group('store_list') + '\r\n'):
            area_item = self.catalog_store_item(
                self.character.inventory.remove_a_an_some(imatch.group('item').strip()), 
                str(imatch.group('size')), 
                int(imatch.group('cost')))
            magentaprint(
                'Cartography store_list catalog_store_item parsed: ' + self.character.inventory.remove_a_an_some(imatch.group('item').strip()) + \
                ', size: ' + str(imatch.group('size')) + \
                ', cost: ' + imatch.group('cost') + \
                '. Got item id: ' + str(area_item.id))
            self.catalog_area_store_item(area_item, self.character.AREA_ID)
            # item_list = re.findall(self.store_item_list, M.group(0))
            # magentaprint("{" + M.group(0) + "}", False)
            # magentaprint("items: " + str(item_list), False)
            # for item in item_list:
            #     item_name = item[0]
            #     item_size  = item[1]
            #     item_value = item[2]
        # Solution is - have the data accurately in the dB
        # And have the bot decide whether it should buy it
        # (ie if you don't want to buy something)

        # for imatch in re.finditer(self.store_item_re, M.group('store_list') + '\r\n'):
        #     # Redo loop for print readability
        #     magentaprint("Cartography mapped asi area/ item: {}/{}".format(asitem.area.id, asitem.item.id))

        # Ehrm cost not getting uploaded?? Not sure why not maybe since the record exists already?

        # Could do an "if" on "size" above

    #Used if it's dark and / or the current area doesn't appear to be findable
    def guess_location(self, area_from_id, direction_from):
        C=self.character
        guessed_area = None
        magentaprint(f"Cartography.guess_location({area_from_id}, {direction_from}), current MUD_AREA: {C.MUD_AREA}")

        # Suppose we have "go b" for boulder
        # Would be better to use the exit that is on MUD_AREA instead of doing a global lookup
        # boulder doesn't come up with "go b"
        # Using startswith can get backroom
        # The bot doesn't shorten exits so it's fine

        if C.MUD_AREA != None:
            exit_type = ExitType.get_exit_type_by_name_or_shorthand(direction_from)
            # "ExitType" is an exit, like "north", but every "north" has the same ID, so we are just doing that lookup based on the go text we have

            if exit_type == None:
                exit_type = ExitType(name=direction_from) # Create an Exit if we didn't get one

            guessed_area = C.MUD_AREA.get_area_to_from_exit(exit_type)
            # MUD_AREA is an object for the current area
            # It's going to check its exits to see if it has a match for what we are giving it

            # Commenting code that appears to do nothing... (guessedArea already equals the same thing)
            # curMudArea   = C.MUD_AREA.get_area_to_from_exit(exit_type)

            # if curMudArea != None:
            #     #check if curMudArea can be dark
            #     guessed_area = curMudArea

        return guessed_area

    def set_area_exit_as_unusable(self, regex):
        self.character.GO_NO_EXIT = True
        self.character.SUCCESSFUL_GO = False
        self.CHECK_GO_FLAG = 0

        if self.character.ACTIVELY_MAPPING:
            try:
                MudArea.set_area_exit_as_unusable(
                    regex, 
                    self.character.AREA_ID, 
                    self.character.LAST_DIRECTION
                )
            except Exception:
                magentaprint("Tried to make an area exit unusuable but failed")

    def catalog_monsters(self, area, monster_list):
        try:
            magentaprint("Cartography catalog_monsters() monster_list: " + str(monster_list)) #mob_location id {0}, {1}".format(mob_location, mob.name))
            for monster in monster_list:
                mob = Mob(name=monster)
                mob.map()

                if self.character.ACTIVELY_BOTTING:
                    if mob.approximate_level == None:
                        self.commandHandler.process('l ' + monster)

                # magentaprint(str(mob))

                mob_location = MobLocation(area=area, mob=mob)
                mob_location.map()

                # magentaprint("Cartography catalog_monsters() mob_location id {0}, {1}".format(mob_location, mob.name))
        except Exception:
            magentaprint("Problem cataloguing monsters", False)

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
            magentaprint("Problem cataloguing monster bio")

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
            magentaprint("Cartography catalogued new path blocker", False)
            mob.blocks_exit = True
            mob.save()

    def catalog_loot_blocker(self, loot_blocker_name):
        mob = Mob(name=loot_blocker_name)
        mob.map()

        if not mob.blocks_pickup:
            magentaprint("Cartography catalogued new loot blocker", False)
            mob.blocks_pickup = True
            mob.save()

    def catalog_store_item(self, item_name, item_size, item_value):
        item = Item(name=item_name, value=item_value, description=item_size) # Peewee implements the constructor with args/kwargs according to the database
        # Ok so the code actually does rely on the description to have size(!!??)
        # Yes it doesn't actually use the ItemType field
        # (Cartography store_item)
        if item_size and item_size != "None":
            # Yes, it can come in as str(None)
            item.map_given_name_and_description() # Queries on more than just the item name
        else:
            item.map() # Any item without a size, gets item_size "None" at this point
        return item
        # Ehrm should we use description for size? We could
        # I don't think that how ItemType works is coded up anywhere


    def catalog_area_store_item(self, item, area):
        asitem = AreaStoreItem(area=area,item=item)
        # magentaprint("Mapped asi area, item, model (ie. size/sharp): {},{},{}".format(asitem.area.id, asitem.item.id, asitem.item.itemtype.model)) # itemtype was none
        # magentaprint("Cartography mapped asi area/ item: {}/{}".format(asitem.area.id, asitem.item.id))
        asitem.map()

    def parse_exit_list(self, MUD_exit_str):
        try:
            if MUD_exit_str is None:
                magentaprint("Cartography exit match: " + str(MUD_mob_str))
                return []

            MUD_exit_str = MUD_exit_str.strip()
            my_exit_regex = r"(?s)Obvious exits: (.+?)\." #added clause if the exits break onto two lines - likely this will ahve to happen for mobs too
            match_exits = re.match(my_exit_regex, MUD_exit_str)
            E_LIST = [x.strip() for x in match_exits.group(1).split(',')]
            #technique above is referred to as list comprehension see:
            #http://stackoverflow.com/questions/501308/problem-in-understanding-python-list-comprehensions/501323#501323

            E_LIST = self.number_exits(E_LIST)
            # magentaprint("parse_exit_list got exit list " + str(E_LIST))
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
        if E_LIST != None:
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

