
from bots.GrindThread import GrindThread
# This should help the bot find itself if it gets after a chase from TrackGrind.  

# The chase-from area id is given and is one node away.  However, we don't know the exit to take to return.  
# This bot wanders around until it finds the node it came from.  It'll follow normal grindy engagement rules.


# (chase node)  -------->  (secondary node)
# (chase aid )             
#       |
# (chase-from node)
# (chase_from aid)

# -----> dotted line is a wrong try on an exit (we tried an exit to find our way back and it didn't get us back)
# At this point we're too far 
# Ummm this is pretty difficult.
# The 'secondary node' rabbit hole could go indefinitely...
# We should rely on exit name pairs n/s e/w
# That gets complicated.
# We could not chase w/o map.  We could only chase on directions.  
# Yea... I think we should only chase with map.  It's the only thing that makes sense.  In the future, 
#  we'll have a very good map, so that will satisfy.

class FindNearbyNode(GrindThread):
    def __init__(self, character, commandHandler, mudReaderHandler, mud_map, chase_from_aid):
        super().__init__(character, commandHandler, mudReaderHandler, mud_map)
        magentaprint('GrindThread.find_nearby_node()')
        primary_aid = self.character.AREA_ID
        self.one_node_away = True
        self.two_nodes_away = False
        self.primary_exit_list = self.character.EXIT_LIST
        self.secondary_exit_list = None

    def run(self):
        # TrackGrind can call run directly since it doesn't need to make a thread.
        for i in range(0:len(self.character.EXIT_LIST))
            # Ehrm, can't loop through something that will be rewritten
            if self.one_node_away:
                direction_list.push('exit0')

    def decide_where_to_go(self):
        # We have to use a lot of state information here to pull this off...
        # Algorithm: we iterate through the exits
        #  If an exit doesn't get us to our desination, we have to work pretty hard to get back.
        self.exit_number = -1
        self.seconday_exit_number = -1
        if self.one_node_away:
            self.exit_number++
            return self.primary_exit_list[self.exit_number]
            # Do we have to assume successful go?  We'd better not, that's too bold.  We have to work with the hooks.
        elif self.two_nodes_away:

    def do_on_successful_go(self):
        if self.character.AREA_ID == self.
        self.one_node_away = False
        self.two_nodes_away = True
