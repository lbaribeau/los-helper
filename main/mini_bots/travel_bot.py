
# from bots.GotoThread import GotoThread
from mini_bots.mini_bot import MiniBot
from misc_functions import magentaprint
from threading import Thread

class TravelBot(MiniBot):
    # This bot can kill enemies on the way

    def __init__(self, char, command_handler, mud_reader_handler, map):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        self.mrh = mud_reader_handler
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
        self.thread = Thread(target=self.go_to_area, args=area_to_id)
        self.thread.start()

    def follow_path(self, path, grinding=False):
        for exit in path:
            if self.stopping:
                return

            if grinding:
                self.clean_out_node()  # Needs to check mob level and player health

            self.command_handler.go.execute_and_wait(exit)

            if self.command_handler.go.success:
                pass
            else:
                raise Exception("TravelBot failed go!")

    def clean_out_node(self):
        for mob in self.char.mobs.list:
            if self.should_kill(mob):
                self.command_handler.smartCombat.start_thread(mob)

    def should_kill(self, mob):
        # We want a should_kill check that relies more on the db... even for just a basic level check (not too high)
        return str(mob) in self.char.MONSTER_KILL_LIST

    def go_to_area_by_title(self, title_fragment):
        pass

    def get_directions(self, orig_aid, dest_aid):
        return self.map.get_path(orig_aid, dest_aid)

    def go_to_area(self, aid):
        path = self.map.get_path(self.char.AREA_ID, area_to_id)
        self.stopping = False
        self.follow_path(path)

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

