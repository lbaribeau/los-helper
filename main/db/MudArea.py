
from db.Database import *
from misc_functions import *

class MudArea():
    # An object for area that is more than the just the Peewee Area (DB object) because it also has the exits of the area
    # Area: 
    #    - id (BaseModel)     # Identifying integer (2 is chapel, 1258 is coral medi centre)
    #    - name (NamedModel)  # Area title
    #    - description      = peewee.CharField(null=True)        
    #        # Text associated with the area
    #        # (This will only be used for crawler comparisons)
    #    - is_always_dark   = peewee.BooleanField(default=False)
    #    - is_dark_at_night = peewee.BooleanField(default=False)
    #    - is_restorative   = peewee.BooleanField(default=False)
    #    - is_smithy        = peewee.BooleanField(default=False)
    #    - is_pawn_shop     = peewee.BooleanField(default=False)
    #    - is_tip           = peewee.BooleanField(default=False)
    # area_exits[]:
    #    - id (BaseModel)
    #    x (no "name")
    #    - exit_type : ie. 
    #        - id: 7, 
    #        - name: northeast
    #    - area_from  <MudArea>
    #    - area_to    <MudArea>
    #    - is_useable <Boolean>
    #    - is_hidden  <Boolean>
    #    - note       <string>
    
    area       = None
    area_exits = []

    def __init__(self, area, area_exits=None):
        if self.area is not None or area is not None:
            if self.area is None:
                self.area = area

            if area_exits is None and self.area:
                self.area_exits = AreaExit.get_area_exits_from_area(area)
            else:
                self.area_exits = area_exits
        else:
            print("MudArea init, given area is null for some awful reason.")

    @staticmethod
    def map(area_title, area_description, previous_exit_list, current_exit_list, area_from, direction_from, previous_mud_area):
        # This tries to make a DB-synced area object (Cartography sets C.MUD_AREA, calling this)
        # I mean, adds it to the DB with an identifier if it doesn't exist, or
        # looks it up in the dB
        # Note that a MudArea is a bit more than an Area, it's got an Area and it's got a list of area_exits
        area = Area(
            name        = str(area_title), 
            description = str(area_description).replace("\n\r", ' ') # Removes newlines from matched description text
        )
        # mud_area = None
        area_exits     = None
        current_direction_list = []

        for exit in current_exit_list:
            exit_type = ExitType(name=str(exit)) # Looks up the index related to the exit text (ie "north" is 5)
            exit_type.map() # This gets us the id number of the exit text
            current_direction_list.append(exit_type) # Ok now we have a list of "exits" of proper type
            # This isn't "direction" like how TrackGrind follows a list of exits
            # This is an exit list associate on one area

        discerned_area = MudArea.discern_location(
            area           ,
            previous_exit_list,
            area_from      ,
            direction_from ,
            previous_mud_area # This is the previous record of the area that we left from
            # It is used with LAST_DIRECTION which was picked up by user_move to determine where we have gone to
        )
        # Ok this follows the given direction
        # If this succeeds, we return the result
        # So if an areaexit is wrong, we don't detect it
        # Yes the idea is that the preious mud area could have a link to follow
        # It creates a MudArea using the areaid after following the current (previous) MudArea's area_exit
        # So it does assume the DB is solid, right? Yes, but there is some checking in the caller, which also has the (?)

        # A new MudArea is made below though, I think it puts the area_exits on there
        # Ok so if both links go to 1708, that's not good... and I don't see to unlink it since the descs and exits are the same...
        # Also it'd definitely presume if there was no area that we got into the same area by a different exit...
        # I guess I need to tell it to make a new area node
        # I could do it in dBeaver but let's do it here...
        # Suppose we say "newarea south"... would that break anything... hopefully not... 

        # Let's just assume that Cartography wants us to figure this out... if we can...
        # Only the human seems to be able to know that a new node is needed
        # So... we could skip Cartography or "tell" it... last time I thought I'd write a command to delete an exit,
        # I ended up not because I was able to get Cartography to figure out... but not this time, so...
        # Could just make the command this time for that reason... either way is possible but a new "flag" variable would be needed...
        # Not about that lately
        # I mean I guess we could presume that if the water sprite is there it's a new node... or we could just do dBeaver manually
        # I think a new node command would be good...

        # Ok well hmph not sure how TRYING_TO_MOVE is true on login hmmm

        if discerned_area is not None:
            area = discerned_area.area
        else:
            if area_from is not None and direction_from is not None: #if we have an area we're coming from
                area_from = Area.get_area_by_id(area_from)
                direction_from = ExitType.get_exit_type_by_name_or_shorthand(direction_from)
                # magentaprint("MudArea: " + str(area_from) + " " + str(direction_from))
                area.map(current_direction_list, area_from, direction_from)
            else:
                area.map(current_direction_list)
        area_exits = AreaExit.get_area_exits_from_area(area)  # Ummm this should be unindented one??? Let's try it
        return MudArea(area, area_exits)
        # I guess .map is being used as kind of a constructor

    def find_exit(self, exit_name):
        for e in self.area_exits:
            magentaprint("Looping, looking for "+str(exit_name)+" ... " + str(e.exit_type.name))
            if e.exit_type.name == exit_name:
                magentaprint("Got it.")
                return e

    def unset_exit(self, exit_name):
        area_exit = self.find_exit(exit_name)
        magentaprint(f"MUDAREA DELETED AREA EXIT AREA TO: {area_exit.area_to}")
        area_exit.area_to = None  # NoneType object has no attribute 'area_to'
        area_exit.map()
        # self.map()

    def unset_area_exit(self, area_exit):
        magentaprint(f"Gotta set {area_exit.area_to} to None")
        area_exit.area_to = None
        ae.map()

    @staticmethod
    def discern_location(area, previous_direction_list, area_from_id, direction_from, previous_mud_area):
        # Ok here we know what exit was taken and from what area
        # So we can use that to do a db lookup to find out where we have ended up
        # We also have "direction_list" which is what is matched after "Obvious exits" (ie. an exit list)
        # But we don't use it
        # Area_from_id isn't used
        # We just use current_mud_area
        # Basically the point here is to get the next area given the current mud_area and the exit name
        # MudArea constructor gets called on the areaid from the exit
        # So I'd have called it get_mud_area(current_mud_area, exit_name)

        # The point is we want to figure out the area id based on the direction and the previous area
        # Ok previous code... I don't like because... it's kind of a global lookup for the exit type...
        # Also if I say "go tav" it's not converting to tavern
        # and I have code that can do that...

        # direction_from = self.string_match_area_exit(
        # Ehrm so we string match it...
        # What if there are a few "cave"s
        # We don't just want "cave"
        # We'll want "cave 3"

        # Ok so the direction_list is supposed to be not the previous area's exits but the current area
        # So that's why it just uses direction_from...
        # Hmmmm

        # Ok well we do get called with some blank arguments on startup, TRYING_TO_MOVE probably shouldn't be true

        if direction_from and previous_mud_area and area_from_id and previous_direction_list:
            # Ummm there's a problem, we have the previous node's direction list???
            # taken_exit_name = MudArea.string_match_exit_string([d.name for d in previous_direction_list], direction_from)
            taken_exit_name = MudArea.string_match_exit_string(previous_direction_list, direction_from) # Should work
            exit_type = ExitType.get_exit_type_by_name(taken_exit_name) # Should work
            # Ok we should have mapped the id now
            if exit_type:
                return previous_mud_area.get_area_to_from_exit(exit_type)

        # Looks at the text exits from previous area and the go command to map to an exit name
        # if not taken_exit_name:
        magentaprint("MudArea.discern_location ran into trouble")
        # Ok well as to why we are calling this when we aren't TRYING_TO_MOVE (why is it true on startup??!?!
        # If it ain't broke don't fix it????
        # Oyyyy

        # # Previous version... 
        # if previous_mud_area is not None:
        #     exit_type = ExitType.get_exit_type_by_name_or_shorthand(direction_from) # Gets the exit DB object given the exit name

        #     if exit_type is None:
        #         exit_type = ExitType(name=direction_from) # Just creates one on the spot with "direction_from" (the go command argument sent)
            
        #     return previous_mud_area.get_area_to_from_exit(exit_type) # A MudArea

        #     #if isNewExit: - this is logic we can implement once we have exit_type mapping completely bullet proof
        #     # magentaprint("MudArea discerning: " + str(cur_mud_area) + " against " + str(area))
        #     # Ok I'm a bit concerned that every "north" is 5 and it looks like we are using only that to figure out where we are

    def get_area_to_from_exit(self, exit_type):
        # Makes a MudArea from the areaid on the appropriate area_exit
        for areaexit in self.area_exits:
            if areaexit.exit_type.name == exit_type.name:
                if areaexit.area_to is not None:
                    return MudArea(areaexit.area_to)

    @staticmethod
    def set_area_exit_as_unusable(regex, area_from, exit_type):
        # Cartography calls MudArea.set_area_exit_as_unusable(regex, C.AREA_ID, C.LAST_DIRECTION)
        # So area_from is just an integer (area_id)
        # Exit_type being just an exit string works

        if area_from is not None and exit_type is not None:
            area_from = Area.get_area_by_id(area_from)
            exit_type = ExitType.get_exit_type_by_name_or_shorthand(exit_type)
            area_exit = AreaExit.get_area_exit_by_area_from_and_exit_type(area_from, exit_type)

            if area_exit is not None:
                area_exit.is_useable = False
                area_exit.note = str(regex)
                area_exit.save()

    def get_exit_name_to_areaid(self, areaid):
        # class AreaExit(BaseModel):
        # Has:
        #     exit_type : ie. 
        #         id: 7, 
        #         name: northeast
        #     area_from <Area> # A MudArea??? No just an AREA
        #     area_to   <Area>
        #     is_useable <Boolean>
        #     is_hidden <Boolean>
        #     note <string>
        for areaexit in self.area_exits:
            if areaexit.area_to and areaexit.area_to.id == areaid or (areaid == 1 and areaexit.area_to == None):
                return areaexit.exit_type.name

    def compare_to_area_and_exit_list(self, area, exit_list):
        matchFound = True

        if self.area.name == area.name and len(exit_list) <= len(self.area_exits):
            for areaexit in self.area_exits:
                if not areaexit.is_hidden:
                    matchedExit = False
                    for exit in exit_list:
                        if exit.name == areaexit.exit_type.name:
                            matchedExit = True
                            break
                    if not matchedExit:
                        matchFound = False
                        break
        else:
            matchFound = False

        return matchFound

    def to_string(self):
        return str(self.area) + str(self.area_exits)[1:-1]  # I think this strips off the [ and ], otherwise, self.area_exits would look like a list

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

    def pretty_string(self):
        # return f"Area: {str(self.area)},"+ '\nArea Exits '.join(Area Exits: {str(s) for s in self.area_exits)}"
        # return f"Area: {str(self.area)},"+ '\nArea Exit: '+'\nArea Exit n: '.join(str(s) for s in self.area_exits)
        # return "AreaExit ... : \n" + \
        #     "    .id             : " + str(self.id)             + "\n" + \
        #     "    .exit_type.id   : " + str(self.exit_type.id)   + "\n" + \
        #     "    .exit_type.name : " + str(self.exit_type.name) + "\n" + \
        #     "    .area_from.id   : " + str(self.area_from.id)   + "\n" + \
        #     "    .area_to.id     : " + str(self.area_to.id)     + "\n" + \
        #     "    .is_useable     : " + str(self.is_useable)     + "\n" + \
        #     "    .is_hidden      : " + str(self.is_hidden)      + "\n"
        return f"Area : \n"+\
            "    .area.id : " + str(self.area.id) + "\n"+ \
            "    .area_exits[] (len: " + str(len(self.area_exits)) + ")" + \
            "\n        ".join(str(s) for s in self.area_exits)

    def pretty_string2(self):
        return "MudArea : \n"+\
            "    .area.id : "  + str(self.area.id) + "\n"+ \
            "- ".join(ae.pretty_string() for ae in self.area_exits)
            # "Exits: \n"+\

    def shorter_map_node_string(self):
        return f"MudArea {self.area.id} exits: \n- "+\
            "\n- ".join(ae.shorter_pretty_string() for ae in self.area_exits) + "\n"

    @classmethod
    def string_match_exit_string(cls, exit_string_list, go_argument_from):
        # Ehmmm copying code.... see also "string_match_area_exit"
        # This version is for simple strings... without making AreaExits... DB-connected objects
        # I think copying the function is okay... there is way more to do if we are dealing with the DB (ie. "cave 3")

        # area_exits.sort(key=lambda areaexit: areaexit.exit_type.name) # .name should be inherited from NamedModel... or .to_string()... should be the exit text
        exit_string_list = sorted(exit_string_list)
        # magentaprint(f"Obvious exits: {[ae.exit_type.name for ae in area_exits]}")
        magentaprint(f"String match exit string: {exit_string_list}")
        if go_argument_from in ['d', 'do']:
            for e in exit_string_list:
                if e  == 'down':
                    return e
            return None
        if go_argument_from == 'sw':
            go_argument_from = 'southwest'
        elif go_argument_from == 'nw':
            go_argument_from = 'northwest'
        elif go_argument_from == 'se':
            go_argument_from = 'southeast'
        elif go_argument_from == 'ne':
            go_argument_from = 'northeast'

        # Do some processing on go_argument_from... try to make sure it's a proper reference we can use against exit list
        ref = go_argument_from
        if len(ref.split(' ')) >= 2:
            try:
                refw, n = ref.split(' ')[0], int(ref.split(' ')[1])
            except ValueError:
                # ValueError could be that the integer conversion didn't work
                # Example: "go mine shaft". Probably should fix GoTo to not do that...
                refw, n = ref.split(' ')[0], 1 
        else:
            refw, n = ref, 1

        # Ok this part might be different from the DB, since, in the DB, it'd be "cave 3"
        # I think that what we need to do is make a REFERENCING LIST
        # RL = ReferencingList(exit_string_list)
        # exit_string = RL.get(go_argument_from)
        # Alright well there is a PROBLEM
        # Which cave?
        # If we just return "cave" what good will that be to the caller
        # Yeah caller doesn't want "cave" caller wants "cave 3" right now (discern location)
        # Ok fair... so... just like the other function ("string_match_area_exit")... let's expand "cav" to "cave" and go from there
        # Uncomment above if block

        # Expand "cav" to "cave" (for example):
        # (Find it in exit_string_list with startswith and just expand based on the first one...)
        # (ignore cavern collision problem)
        # for e in [x.exit_type.name for x in exit_string_list]:
        for e in exit_string_list:
            if e.startswith(refw):
                refw = e.split(' ')[0]
                break

        if n == 1:
            exit_ref = refw
        else:
            exit_ref = refw+' '+str(n) # ie "cave 3"

        return exit_ref # So this'll be like "cave 3" ... so we haven't used "AreaExit"s... we made an equivalent string... how ExitType.name does it

        # for e in exit_string_list:
        #     if e.exit_type.name == db_exit_name:
        #         return e

    @classmethod
    def string_match_area_exit(cls, area_exits, go_argument_from):
        # Wrote this into Cartography first
        # Ok we are given a direction (argument to go command) and a list of "area exits" so we want to return the one that is correct

        area_exits.sort(key=lambda areaexit: areaexit.exit_type.name) # .name should be inherited from NamedModel... or .to_string()... should be the exit text
        magentaprint(f"Obvious exits: {[ae.exit_type.name for ae in area_exits]}")
        if go_argument_from in ['d', 'do']:
            # These refer to 'down' unequivically and won't actually work on 'door', so we have to return None to prevent returning door
            for ae in area_exits:
                if ae.exit_type.name == 'down':
                    return ae
            return None
        # I think "up" and "u" will be ok because they string match with "up"
        # This code is not very concise
        if go_argument_from == 'sw':
            go_argument_from = 'southwest'
            # for ae in area_exits:
            #     if ae.exit_type.name == 'southwest':
            #         return ae
        elif go_argument_from == 'nw':
            go_argument_from = 'northwest'
            # for ae in area_exits:
                # if ae.exit_type.name == 'northwest':
                    # return ae
        elif go_argument_from == 'se':
            go_argument_from = 'southeast'
            # for ae in area_exits: 
                # if ae.exit_type.name == 'southeast':
                    # return ae
        elif go_argument_from == 'ne':
            go_argument_from = 'northeast'
            # for ae in area_exits:
                # if ae.exit_type.name == 'northeast':
                    # return ae
        # Alright now how about "c 3" can we get "cave 3"???
        # Do we need a referencing list?
        # Why not?
        # RL=ReferencingList(area_exits)
        # return RL.get(go_argument_from) # Interprets go_argument_from as a "reference", such as in for exambple "go cav 3"
        # return ReferencingList(area_exits).get(go_argument_from) # Interprets go_argument_from as a "reference", such as in for example "go cav 3"
        # return ReferencingList([ae.exit_type for ae in area_exits]).get(go_argument_from)

        # return area_exits[ReferencingList([ae.exit_type for ae in area_exits]).index(go_argument_from)] 
            # Makes a parallel array because ReferencingList needs .name,
            # Uses referencingList.index to find the appropriate item
            # Indexes the parallel array to get the right area_exit out
            # The point here is for "goto" to still work even though we've walked through the dark
        # Why did I get None??!

        # Why not copy code from referencing_list.index() (trigger warning)
        # Ok turns out there are some differences so can't run the same code... similar algorithm though
        # Ok this is checking the integrity of the input... also, we'll put a "1" if there's no "1"
        # Make it into a proper reference... one string one number
        ref = go_argument_from
        if len(ref.split(' ')) >= 2:
            try:
                refw, n = ref.split(' ')[0], int(ref.split(' ')[1])
            except ValueError:
                refw, n = ref.split(' ')[0], 1 # Example: "go mine shaft". Probably shouldn't have goto do that anyway 
        else:
            refw, n = ref, 1

        # Ok well we don't have cave, cave, cave, cave from the DB
        # We have cave, cave 2, cave 3... 
        # Not sure how good or bad that is but
        # We can assume that...
        # So let's start by extending "c" to cave?
        # It wouldn't give us caverns would it
        # That would be bananas
        # "c 7" would have to hit cavern
        # Let's just not handle that

        # This code assumes cave, cave, cave in the db so it's no good... counting 'cave' won't help because in the DB it's saved as cave, cave 2, cave 3
        # index=None
        # for name_from_list in sorted(list(set(x.exit_type.name for x in area_exits))):
        #     magentaprint("Cartography RefList name_from_list: %s, list.count(obj): %s" % (name_from_list, str(area_exits.count(name_from_list))))
        #     if any(w.startswith(refw) for w in name_from_list.split(' ')):
        #         # If any of the words of the thing in the list start with "refw", we could have a hit, if "n" is low enough
        #         if n <= area_exits.count(name_from_list):
        #             magentaprint("Cartography RefList.index returning " + str(area_exits.index(name_from_list)+n-1))
        #             # return area_exits.index(name_from_list) + n - 1 # Returns index of item given by ref
        #             index = name_from_list + n - 1 # Returns index of item given by ref
        #         else:
        #             n = n - area_exits.count(name_from_list) # Reduces "n" and continues
        # Above code assumes cave, cave, cave but it's cave, cave 2, cave 3, so... gotta modify it
        # if index:
        #     area_exits...
        # exit_list = [x.exit_type.name for x in area_exits]
        # exit_list = area_exits

        # Lengthen "c" to "cave" by looking through area_exits to find "cave"
        for e in [x.exit_type.name for x in area_exits]:
            if e.startswith(refw):
                refw = e.split(' ')[0] # Assumes there's nothing like "cavern"... that first hit is true
                break

        # Now use "cave 3" to get the AreaExit, which is what we want to return
        # First, though, handle the case n == 1 because there shouldn't be "cave 1"
        if n == 1:
            db_exit_name = refw
        else:
            db_exit_name = refw+' '+str(n) # ie "cave 3"

        for e in area_exits:
            if e.exit_type.name == db_exit_name:
            # if e.exit_type.name.startswith(db_exit_name): # We don't need startswith now because we extended the term
                return e

        # Ok well the problem is now that in the DB it's actually "cave 3"
        # So we just need to extend "c" to "cave"
        # I wonder how it got saved that way

        # Below code was good but didn't handle cave 3
        # (Now we end the same way)
        # for ae in area_exits:
        #     # Suppose "go n" and north and northwest exist, north sorts first so we'll correctly get north
        #     if ae.exit_type.name.startswith(go_argument_from):
        #         return ae

        # Ehrm I find I have to type the whole exit name for it to map... I guess that's fine...




