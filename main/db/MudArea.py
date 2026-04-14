from db.Database import *
from misc_functions import *

class MudArea():
    # An object for area that is more than the just the Peewee Area (DB object) because it also has the exits of the area
    # Area: 
    #    - id (BaseModel)
    #    - name (NamedModel)
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
    #    - area_from <MudArea>
    #    - area_to   <MudArea>
    #    - is_useable <Boolean>
    #    - is_hidden <Boolean>
    #    - note <string>
    
    area = None
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
    def map(area_title, area_description, exit_list, area_from, direction_from, cur_mud_area):
        # This tries to make a DB-synced area object (Cartography sets C.MUD_AREA, calling this)
        # I mean, adds it to the DB with an identifier if it doesn't exist, or
        # looks it up in the dB
        area = Area(
            name        = str(area_title), 
            description = str(area_description).replace("\n\r", ' ') # Removes newlines from matched description text
        )
        # mud_area = None
        area_exits     = None
        direction_list = []

        for exit in exit_list:
            exit_type = ExitType(name=str(exit)) # Looks up the index related to the exit text (ie "north" is 5)
            exit_type.map() # This gets us the id number of the exit text
            direction_list.append(exit_type) # Ok now we have a list of "exits" of proper type
            # This isn't "direction" like how TrackGrind follows a list of exits
            # This is an exit list associate on one area

        discerned_area = MudArea.discern_location(
            area           ,
            direction_list ,
            area_from      ,
            direction_from ,
            cur_mud_area # This is the previous record of the area that we left from
            # It is used with LAST_DIRECTION which was picked up by user_move to determine where we have gone to
        )

        if discerned_area is not None:
            area = discerned_area.area
        else:
            if area_from is not None and direction_from is not None: #if we have an area we're coming from
                area_from = Area.get_area_by_id(area_from)
                direction_from = ExitType.get_exit_type_by_name_or_shorthand(direction_from)
                # magentaprint("MudArea: " + str(area_from) + " " + str(direction_from))
                area.map(direction_list, area_from, direction_from)
            else:
                area.map(direction_list)
        area_exits = AreaExit.get_area_exits_from_area(area)  # Ummm this should be one to the left??? Let's try it
        return MudArea(area, area_exits)
        # I guess .map is being used as kind of a constructor

    @staticmethod
    def discern_location(area, direction_list, area_from_id, direction_from, cur_mud_area):
        # Ok here we know what exit was taken and from what area
        # So we can use that to do a db lookup to find out where we have ended up
        # We also have "direction_list" which is basically what is matched after "Obvious exits" (ie. an exit list)
        # But we don't use it
        # Area_from_id isn't used
        # We just use current_mud_area
        # Basically the point here is to get the next area given the current mud_area and the exit name
        # MudArea constructor gets called on the areaid from the exit
        # So I'd have called it get_mud_area(current_mud_area, exit_name)

        discerned_area = None

        if cur_mud_area is not None:
            exit_type = ExitType.get_exit_type_by_name_or_shorthand(direction_from) # Gets the exit DB object given the exit name

            if exit_type is None:
                exit_type = ExitType(name=direction_from)
            
            discerned_area = cur_mud_area.get_area_to_from_exit(exit_type)

            #if isNewExit: - this is logic we can implement once we have exit_type mapping completely bullet proof

            # magentaprint("MudArea discerning: " + str(cur_mud_area) + " against " + str(area))

            # Ok I'm a bit concerned that every "north" is 5 and it looks like we are using only that to figure out where we are

        return discerned_area

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

    def get_area_to_from_exit(self, exit_type):
        for areaexit in self.area_exits:
            if areaexit.exit_type.name == exit_type.name:
                if areaexit.area_to is not None:
                    return MudArea(areaexit.area_to)

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







