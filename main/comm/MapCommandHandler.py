from misc_functions import magentaprint

class MapCommandHandler:
    def __init__(self, character, mud_map, mud_map_thread):
        self.character      = character
        # self.cartography  = cartography
        self.mudmap         = mud_map
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
        self.wait_for_map()
        magentaprint("MapCommandHandler.shorter_map_node_print()")
        magentaprint(f"\n\n{self.character.MUD_AREA.shorter_map_node_string()}")


    # def check_exit(self, given_exit):
    # 	self.wait_for_map()

    # def print_current_node(self):
    #     # self.print_node(self.cartography.AREA_ID)
    #     # Ehrm might need the database at some point!
    #     self.check_current_area()

    def print_node(self, aid):
        pass

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

