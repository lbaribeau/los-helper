
import time
from math import floor

from reactions.Mobs import Mobs
import misc_functions

class Character(object):
    """ This is a class that holds a bunch of data,
    mostly obtained by the MUD read thread."""
    @property
    def hp(self):
        return self.prompt.hp
    @property
    def mp(self):
        return self.prompt.mp
    @property
    def maxHP(self):
        return self.info.maxHP
    @property
    def maxMP(self):
        return self.info.maxMP
    @property
    def HEALTH(self):
        return self.hp
    @property
    def MANA(self):
        return self.mp
    def hp_maxed(self):
        return self.hp == self.info.maxHP
    def mp_maxed(self):
        return self.mp == self.info.maxMP

    def __init__(self):
        self.mobs = Mobs()

        self.race         = None
        self.title        = None
        self._class       = None
        self.class_string = None
        self.level        = None

        self.BLACK_MAGIC  = True # Could move to smart combat
        self.KNOWS_VIGOR  = True
        #WEAPON_SKILLS = [0, 0, 0, 0, 0] #sharp, thrust, blunt, pole, missile
        #MAGIC_SKILLS= [0, 0, 0, 0, 0]
        self.SKILLS = {}
        self.LEVEL_LIST = [
            "You could kill (?:.+?) with a needle\.",   #-4 or more levels
            "(?:.+?) should be easy to kill\.",         #-3 level from this character
            "(?:.+?) shouldn't be too tough to kill\.", #-2 level from this character
            "(?:.+?) is not quite as good as you\.",    #-1 level from this character
            "(?:.+?) is a perfect match for you!",      #same level as character
            "(?:.+?) is a little better than you\.",    #+1 level from this character
            "(?:.+?) might be tough to kill\.",         #+2 level from this character
            "(?:.+?) should be really hard to kill\.",  #+3 levels from this character
            "(?:.+?) could kill you with a needle\."    #+4 or more levels from this character
        ]
        self.WEAPON_TYPES = ["Sharp", "Thrust", "Blunt", "Pole", "Missile" ]
        self.ARMOR_SLOTS = []
        self.ARMOR_SIZE = "m" # todo: set this in info or whois
        # self.equipment  # We have an Equipment object for this
        # WEAPON_SLOTS = []  use character._class.weapon_slots

        self.EXPERIENCE       = 0
        self.GOLD             = 0
        self.TOTAL_EXPERIENCE = 0
        self.TOTAL_GOLD       = 0

        self.HAS_BUFF_ITEMS = False # Now there's an Inventory object
        self.HAS_RESTORE_ITEMS = False

        self.ATTACK_PERIOD = 3 #sec
        self.ATTACK_PERIOD_HASTE = 2 #sec
        self.CAST_PERIOD = 6 # Changes based on class

        # ATTACK_CLK = -ATTACK_WAIT
        # MOVE_CLK = -MOVE_WAIT
        # CAST_CLK = -CAST_WAIT # Last successful cast
        self.ATTACK_WAIT = self.ATTACK_PERIOD   # Used by timer. Amount of time to wait to walk after attacking
        self.MOVE_WAIT = 0.34
        self.CAST_WAIT = self.CAST_PERIOD

        self.DEATHS = 0
        self.DEAD = False

        self.LAST_BUFF = -150
        self.LAST_MEDITATE = -150 # There could be a meditate "CoolAbility" to handle this
        self.HASTING = False

        self.weapon1 = ''
        self.weapon2 = ''

        self.LEVEL_UP_REQUIREMENTS = [512, 1024, 2048, 4096, 8192]

        # These are like globals, doesn't seem like the best place, I think there's a new Go object
        self.SUCCESSFUL_GO   = True
        self.GO_BLOCKING_MOB = ""
        self.GO_PLEASE_WAIT  = False
        self.GO_NO_EXIT      = False
        self.GO_TIMEOUT      = False

        self.CONFUSED = False
        self.CAN_SEE = True
        self.ACTIVELY_MAPPING = False
        self.ACTIVELY_BOTTING = False

        self.MUD_AREA = None
        self.AREA_TITLE = ""
        self.EXIT_LIST = []
        self.MONSTER_LIST = []
        self.MOBS_JOINED_IN = []
        self.MOBS_ATTACKING = []

        self.TRYING_TO_MOVE = False
        self.EXIT_REGEX="self.character.EXIT_REGEX"
        self.AREA_ID = None
        self.LAST_DIRECTION = None

        self.START_TIME = time.time()

        self.steel_bottle_keep_amount = 1

    # def __init__(self):
    #     self.set_level_health_mana_variables()
    #     self.set_monster_kill_list()

    def add_to_monster_list(self, monster_name):
        self.MONSTER_LIST.append(monster_name)
        self.MONSTER_LIST.sort()

    def remove_from_monster_list(self, monster_name):
        for index, monster in enumerate(self.MONSTER_LIST):
            if (monster == monster_name):
                self.MONSTER_LIST.pop(index)
                continue
        self.MONSTER_LIST.sort()

    def process_info(self):
        #misc_functions.magentaprint("Character.process_info() processing info from 'info' command.")

        self.preferred_aura = self.info.preferred_alignment

        if self.level <= 3:
            self.HEALTH_TO_HEAL = 0.85 * self.info.maxHP
        else:
            self.HEALTH_TO_HEAL = 0.75 * self.info.maxHP  # We can crank this back up when we fight stronger mobs

        self.hp_tick = floor((self.info.con-1)/3)  # +3 in chapel

        # self.ARMOR_SLOTS = self._class.ARMOR_SLOTS
        # self.WEAPON_SLOTS = self._class.WEAPON_SLOTS

        self.weapon_proficiencies = {
            'Sharp'   : self.info.sharp, 
            'Thrust'  : self.info.thrust, 
            'Blunt'   : self.info.blunt,
            'Pole'    : self.info.pole, 
            'Missile' : self.info.missile
        }
        self.spell_proficiencies = {
            'Earth'  : self.info.earth, 
            'Wind'   : self.info.wind, 
            'Fire'   : self.info.fire,
            'Water'  : self.info.water, 
            'Astral' : self.info.astral
        }

        self.weapon_type = misc_functions.key_with_max_val(self.weapon_proficiencies)
        self.weapon_proficiency = self.weapon_proficiencies[self.weapon_type]

        if self.weapon_proficiency >= 70:
            self.weapon_level = 3
        elif self.weapon_proficiency >= 40:
            self.weapon_level = 2
        else:
            self.weapon_level = 1

        self.spell_type = misc_functions.key_with_max_val(self.spell_proficiencies)
        self.spell_proficiency = self.spell_proficiencies[self.spell_type]

        if self.level >= 9:
            self.armor_level = 3  # steel
        elif self.level >= 4:
            self.armor_level = 2  # chain
        else:
            self.armor_level = 1  # ring mail wearable immediately

        self.weapon_to_buy = self.pick_weapon()

    def pick_weapon(self):
        # Now we go to the db... (this isn't used)
        if self.weapon_type == 'Sharp':
            if self.weapon_level >= 2:
                return 'leaf blade'
            else:
                return 'rapier'  # 'battle axe', cleaver, scimitar
        elif self.weapon_type == 'Thrust':
            if self.weapon_level >= 2:
                return 'long sword'
            else:
                return 'broad sword'  # silver dagger (k. shaman) is good, stilleto (sentry) is better
        elif self.weapon_type == 'Blunt':
            if self.weapon_level >= 2:
                return 'morning star'  # expensive, doesn't require 40%, also, war hammer (lvl2), footman's flail, large mace
            else:
                return 'small mace'  # large mace (amethyst guards, vicars, Malbon)
        elif self.weapon_type == 'Pole':
            return 'quarter staff'
        elif self.weapon_type == 'Missile':
            if self.weapon_level >= 3:
                return 'heavy crossbow'
            elif self.weapon_level >= 2:
                return 'long bow'  # GREAT starting missile weapon, beware of roaming lion though (maybe bad for long-running lowish lvl bot )
            else:
                return 'javelin'

    # All monster lists are mutually exclusive except for "preferred."
    # Monsters may be placed in a higher level group if they are difficult to kill.

    lvl1_monsters = [ # 1-8 exp
        'dustman', 'small girl', 'young boy', 'old woman', 'old man', 'townsman', 'stall holder', 'duck', 'hedgehog', 'piglet',
        'streetsweeper', 'shopper', 'window shopper', 'window cleaner', 'waitress', 'housewife', 'squirrel', 'milk maid', 'rabbit',
        'one man band', 'heather seller', 'irate teenager', 'peasant', 'one-armed beggar', 'village elder', 'small dog', 'tribesman',
        'searcher', 'delivery boy', 'traveller', 'wanderer', 'villager', 'vagrant', 'dropout', 'tramp', 'serf', 'dishwasher',
        'punter','chicken'
    ]
    lvl1_red_monsters = [ # 8-15 exp
        'old kobold', 'kobold child', 'kobold dam'
    ]
    lvl2_monsters = [
        'hawker', 'barmaid', 'smelly beggar', 'black crow', 'sheep', 'goose', 'singer', 'musician', 'spiv', 'bidder', 'dairy cow',
        'scholar', 'juggler', 'shepherd', 'gazelle', 'dancer', 'jongleur', 'clerk', 'stablehand', 'rich kid', 'bladesman',
        "cook's assistant", "miner's assistant", 'mare', 'tabby cat', 'plumber'
        'acolyte' #, 'penitent'  # aur
    ]
    lvl2_red_monsters = [
        'kobold sentry', 'blond hooker', 'sultry hooker', 'kobold', 'spiv', 'drunken miner', 'kobold miner', 'kobold archer',
        'angry hooker', 'angry kobold', 'red axer', 'pickpocket', 'thug', 'tired hooker', 'scruffy man'
    ]
    # pickpockets drop leather collars and masks
    # red axer drops studded leather collar
    # thugs hostile.  They drop leather collar
    lvl3_monsters = [ # 25-35 exp
        'market official', 'street trader', 'field worker', 'harvester', 'horse', 'cow', 'doorman', 'stilt walker',  'messenger',
        'cashier', 'thatcher',  'tax inspector', 'journeyman', 'human miner', 'hobbitish miner', 'hawk', 'stacker', 'mill worker',
        'The General', 'bouncer', 'yard worker', 'town clerk', 'stevedore'
        # 'robed pilgrim'  # aura
        #'miner's mule"  # mill worker drops chain mail gloves
        # stevedore leather gloves
    ]
    lvl3_red_monsters = [
        'large kobold', 'insane kobold', 'kobold scout', 'drunk', 'drunken trouble-maker'
    ]
    lvl4_monsters = [ # 45-60 exp
        'actor', 'grip', 'theatre goer', 'merchant', 'journeyman', 'logger', 'trader', 'butcher', 'acrobat', 'militia soldier',
        'carpenter', 'stagehand', 'hungry spider', 'cook', 'joiner', 'ranch hand', 'old rancher', 'tired ranch hand',
        'drinking ranch hand', 'busy ranch hand', 'sawmill operator', 'vulture', 'auctioneer', 'barbecue cook', 'stable attendant',
        'steer', 'sage' # Stoneheart Road
        # 'actress', #'young knight' # For blue balance
        #'miner'
        # enlightened  # "arrives" in the large Kings road dojo (not always there)
    ]
    # hungry spiders are hostile
    lvl4_red_monsters = [
        'kobold shaman', 'kobold champion', 'hungry spider'
    ]
    lvl5_monsters = [
        'dwarven farm hand', 'dwarven barmaid', 'fort sentry', 'fur trader', 'aristocrat',
        'nobleman', 'lyrist', 'logger', 'veteran', 'bruiser', 'axeman', 'seeker', 'hunter', 'bull', 'aspirant'
        # 'vicar', 'lay priest', 'protector', 'battered knight', 'orange picker' # makes trackgrind too red?
    ]
    lvl5_red_monsters = [
        'large bandit', 'kobold guard', 'mugger', 'large spider', 'mime artist'
    ]
    lvl6_monsters = [  # 100+ exp
        'dwarven field worker', 'dwarven bartender', 'school teacher', 'lyrist', 'nobleman', 'seeker', 'bull', 'hunter', 'usher',
        'sword swallower', 'archer', 'yard supervisor', 'sawmill supervisor', 'large spider', 'blacksmith', 'farm foreman',
        'Old Man James', 'dwarven traveller', 'Goourd', 'tourney organiser', 'Greenbough the Dryad'
        #'sentry' stand in pairs unfortunately...
    ]
    lvl6_red_monsters = [ #1574 for gnoll camp
        'gnoll sentry', 'bandit swordsman', 'gnoll spearsman', 'gnoll raider', 'gnoll bandit'
    ]
    lvl7_monsters = [ # ~200 exp
        'dwarven cook', 'swordsman', 'fort sergeant', 'oremaster', 'giant spider', 'rock spider', 'Aldo', 'dwarven trader',
        'gnoll chaplain', 'Cheryn', 'orc scout', 'bouncer', 'rancher sentry', 'dwarven shepherd', 'clown', 'war horse,'
        'top ranch hand', 'raging bull'  # top ranch hand dusty blue
        # oremaster steel collar (m) for paladin
        # 'Cheryn (E)'
        # 'robed priest',
    ]  # There are also lvl 5 rancher sentries... they're a bit blue
    lvl8_monsters = [  # There are 2 amethyst guards and 3 amber guards of this level
        'Alaran the Market Manager', 'hauler', 'Farmer Malbon', 'sonneteer', 'Tag', 'mine manager', 'artificer',
        'Dini Stonehammer', # horseman's flail 500g
        'Olmer', 'Thereze', 'Farmer Viladin', 'Rancher Renstone', 'berzerker', 'dwarven hunter',
        'initiate', 'berserk orc', 'hedge knight', 'refinery supervisor', 'owlbear', #'sentry'
        # 'elven trader', 'old knight', 'dusty warrior'
        # dark warrior  sacrificing priestess
        # forger        weathered barbarian
        # large knight  cutthroat     
        # deaconess     initiate      
        # gnome smith   Farmer Calmor 
    ]  # elves are very blue
    lvl9_monsters = [ # ~300 exp
        'director', 'Elder Barthrodue', 'Farmer Calmor', 'orc warrior', 'giant beetle', 'white knight',  # 380
        'weathered barbarian', 
        'Trent the Merchant' # silver rod guarded by Egan
        #'old man'
        # gnoll sub-chief
        # unholy master
    ]  # respect the knights! (+1 difficulty)
    lvl10_monsters = [ # 350+
        'wounded knight', # -2 difficulty
        'The Master of Ceremonies', # 280
        'Dame Brethil', 'Kelluran', 'Jerrek', 'Rimark', 'Commander Rilmenson', 'Farmer McDermott', 'dwarven blacksmith'   # 400
        'abbot', # 445
        'silver knight',  # 380, +1 difficulty
        'barbarian cook', "shaman's assistant",
        'The Ringmaster', 'Marie', 'market guard', #(<=10 (need to check these))
        'surveyor','master miner','shaft manager','pit pony','cleaner' # check the levels on these
        # gnomish miner
        # Maybe try master miners then mine managers
        # Mine track looks tougher than others
        # hero?
    ]  # wounded knight -2 difficulty
    # I think Rilmenson could get a +1 level
    # 'gnoll sub-chief', 'Gnardu'
    lvl11_monsters = [
        'dwarven adventurer',  # dusty blue
        'enchantress', # 456 exp, appeard in the school on Stoneheart, silver rod (Purest adamantine. You feel no different - the want emits a brief glow)
        'Brotain', 'minstrel', # silver ring
        'brutalizer', 'Gregor', 'Bertram Dalrum', 'brother', 'priest'
    ]
    lvl12_monsters = [
        'barbarian shaman', 'barbarian warrior', 
        'Hurn the Smith', # 600xp, 733g
        'Horbuk', # steel collar like oremaster
        'The Floor Manager', 'Tardan', 'ranch foreman', 'Gorban', 'shadowed huorn', # dusty blue
        'Boris Ironfounder', 'Lady Denlise', 'Annette Plover', 'house guest', 'Martin' # fireball/gold dagger/810 exp
        #'The Saga Teacher', 'The Amber Mage', # cannot be killed ("This is not possible!")
        # Tardan 560 exp
        # 'vigil knight'
        # Servant of the Night
    ]
    lvl13_monsters = [
        'The Dojo Administrator', 
        'Elsuria', # fine elven cloak
        'Tendrurn', # adamantine axe 600g
        'Nospe' # under the Casino
    ]
    lvl14_monsters = [
        'cave troll guard', 'Rancher Plover', # assassin's dagger
        'Team Leader Egan', 'Qimoth', "Th'kit the HorseMaster", 'warmonger',
        'Lord Tamaran', # aaashaaal's gift
        'Olarma', 'castle priest',
        'The Manic Soothsayer' # dragon claws (thief boots)
    ]
    lvl15_monsters = ['Thomas Ironheart', 'Earl Mardley', 'The Immigration Officer', 
    'Mayor Demlin',  # crumpled parchment
    'Madame Zara', # Can only fit one in the tent
    'Rogue Oak'] # confirm Madame Zara
    lvl16_monsters = ['Holbyn', # Holby closes at night
    'Ordaran the White', 'Pansy', 'Vickie', 'Matriarch Sara']  # Hawk camp
    lvl17_monsters = ['Faldomet', 'Patriarch Jedd Morhennon', 'Farside', 'Lord Arduis', 'Lady Arielle']
    lvl18_monsters = ['Lady Jenlira', 'Deep Root'] # vigil knight guards the entrance
    lvl20_monsters = ['The Archbishop'] # needles me at 16
    # A list of monsters redundant to the above lists that
    # I may want to kill even if they are too low of level.
    # Mostly hostiles and things that don't let you loot.
    # Level 18 <= 'master', 'Magus Bregum', 'Magus Cristyl', 'Magus Olthim', 'Magus Tertial', 'Dwar', 'Joffi the Mystic'
    # Lich on blood rock (shadow lich). Giant bog troll. Wyvern
    # "Grand Master Yang-Shi" "The Sensei"
    # "The Master Artificer" (That is not possible!)
    # scared trawlerman
    # Combat Master
    # Green Branch
    # Haelyn
    # Druid Tutor
    # Chief Alchemist
    # queen werewolf
    # Farmer Woldis
    # Farmer Viladin
    # ogrish guard
    # caretaker

    preferred_lvl_1_2_monsters = [
        'oaf', 'wanderer', 'thug', 'spiv', 'kobold sentry', 'tired hooker', 'waitress',
        'blond hooker', 'angry hooker', 'sultry hooker', 'journeyman', 'housewife', # 'acolyte'
    ]

    def set_monster_kill_list(self):
        self.MONSTER_KILL_LIST = []

        self.MONSTER_KILL_LIST.extend(self.lvl1_red_monsters)

        if self.level <= 7:
            self.MONSTER_KILL_LIST.extend(self.lvl1_monsters)

        if self.level >= 4:
            self.MONSTER_KILL_LIST.extend(self.lvl2_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl2_red_monsters)
        if self.level >= 5:
            self.MONSTER_KILL_LIST.extend(self.lvl3_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl3_red_monsters)
        if self.level >= 6:
            # self.MONSTER_KILL_LIST = [m for m in self.MONSTER_KILL_LIST \
            #                           if m not in self.lvl1_monsters    \
            #                           and m not in self.lvl2_monsters]
            self.MONSTER_KILL_LIST.extend(self.preferred_lvl_1_2_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl4_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl4_red_monsters)
        if self.level >= 7:
            self.MONSTER_KILL_LIST.extend(self.lvl5_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl5_red_monsters)
        if self.level >= 9:
            self.MONSTER_KILL_LIST.extend(self.lvl6_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl6_red_monsters)
        if self.level >= 11:
            self.MONSTER_KILL_LIST.extend(self.lvl7_monsters)
        if self.level >= 13:
            self.MONSTER_KILL_LIST.extend(self.lvl8_monsters)
        if self.level >= 15:
            self.MONSTER_KILL_LIST.extend(self.lvl9_monsters)
        if self.level >= 16:
            self.MONSTER_KILL_LIST.extend(self.lvl10_monsters)
        if self.level >= 17:
            self.MONSTER_KILL_LIST.extend(self.lvl11_monsters) # Brotain seems a bit tough... need mend wounds logic... or maybe the bot will surprise me with heals or something
# Drops -
#  Alaran, Aldo, Farmer Calmor for rings (platinum, gold, etc.)

    def configure_health_and_mana_variables(self):
    # Health to heal is now a percentage (see process_info)
        if self.level <= 2:
            # self.HEALTH_TO_HEAL = 19
            self.HEALTH_TO_FLEE = 8
            self.MAX_MANA = 3
            self.MANA_TO_ENGAGE = 3
        elif self.level <= 3:
            # self.HEALTH_TO_HEAL = 27
            self.HEALTH_TO_FLEE = 9
            self.MAX_MANA = 7
            self.MANA_TO_ENGAGE = 3
        elif self.level <= 4:
            # self.HEALTH_TO_HEAL = 31
            self.HEALTH_TO_FLEE = 11
            self.MAX_MANA = 9
            self.MANA_TO_ENGAGE = 3
        elif self.level <= 5:
            # self.HEALTH_TO_HEAL = 31
            self.HEALTH_TO_FLEE = 8
            self.MAX_MANA = 12
            self.MANA_TO_ENGAGE = 6
        elif self.level <= 6:
            # self.HEALTH_TO_HEAL = 35 # was 43 for Ruorg
            self.HEALTH_TO_FLEE = 15
            self.MAX_MANA = 18
            self.MANA_TO_ENGAGE = 9
        elif self.level <= 7: # has the same enemy list as 6
            # self.HEALTH_TO_HEAL= 40 # was 45
            self.HEALTH_TO_FLEE =  15
            self.MAX_MANA = 21
            self.MANA_TO_ENGAGE = 9
        elif self.level <= 8:
            # self.HEALTH_TO_HEAL= 45
            self.HEALTH_TO_FLEE = 30
            self.MAX_MANA       = 24 # This has to depend on the class
            self.MANA_TO_ENGAGE = 15
        elif self.level <= 9:
            self.HEALTH_TO_FLEE = 31
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 16
        elif self.level <= 10:
            self.HEALTH_TO_FLEE = 32
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 17
        elif self.level <= 11:
            self.HEALTH_TO_FLEE = 33
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 18
        elif self.level <= 12:
            self.HEALTH_TO_FLEE = 34
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 19
        elif self.level <= 13:
            self.HEALTH_TO_FLEE = 35
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 20
        elif self.level <= 14:
            self.HEALTH_TO_FLEE = 36
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 21
        elif self.level <= 15:
            self.HEALTH_TO_FLEE = 37
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 22
        elif self.level <= 16:
            self.HEALTH_TO_FLEE = 38
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 23
        elif self.level <= 17:
            self.HEALTH_TO_FLEE = 39
            self.MAX_MANA       = 24
            self.MANA_TO_ENGAGE = 24
        elif self.level <= 18:
            self.HEALTH_TO_FLEE = 40
            self.MAX_MANA       = 25
            self.MANA_TO_ENGAGE = 25
        else:
            # self.HEALTH_TO_HEAL = 62
            self.HEALTH_TO_FLEE = 27
            self.MANA_TO_ENGAGE = 18
            #adam.HEALTH_TO_HEAL = 65
            #adam.HEALTH_TO_FLEE = 15
            #adam.MAX_MANA = 4
            #adam.MANA_TO_ENGAGE = 0

    def max_vigor(self):
        return self.info.pty / 2.3
        # if self.health_monitor.vig_amounts:
        #     return max(self.health_monitor.vig_amounts)
        # else:
        #     return self.info.pty / 2.3

    def max_mend(self):
        if self.health_monitor.mend_amounts:
            return max(self.mend_amounts)
        else:
            return 9

        # if self.__class__.tick_times:
           #  self.__class__.tick_times.append(time.time() - self.__class__)
       # else:


