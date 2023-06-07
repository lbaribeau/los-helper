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
            self.target_mobs = [#"Madame Zara",
                  # "Farmer Malbon",
                  #"Druid Tutor", #buggy
                  # "Bertram Dalrum",
                  "Farmer Calmor",
                  # "Dame Brethil",
                  # "Grand Master Yang-Shi", "Sensei", "Dojo Administrator",
                  # "Jerrek", "Tag", "Haelyn", "Chief Alchemist", "Caethrodyn",
                  # "Master of Ceremonies", 
                  # "Lord Tamaran", "Tario", "Lady Denlise", "Boris Ironfounder", "Tendrurn",
                  # "Floor Manager",
                  # "Saga Teacher",
                  # "Brotain","Rimark","Aldo","Horbuk","Master Monk","Volman the Inhumer","Master Artificer",
                  # "Kin'Tal","Archbishop","Tardan","Cheryn","Trantas","Gregor",
                  # "Manic Soothsayer","Elder Barthrodue","Farmer Viladin","Rancher Renstone",
                  # "Rancher Plover","Annette Plover",#"White Mage",
                  #"Barding Lord",
                  # "Farmer McDermott","Knight Errant", "Vickie",
                  #  "Matriarch Sara",
                  # "Goourd",
                  # "Lyron the Elder","Shaldena the Red","Garbo the Hobbit","Whiteblade the Barbarian",
                  # "Great Druid",
                  # "Teamleader Egan","Trent the Merchant",
                  # "Al'Sik the Carver",
                  # "Zi'Cab the Chieftan",
                  # "Vas'Polu the HawkMaster","Byr'Ula the Smith","Ha'Chans the Shaman",
                  # "Th'kit the HorseMaster",
                  # "Forest Master", "Douvan", "Queen Dalla", "Broad Leaf", "Red Crown",
                  # "Cal the Hermit",
                  # "Esrhae",
                  # "Ringmaster",
                  # "Corien", "Farside","Lord Arduis","Lady Arielle","Lady Jenlira", 
                  #  "Robar Greybeard",
                  # "Greenbough the Dryad",
                  # "Oakheart",
                  # "Winter's Watcher",
                  # "Agguedian's Simulcrum",
                  # "barbarian shaman",
                  # "shadow lich", #doesn't respond to anything afaik
            ]

            self.index = 0

            self.talk_topics = [
                  "", # empty string to talk to the mob
                  # activities
                  "quest",
                  "trouble",
                  "reward",
                  "help",
                  "advice",
                  "task",
                  "mission",
                  "job",
                  "work",
                  "adventure",
                  "explore",
                  "battle",
                  "fear",
                  "danger",
                  # leveling
                  "train",
                  "one",
                  "two",
                  "three",
                  "four",
                  "five",
                  "six",
                  "seven",
                  "eight",
                  "nine",
                  "ten",
                  "eleven",
                  "twelve",
                  "thirteen",
                  "fourteen",
                  "fifteen",
                  "sixteen",
                  "seventeen",
                  "eighteen",
                  "nineteen",
                  "twenty",
                  # mobs
                  "griffon",
                  "ogre",
                  "giant",
                  "golem",
                  "goblin",
                  "troll",
                  "orc",
                  "dragon",
                  "wyvern",
                  "zombie",
                  "undead",
                  "kobold",
                  "spider",
                  "bandit",
                  "chameleon",
                  "bugbear",
                  # things
                  "item",
                  "glade",
                  "portal",
                  "artifact",
                  "flute",
                  "mithril",
                  "adamantine",
                  "key",
                  "ore",
                  "gold",
                  "silver",
                  "copper",
                  "iron",
                  "steel",
                  "weapon",
                  "spell",
                  "armor",
                  "treasure",
                  "gem",
                  "fire",
                  "water",
                  "earth",
                  "air",
                  "wind",
                  "good",
                  "evil",
                  "dark",
                  "light",
                  # spells
                  "blind",
                  "clairvoyance",
                  "invisibility",
                  "levitate",
                  "fly",
                  "heal",
                  "poison",
                  "disease",
                  "curse",
                  "bless",
                  "heal",
                  "cure",
                  "protect",
                  "scroll",
                  "resist",
                  "restore",
                  "reveal",
                  "silence",
                  "transport",
                  "word-of-recall",
                  "sealing",
                  # places
                  "mine",
                  "cave",
                  "deep",
                  "dark",
                  "forest",
                  "mountain",
                  "dungeon",
                  "castle",
                  "tower",
                  "bog",
                  "swamp",
                  "station",
                  "inn",
                  "tavern",
                  "chapel",
                  "shop",
                  "farm",
                  "lair",
                  "nest",
                  "Amber",
                  "HighMarket",
                  "Amethyst",
                  "Farrin",
                  "Coral",
                  "Kelim",
                  "Blackstar",
                  "Halwyn",
                  "Rook",
                  "astral",
                  #races
                  "dwarf",
                  "elf",
                  "human",
                  "orc",
                  "hobbit",
                  "gnome",
                  "half",
                  # classes
                  "fighter",
                  "warrior",
                  "barbarian",
                  "mage",
                  "cleric",
                  "thief",
                  "ranger",
                  "knight",
                  "assassin",
                  "dark-knight",
                  "bard",
                  "alchemist",
                  "druid"
            ]

      def get_path_to_target_mob(self, mob):
            # find a mob to talk to
            mob_location = MudMap.get_mob_locations_by_name(mob)
            
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

      def talk_to_mob(self, mob, topic):
            # talk to the mob about the topic in our list
            first_mob_word = mob.split(" ", 2)[0]
            first_mob_word = first_mob_word.split("'", 2)[0] # cover for the apostrophe in the mob name
            talk_command = "ask {} {}".format(first_mob_word, topic)
            self.command_handler.process(talk_command)

      def decide_where_to_go(self):
            # for mob in self.target_mobs:
            if self.index >= len(self.target_mobs):
                  self.stop()
                  return []
            
            self.target_mob = self.target_mobs[self.index]
            if not self.talking:
                  magentaprint("Looking {} for mob: {}".format(self.index, self.target_mob), False)
                  # get the path to the mob
                  try:
                        path = self.get_path_to_target_mob(self.target_mob)
                  except:
                        magentaprint("Error getting path to mob, skipping: {}".format(self.target_mob), False)
                        # we can't path to this mob so skip it
                        self.index += 1
                        path = []

                  # if we found a path then return the path
                  if path is not None:
                        return path
            else:
                  magentaprint("Talking to mob: {}".format(self.target_mob), False)
                  # talk to the mob about all the topics in our list
                  for topic in self.talk_topics:
                        self.talk_to_mob(self.target_mob, topic)
                        time.sleep(0.5)
                  self.talking = False
                  self.index += 1              
            
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