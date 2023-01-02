
# from bots.GotoThread import GotoThread
from mini_bots.mini_bot import MiniBot
from misc_functions import magentaprint
from threading import Thread

class TravelBot(MiniBot):
    # TODO: This bot should be able to kill enemies on the way (like muggers)
    # Maybe not - maybe it can raise an exception

    def __init__(self, char, command_handler, map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        self.map = map
        # self.goto_thread = None

    # def stop(self):
    #     magentaprint("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TravelBot.stop()")
    #     if self.goto_thread:
    #         self.goto_thread.stop()  # for go_to_area_by_id()
    #     self.stopping = True  # for follow_path()

    # def run(self, area_to_id):
    #     self.follow_path(area_to_id)
    # def start_thread(self, area_to_id):
    #     self.goto_thread = GotoThread(self.char, self.command_handler, self.mrh, self.map, area_to_id)
    #     self.goto_thread.run()
    # def go_to_area_by_id(self, area_to_id):
    #     self.start_thread(area_to_id)

    def start_thread(self, area_to_id):
        self.stopping = False
        self.thread = Thread(target=self.go_to_area, args=area_to_id)
        self.thread.start()

    def follow_path(self, path, grinding=False):
        magentaprint("--- TRAVEL_BOT.FOLLOW_PATH() ---\n" + str(path))
        go = self.command_handler.go
        self.stopping = False

        for exit in path:
            if self.stopping:
                return

            if grinding:
                self.clean_out_node()  # Needs to check mob level and player health (not implemented yet)

            go.wait_execute_and_wait(exit)

            if go.success:
                continue
            else:
                # raise Exception("TravelBot failed go!")
                # Can we assume that it failed?  Should we redo the whole path?  Let's rule out please_wait
                if go.please_wait:
                    go.wait_execute_and_wait(exit)  # Trying again should do the trick
                elif go.error:
                    # Wrong exit name... only thing to try is to rebuild the path
                    return False
                elif go.failure:
                    while go.blocked:
                        # ie. - A mugger the bot didn't want to engage due to HP.
                        #     - Gnoll bandit (rare)
                        # TravelBot needs to be able to engage enemies or trust the caller to do so.
                        # Adding gnoll bandit to kill list won't resolve this, since TravelBot doesn't refer to that.
                        # Looks like we HAVE smartCombat on us.
                        # So the question is, if we are blocked, what do we do - kill the blocker? It should be in the monster kill list...
                        #if go.M_obj(0) in self.char.MONSTER_KILL_LIST:
                        #self.command_handler.smartCombat.start_thread(go.M_obj(0).split(0))
                        # magentaprint("TravelBot engaging blocking mob!")
                        #self.command_handler.smartCombat._initialize(self.char.mobs.get_reference(go.M_obj(0)))
                        #self.command_handler.smartCombat._initialize(self.char.mobs.list.get_reference(self.char.mobs.read_match(go.M_obj))
                        #self.command_handler.smartCombat._initialize(self.char.mobs.get_reference_from_mob_match_object(go.M_obj))
                        # self.command_handler.smartCombat._initialize(self.char.mobs.get_reference(self.char.mobs.read_match(go.M_obj)))
                        # self.command_handler.smartCombat.target = self.char.mobs.get_reference(self.char.mobs.read_match(go.M_obj))
                        # self.command_handler.smartCombat.set_pot_thread = False
                        # self.command_handler.smartCombat.run()  # Calling run explicitly since we don't want to spawn a thread
                        # self.fight(self.char.mobs.get_reference(self.char.mobs.read_match(go.M_obj)))
                        self.command_handler.smartCombat.fight(self.char.mobs.get_reference(self.char.mobs.read_match(go.M_obj))) # Doesn't spawn a thread
                        magentaprint("TravelBot's smartCombat completed!")
                        go.wait_execute_and_wait(exit)
                    if go.success:
                        continue
                    else:
                        # We will try again (redoing the path), it probably won't work, then we'll raise the exception.
                        # Ehrm getting mugged on the road, the while loop worked, but we shouldn't have returned after
                        # (Added check to go.success)
                        return False # Should rebuild the path?... weapon_bot just assumes travel_bot will get us there though

        return True

    def stop(self):
        super().stop()
        self.command_handler.smartCombat.stop()

    def clean_out_node(self):
        for mob in self.char.mobs.list:
            if str(mob) in self.char.MONSTER_KILL_LIST:
                # self.command_handler.smartCombat.start_thread(mob) # Shouldn't this be a run() call
                self.command_handler.smartCombat.fight(self.char.mobs.get_reference(str(mob)))

    # def should_kill(self, mob):
    #     # We want a should_kill check that relies more on the db... even for just a basic level check (not too high)
    #     return str(mob) in self.char.MONSTER_KILL_LIST

    def go_to_area_by_title(self, title_fragment):
        pass

    def get_directions(self, orig_aid, dest_aid):
        return self.map.get_path(orig_aid, dest_aid)

    def go_to_area(self, aid):
        path = self.map.get_path(self.char.AREA_ID, aid)
        self.stopping = False
        while not self.follow_path(path) and not self.stopping:
            path = self.map.get_path(self.char.AREA_ID, aid)
            self.command_handler.go.wait_until_ready()
            self.command_handler.go.execute_and_wait(path.pop(0))
            if not self.command_handler.go.success:
                raise Exception("TravelBot aborting due to errors!")
                # Could be that AREA_ID is wrong - try doing a look.

    def get_pawn_path(self):
        try:
            paths = self.map.get_pawn_paths(self.char.AREA_ID)
        except Exception as e:
            #not a good situation - we can't find a way to the chapel from wherever we are
            #therefore we should just sit and wait here until we can go on the warpath again
            magentaprint("Exception getting pawn path.")
            magentaprint(e, False)
            raise e

        if paths:
            return misc_functions.get_shortest_array(paths)
        else:
            magentaprint("get_pawn_path() error... no exception but no path returned... make sure the DB is accessible.")
            return []

    def go_to_nearest_pawn_shop(self, grinding=False):
        self.follow_path(self.map.get_path_to_nearest_pawn_shop(self.char.AREA_ID))
    def go_to_nearest_smithy(self, grinding=False):
        self.follow_path(self.map.get_path_to_nearest_smithy(self.char.AREA_ID))
    def go_to_nearest_tip(self, grinding=False):
        self.follow_path(self.map.get_path_to_nearest_tip(self.char.AREA_ID))

# class GotoThread(BotThread):
#     def decide_where_to_go(self):
#         directions = []
#         magentaprint(str(self.character.AREA_ID) + " to " + str(self.area_to_id), False)

#         try:
#             directions = self.mud_map.get_path(self.character.AREA_ID, self.area_to_id)
#             # Hmmm... get_path returning none...
#         except Exception as e:
#             # magentaprint("I/O error({0}): {1}".format(e.errno, e.strerror))
#             magentaprint("GotoThread caught exception: " + str(e))
#             self.stop()
#             # raise e  # Not sure which exceptions we want to survive...

#         if "amethyst" in directions:
#             magentaprint(directions, False)
#             magentaprint("Path goes through limbo!")
#             return []  # This will break the bot if the db gives a path through limbo

#         if self.is_show_to:
#             magentaprint(directions, False)
#             directions = []
#             self.stop()

#         return directions

#     def do_after_directions_travelled(self):
#         self.stop()

# from bots.BotThread import *
# from misc_functions import *
# from db.MudMap import *

# class GotoThread(BotThread):
#     def __init__(self, character, commandHandler, mudReaderHandler, mud_map, area_to_id=None, is_show_to=False):
#         super().__init__(character, commandHandler, mudReaderHandler, mud_map)

#         if isinstance(area_to_id, int):
#             self.area_to_id = area_to_id
#             self.is_show_to = is_show_to
#         else:
#             magentaprint("No Area ID supplied to goto", False)

#     def decide_where_to_go(self):
#         directions = []
#         magentaprint(str(self.character.AREA_ID) + " to " + str(self.area_to_id), False)

#         try:
#             directions = self.mud_map.get_path(self.character.AREA_ID, self.area_to_id)
#             # Hmmm... get_path returning none...
#         except Exception as e:
#             # magentaprint("I/O error({0}): {1}".format(e.errno, e.strerror))
#             magentaprint("GotoThread caught exception: " + str(e))
#             self.stop()
#             # raise e  # Not sure which exceptions we want to survive...

#         if "amethyst" in directions:
#             magentaprint(directions, False)
#             magentaprint("Path goes through limbo!")
#             return []  # This will break the bot if the db gives a path through limbo

#         if self.is_show_to:
#             magentaprint(directions, False)
#             directions = []
#             self.stop()

#         return directions

#     def do_after_directions_travelled(self):
#         self.stop()

