import random

from misc_functions import *
from bots.BotThread import *
from db.Database import *
from db.MudMap import *
from mini_bots.travel_bot import TravelBot

# bot that finds named mobs and talks to them
class TalkGrindThread(BotThread):
      def __init__(self, character=None, command_handler=None, mud_reader_handler=None,
            mud_map=None):
            super().__init__(character, command_handler, mud_reader_handler, mud_map)

            # self.travel_bot = TravelBot(self.char, self.command_handler, mud_map)
            self.talking = False
            self.target_mob = "Gorban"

            self.talk_topics = ["quest", "trouble", "reward", "griffon", "mithril", "ogre", "giant", "key"]

      def get_path_to_target_mob(self):
            # find a mob to talk to
            mob_location = MudMap.get_mob_locations_by_name(self.target_mob)
            
            # if we found a mob location and the list is not empty then get the path to that area id
            if mob_location is not None and len(mob_location) > 0:
                  # get the area id of the mob
                  area_id = mob_location[0]

                  # get the path to the area
                  path = self.mud_map.get_path(self.character.AREA_ID, area_id)

                  # if we found a path then return the path
                  if path is not None:
                        # append talk to the mob to the path
                        path.append("talk")
                        return path

      def talk_to_mob(self, topic):
            # talk to the mob about the topic in our list
            talk_command = "ask {} {}".format(self.target_mob, topic)
            self.command_handler.process(talk_command)

      def decide_where_to_go(self):
            if not self.talking:
                  # get the path to the mob
                  path = self.get_path_to_target_mob()

                  # if we found a path then return the path
                  if path is not None:
                        return path
            else:
                  # talk to the mob about all the topics in our list
                  for topic in self.talk_topics:
                        self.talk_to_mob(topic)
                        time.sleep(1)
                  
                  self.stop()
                  self.talking = False
                  return []
      
      # do go hooks for talking to a mob
      def do_go_hooks(self, exit_str):
            # if we are going to talk to a mob then set the talking flag to true
            if exit_str == "talk":
                  self.talking = True
                  time.sleep(1)
                  return True
            else:
                  return super().do_go_hooks(exit_str)