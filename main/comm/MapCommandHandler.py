from misc_functions import magentaprint
from db.Area import Area
from db.ExitType import ExitType
from db.AreaExit import AreaExit 
from db.MudArea import MudArea

class MapCommandHandler:
    def __init__(self, character, mud_map, mud_map_thread):
        self.character      = character
        # self.cartography  = cartography
        self.mud_map        = mud_map
        self.mud_map_thread = mud_map_thread

    def wait_for_map(self):
        magentaprint("MapCommandHandler.wait_for_map()")
        self.join_thread(self.mud_map_thread)
        # Doesn't work... call command_handler.join_mud_map_thread()

    def join_thread(self, thread):
        if thread and thread.is_alive():
            thread.join(10)

    def write_map(self):
        magentaprint("MapCommandHandler.write_map()")
        self.wait_for_map()
        # I didn't need this... fixed Cartography auto write

    def fix_current_node(self, go):
        # I didn't need this... fixed Cartography auto write
    	# Looks at current exits for a None
    	# Takes that exit to get area text and writes DB
    	mudarea=self.character.MUD_AREA
    	e = None
    	for exit in mudarea.area_exits:
    		if hasattr(exit, 'area_to') and exit.area_to == None:
    			e = exit
    			break

    	if not e:
    		return False

    	exit_list = ReferencingList([e.name for e in mudarea.area_exits])

    	# go.execute_and_wait(e.name.split(' ')[0])
    	go.execute_and_wait(exit_list.get_first_reference(e.name))
    	# EHERMRMEMRE not sure why this doesn't save already???
    	# Is it because the things already exist partially?
	    	        #     "    .area_to.id     : " + str(self.area_to.id)     + "\n" + \

    def check_current_area(self):
    	# Ok I think that this is good...
        self.wait_for_map()
        magentaprint("MapCommandHandler.check_current_area()")
        # Suppose I enter "mapcheck northeast"
        # Just give me back an areaid
        # mudarea=self.character.MUD_AREA
        # magentaprint("Assuming current character mud area: " + str(mudarea))
        # magentaprint("Assuming current character mud area: " + str(mudarea.area.id))
        # magentaprint(f"Pretty string:\n{mudarea.pretty_string()}")
        # if hasattr(mudarea, 'area'):
        # 	magentaprint(f"Has area: {mudarea.area}")
        # else:
        # 	magentaprint(f"No area attribute!")

        # magentaprint(f"Pretty string 2: \n{mudarea.pretty_string2()}")
        magentaprint("\n\n"+self.character.MUD_AREA.pretty_string2() if hasattr(self.character.MUD_AREA, 'pretty_string2') else "\n\n<None>")

        # if hasattr(mudarea, 'area_exits'):
        #     # magentaprint("Has exits: " + str([ae.exit_type.name for ae in mudarea.area_exits]))
        #     # magentaprint(": " + str(mudarea))
        #     for ae in mudarea.area_exits:
        #         if ae and hasattr(ae, 'area_to') and ae.area_to and hasattr(ae.area_to,'id') and hasattr(ae.area_to, 'name'):
        #             magentaprint(f"Exits go to... {ae.exit_type.name} -> id: {ae.area_to.id}, name: {ae.area_to.name}")
        #             # magentaprint("Pretty string: \n" + ae.pretty_string())
        #             magentaprint("\n"+ae.pretty_string())
        #         else:
        #             magentaprint(f"Incomplete!: {ae}")
        # else:
        #     magentaprint(f"No area_exits attribute!")
    def shorter_map_node_print(self):
        magentaprint("MapCommandHandler.shorter_map_node_print()")
        if self.character.MUD_AREA != None:
            self.wait_for_map()
            magentaprint(f"\n\n{self.character.MUD_AREA.shorter_map_node_string()}")
        else:
            magentaprint("MUD_AREA is None!")

    # def check_exit(self, given_exit):
    # 	self.wait_for_map()

    # def print_current_node(self):
    #     # self.print_node(self.cartography.AREA_ID)
    #     # Ehrm might need the database at some point!
    #     self.check_current_area()

    def print_node(self, aid):
        pass

    def showcrawl2(self):
    	# Try showing precessors to areaid 1
    	magentaprint([n for n in self.mud_map.get_predecessors(1)])

    def make_new_area_node(self, exit_string_partial, character, go_command, cartography):
        # Suppose we have nodes with identical description and exit that only the human knows needs to be a new node
        # (Would be pretty hard to get the bot to figure out whether or not a node is a different node with everything the same)
        # So let's make a human runnable command to make a node 
        # It should map the current area and given area exit and make the node based on the text that comes in 
        C=character
        go=go_command
        prev_mudarea = C.MUD_AREA
        prev_area_id_from = C.AREA_ID
        # exit_string_partial = args[0] # User command to make a new node in this direction
        exit_string = cartography.string_match_area_exit(C.MUD_AREA.area_exits, exit_string_partial).exit_type.name
        go.execute_and_wait(exit_string_partial)
        if not go.success:
            magentaprint("map command_handler make_new_area_node ran into trouble! (Go failed?!)")
            return

        # Ok.... well... presumably... who knows what Cartography did with that but, let's just ignore
        # It probably mapped our exit to the existing wrong node...
        # I feel we need to ...

        # (Maybe make another object to do this... mapcommandhandler)
        # - make new area node
        # -- set the area title and description obviously
        # -- also the area exits of the new node (obvious exits)
        # - make new "area_exit"
        # - map the exit name to exit_type
        # - set all the fields of the area... restorative, hidden etc.... some defaults (all False)
        # - Use prev_mudarea, get the exit on it, and tie it to a new Mud_area
        # Save the new mud_area
        # 
        # Yeah could we just... kind of... do it in python and call peewee save...
        # We know Cartography didn't make a new area, it probably linked to the existing area...
        # Hopefully we don't run into more trouble since there is a query that could return both areas now (duplicate title and description)
        # That query should also consider obvious exits but the problem has to be handled anyway in case those are the same too
        # Maybe make a function... it'll need
        # -- area title
        # -- area description
        # -- obvious exits (strings)
        # -- from-node id or maybe MUD_AREA object
        # -- from-node-exit name or area_exit object
        # -- (db access)
        # Also, let's delegate to map_command_handler... 
        # self.map_command_handler = MapCommandHandler(self.character, self.mud_map, self.mud_map_thread)

        # area_title = C.AREA_TITLE
        # exit_list = C.EXIT_LIST

        # Some useful code snippets... "grep -r LAST_DIRECTION ."
		# ./comm/command_handler.py:  self.character.LAST_DIRECTION = user_input.replace('go ', '')
		# ./command/Go.py:        self.character.LAST_DIRECTION = str(target)
		# ./reactions/Cartography.py:  prev_mud_area.unset_exit(ReferencingList([ae.exit_type.name for ae in prev_mud_area.area_exits]).get(C.LAST_DIRECTION))
		# ./reactions/Cartography.py:  # prev_mud_area.unset_exit(self.string_match_area_exit(prev_mud_area.area_exits, C.LAST_DIRECTION).exit_type.name) 

		# MUD AREA code...
        # self.area_exits = AreaExit.get_area_exits_from_area_(area)
        # Area Exit code...
        # def get_area_exits_from_area_given_areaid(areaid):
        # We probably have the area exit though
        # I guess we're going to make the object up then call .save()?
        # No you don't save MUD AREAs... you save AREAs and exit lists
        # It finally happens in MUD AREA .map ... after discern location
        #         area_from = Area.get_area_by_id(area_from)
        #         direction_from = ExitType.get_exit_type_by_name_or_shorthand(direction_from)
        #         # magentaprint("MudArea: " + str(area_from) + " " + str(direction_from))
        #         area.map(direction_list, area_from, direction_from)
        #     else:
        #         area.map(direction_list)
        # area_exits = AreaExit.get_area_exits_from_area(area)  # Ummm this should be unindented one??? Let's try it
        # return MudArea(area, area_exits)
        # Maybe make a new area then?
        # My $#&*% why is this so difficult
        # Ok start with a new area... and you can't use Area.map because that searches the DB first
        # But you can just do everything it does, right?

        # Just like how MudArea.map creates an area from the title and the description!
        # Just go through Cartography and mudarea.map and use the code you need

        # new_area_id = Area.create_new_area(C.AREA_TITLE, C.AREA_DESC)
        # Code from MudArea.map...

        area = Area(
            name        = str(C.AREA_TITLE), 
            description = str(C.AREA_DESC).replace("\n\r", ' ') # Removes newlines from matched description text
        )

        obvious_exits_as_exit_type = []
        for exit in C.EXIT_LIST:
            exit_type = ExitType(name=str(exit)) # Looks up the index related to the exit text (ie "north" is 5)
            exit_type.map()                      # This gets us the id number of the exit text
            obvious_exits_as_exit_type.append(exit_type)     # Ok now we have a list of "exits" of proper type
            # This isn't "direction" like how TrackGrind follows a list of exits
            # This is an exit list associate on one area

        # Skip that bit about discerned area...
        # Assume we have area_from and direction_from

        # if area_from is not None and direction_from is not None: #if we have an area we're coming from
        area_from = Area.get_area_by_id(prev_area_id_from)
        magentaprint(f"Got previous area: {area_from}")
        # direction_from = ExitType.get_exit_type_by_name_or_shorthand(direction_from)
        db_exit_from = ExitType.get_exit_type_by_name(exit_string)

        # The "else" in MudArea is if we don't have exit_from and area_from... but we have that here

        # Ah f$#&* we can't use area.map
        # area.map(obvious_exits_as_exit_type, area_from, db_exit_from) # Can we use area.map though?!?!
        # Well area.map starts by going through the same exit type thing
        # Then does is_new_mapping which we don't want to check (it is a new mapping)

        area.save()  # Copying idea from area.map() (creates new area node... we gave it title and description above)
        
        #"now we map our area exits"
        for exit in obvious_exits_as_exit_type:
            #magentaprint("exit " + str(exit.to_string()), False)
            area_exit = AreaExit(area_from=area.id, area_to=None, exit_type=exit)
            # Nevermind opposite exit mumbo jumbo
            # if (exit_from.opposite is None):
            #     if (exit.id == exit_from.opposite.id):
            #         area_exit.map(area_from, exit_from)
            #     else:'''
            area_exit.map()
            # is_new_exit_mapping = True # Would get returned... 

        #"last but not least we want to try to update our area_from with its area_to value :)"
        # Ok same but I won't say "try" here
        # Update area_from with area_to (link last area to this area)

        # if cur_area_from is not None and cur_exit_from is not None:
        # area_exit_from = AreaExit.get_area_exit_by_area_from_and_exit_type(cur_area_from, cur_exit_from)
        area_exit_from = AreaExit.get_area_exit_by_area_from_id_and_exit_type_id(area_from.id, db_exit_from.id)
            # if (area_exit_from is not None):
                # if (area_exit_from.area_to is None): #don't overwrite values that have been
        area_exit_from.area_to = area
        area_exit_from.save()
        #magentaprint("Updating AreaExit with: \n" + area_exit_from.to_string())

        # BONUS set mud area I guess??
        # This is how MudArea.map finishes...
        area_exits = AreaExit.get_area_exits_from_area(area)  # Ummm this should be unindented one??? Let's try it
        mudarea = MudArea(area, area_exits) # I don't think I use this... hmmm... 
        magentaprint("MapCommandHandler made mudarea: {mudarea}")
        # Maybe don't bother let it be broken? We don't trust it do we...
        # Could put it onto character... (C.MUD_AREA)... maybe should... since C.MUD_AREA could actually be the wrong duplicate area!
        # Could create jank if we don't update it
        C.MUD_AREA = mudarea
        return mudarea

        # My draft code...
        # Area.set_is_always_dark(new_area_id)
        # AreaExit.map_obvious_exit(prev_mudarea.area.id, exit_string, new_area_id)

        # area_exit_taken = 

        # # Also, we can make the exits in subsequent steps
        # self.map_exit(

    def write_area_exit(self, current_area_id, exit_name_partial, cartography, area_id_to, character):
        exit_string = cartography.string_match_area_exit(character.MUD_AREA.area_exits, exit_name_partial).exit_type.name # Uses current MUD AREA
        exit_type = ExitType(name=exit_string)  # I think the way I've got my string is fine... didn't go through the parser though
        exit_type.map() # Looks up the index related to the exit text (ie "north" is 5)
        # # area_from = Area.get_area_by_id(current_area_id)
        # # AreaExit.select().where((AreaExit.area_from == area_from_id) & (AreaExit.exit_type == exit_type_id))
        # area_exit = AreaExit(area_from=current_area_id, area_to=area_id_to, exit_type=exit_type) # User better not give us crapola!
        # area_exit.map()
        # # Can't we just save the area exit????
        # # I guess we try???
        # # Did map do it??
        # # Yeah that sshouldlldldld do it I think
        # # Dangit it didn't delete the wrong one...
        # # Ok so we have to do a "get"
        area_exit = AreaExit.get_area_exit_by_area_from_id_and_exit_type_id(current_area_id, exit_type.id)
        # Let's just assume there's only one already
        area_exit.area_to = area_id_to
        area_exit.map() # Ok maybe that'll do it


#class MudArea():
    # An object for area that is more than the just the Peewee Area (DB object) because it also has the exits of the area
    # Area: 
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
    #    - exit_type : ie. 
    #        - id: 7, 
    #        - name: northeast
    #    - area_from <MudArea>
    #    - area_to   <MudArea>
    #    - is_useable <Boolean>
    #    - is_hidden <Boolean>
    #    - note <string>

