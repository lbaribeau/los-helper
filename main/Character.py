
import time

class Character(object):

    # This is a class that holds a bunch of data,
    # mostly obtained by the MUD read thread.
    race = None
    title = None
    _class = None
    level = None
    preferred_alignment = None
    BLACK_MAGIC = True
    KNOWS_VIGOR = True
    #WEAPON_SKILLS = [0, 0, 0, 0, 0] #sharp, thrust, blunt, pole, missile
    #MAGIC_SKILLS= [0, 0, 0, 0, 0]
    SKILLS = {} 

    AURA_LIST =  ['demonic red', 'ominous red', 'ghastly red', 'murky red',
                  'red', 'rusty', 'dusty red', 'grey',
                  'dusty blue', 'pale blue', 'blue',
                  'deep blue', 'bright blue', 'shimmering blue', 'heavenly blue'
    ]  # blood red and blazing blue...
    # note... never uses "an"  (ie. "You glow with _a_ ominous red aura")
    LEVEL_LIST = ["You could kill (?:.+?) with a needle\.", #-4 or more levels
                  "(?:.+?) should be easy to kill\.", #-2 level from this character
                  "(?:.+?) shouldn't be too tough to kill\.", #-2 level from this character
                  "(?:.+?) is not quite as good as you\.", #-1 level from this character
                  "(?:.+?) is a perfect match for you!", #same level as character
                  "(?:.+?) is a little better than you\.", #+1 level from this character
                  "(?:.+?) might be tough to kill\.", #+2 level from this character
                  "(?:.+?) should be really hard to kill\.", #+3 levels from this character
                  "(?:.+?) could kill you with a needle\." #+4 or more levels from this character
    ]
    WEAPON_TYPES = ["Sharp", "Thrust", "Blunt", "Pole", "Missile" ]

    ARMOR_SLOTS = []
    ARMOR_SIZE = "m" # todo: set this in info or whois
    
    WEAPON_SLOTS = []

    AURA_SCALE = 8
    AURA = AURA_LIST[AURA_SCALE]
    
    AURA_PREFERRED_SCALE = None
    AURA_PREFERRED = None
    
    AURA_LAST_UPDATE = -300
    LAST_BUFF = -150
    LAST_MEDITATE = -150

    HAS_BUFF_ITEMS = False
    HAS_RESTORE_ITEMS = False

    EXPERIENCE = 0
    GOLD = 0
    TOTAL_EXPERIENCE = 0
    TOTAL_GOLD = 0

    ATTACK_PERIOD = 3 #sec
    ATTACK_PERIOD_HASTE = 2 #sec
    CAST_PERIOD = 6

    ATTACK_WAIT = ATTACK_PERIOD   # Used by timer.  Same as ATTACK_PERIOD.
                                # Amount of time to wait to walk after attacking
    MOVE_WAIT = 0.34
    CAST_WAIT = CAST_PERIOD

    MOBS_KILLED = 0
    HITS_DEALT = 0
    HITS_MISSED = 0
    DAMAGE_DEALT = 0
    HIGHEST_DAMAGE = 0
    LOWEST_DAMAGE = 0
    CRITS_LANDED = 0
    SPELLS_CAST = 0
    SPELLS_FAILED = 0
    SPELL_DAMAGE_DEALT = 0
    SPELLS_CRIT = 0
    HITS_RECEIVED = 0
    HITS_EVADED = 0
    DAMAGE_TAKEN = 0
    DEATHS = 0

    HASTING = False 
    DEAD = False

    WEAPON1=""
    WEAPON2=""
                            
    ATTACK_CLK = -ATTACK_WAIT
    MOVE_CLK = -MOVE_WAIT
    CAST_CLK = -CAST_WAIT # Last successful cast

    HEALTH = 0
    MANA = 0

    LEVEL_UP_REQUIREMENTS = [512, 1024, 2048, 4096]

    # MONSTER LISTS
    # All lists are mutually exclusive except for "preferred."
    # Monsters may be placed in a higher level group if they are 
    # difficult to kill.

    MOBS_JOINED_IN = []
    MOBS_ATTACKING = []

    SUCCESSFUL_GO = True
    GO_BLOCKING_MOB = ""
    GO_PLEASE_WAIT = False
    GO_NO_EXIT = False
    GO_TIMEOUT = False

    CONFUSED = False
    CAN_SEE = True
    ACTIVELY_MAPPING = False
    ACTIVELY_BOTTING = False

    MUD_AREA = None
    AREA_TITLE=""
    EXIT_LIST=[]
    MONSTER_LIST=[]

    def add_to_monster_list(self, monster_name):
        self.MONSTER_LIST.append(monster_name)
        self.MONSTER_LIST.sort()

    def remove_from_monster_list(self, monster_name):
        for index, monster in enumerate(self.MONSTER_LIST):
            if (monster == monster_name):
                self.MONSTER_LIST.pop(index)
                continue
        self.MONSTER_LIST.sort()

    TRYING_TO_MOVE = True
    EXIT_REGEX="self.character.EXIT_REGEX"
    AREA_ID = None
    LAST_DIRECTION = None

    # LEVEL_UP_EXP = [512, 1024, 2048, 4096] 

    weapon_model = "Blunt"
    weapon_proficiency = "0"
    weapon_level = 1
    armor_level = 1
    spell_model = "Fire"
    spell_proficiency = "0"

    START_TIME = time.time()

    # def __init__(self):
    #     self.set_level_health_mana_variables()
    #     self.set_monster_kill_list()
    
    def configure_equipment_and_spell_preferences(self):
        self.ARMOR_SLOTS = self._class.ARMOR_SLOTS
        self.WEAPON_SLOTS = self._class.WEAPON_SLOTS

        if self.weapons is not None:
            self.weapon_model, self.weapon_proficiency = key_with_max_val(self.weapons)

            #more testing needed for weapon level check
            if int(self.weapon_proficiency) > 15:
                self.weapon_level = 2

            if int(self.weapon_proficiency) > 30:
                self.weapon_level = 3

        if self.magic is not None:
            self.spell_model, self.spell_proficiency = key_with_max_val(self.magic)

        if self.level is not None:
            if self.level <= 4:
                self.armor_level = 1
            else: #more testing needs to be done to determine what other levels are available
                self.armor_level = 2
          
    def get_ideal_mana(self):
        ideal_mana = self.MAX_MANA

        if not (self.BLACK_MAGIC): 
            ideal_mana = self.MAX_MANA - 1

        return ideal_mana

        # self.character.MAX_MANA / 2
        #     if self.character.BLACK_MAGIC: 
        #         MANA_TO_GO = self.character.MAX_MANA 
        #     else:
        #         if self.character.MAX_MANA % 2 == 1:
        #             MANA_TO_GO = self.character.MAX_MANA - 1 
        #         else:                                        
        #             MANA_TO_GO = self.character.MAX_MANA  

    def configure_health_and_mana_variables(self):
        if self.level <= 2:
            self.HEALTH_TO_HEAL = 20
            self.HEALTH_TO_FLEE = 8
            self.MAX_MANA = 3
            self.MANA_TO_ENGAGE = 3
        elif self.level <= 3:
            self.HEALTH_TO_HEAL = 27
            self.HEALTH_TO_FLEE = 9
            self.MAX_MANA = 7
            self.MANA_TO_ENGAGE = 3
        elif self.level <= 4:
            self.HEALTH_TO_HEAL = 31
            self.HEALTH_TO_FLEE = 11
            self.MAX_MANA = 9
            self.MANA_TO_ENGAGE = 3
        elif self.level <= 5:
            self.HEALTH_TO_HEAL= 31
            self.HEALTH_TO_FLEE = 8
            self.MAX_MANA = 12
            self.MANA_TO_ENGAGE = 6           
        elif self.level <= 6:
            self.HEALTH_TO_HEAL = 35 # was 43 for Ruorg
            self.HEALTH_TO_FLEE = 15
            self.MAX_MANA = 18
            self.MANA_TO_ENGAGE = 9     
        elif self.level <= 7: # has the same enemy list as 6
            self.HEALTH_TO_HEAL= 40 # was 45
            self.HEALTH_TO_FLEE =  15
            self.MAX_MANA = 21
            self.MANA_TO_ENGAGE = 9
        elif self.level <= 8:
            self.HEALTH_TO_HEAL= 45
            self.HEALTH_TO_FLEE = 30
            self.MAX_MANA = 24
            self.MANA_TO_ENGAGE = 15        
        else:
            self.HEALTH_TO_HEAL = 62
            self.HEALTH_TO_FLEE = 27
            self.MAX_MANA = 27 - 4 + 1
            self.MANA_TO_ENGAGE = 18
            #adam.HEALTH_TO_HEAL = 65
            #adam.HEALTH_TO_FLEE = 15
            #adam.MAX_MANA = 4
            #adam.MANA_TO_ENGAGE = 0
    
    ### Monster stuff ###

    lvl1_monsters = [ # 1-8 exp
        "dustman", "small girl", "young boy", "old woman", "old man", 
        "townsman", "stall holder", "duck", "hedgehog", "piglet", 
        'streetsweeper', "shopper", "window shopper", "window cleaner", 
        "waitress", "housewife", "squirrel", "milk maid", "rabbit", 
        "one man band", "heather seller", "irate teenager", 'peasant', 
        'one-armed beggar', "village elder", "small dog", "tribesman", 
        "searcher", "delivery boy", "traveller", "wanderer", "villager", 
        "vagrant", "dropout", "tramp", "serf", 'dishwasher', "punter"]     
    lvl1_red_monsters = [ # 8-15 exp
        "old kobold", "kobold child", "kobold dam"]
    lvl2_monsters = [
        "hawker", "barmaid", "smelly beggar", "black crow", "sheep", "goose", 
        "singer", "musician", "spiv", "bidder", "dairy cow", "scholar", 
        "juggler", "shepherd", "gazelle", 'dancer', 'jongleur', 'tabby cat', 
        'clerk', 'stablehand', "rich kid", 'bladesman', "cook's assistant", 
        "miner's assistant"
        #"acolyte"  # Problem: clumps up on holly lane
        #"penitent"  # Removed for red/blue balance
        ] 
    lvl2_red_monsters = [ 
        "kobold sentry", "blond hooker", "sultry hooker", "kobold", "spiv", 
        "drunken miner", "kobold miner", "kobold archer", 'angry hooker',
        "angry kobold", 'red axer', 'pickpocket', 'thug', "tired hooker"
        ] 
    # pickpockets drop leather collars and masks
    # red axer drops studded leather collar
    # cat might be lvl 1 not sure
    # thugs hostile.  They drop leather collar
    lvl3_monsters = [ # 25-35 exp
        "market official", "street trader", "field worker", "harvester", 
        "horse", "cow", "doorman", "stilt walker",  "messenger", "cashier",
        "thatcher",  "tax inspector", 'journeyman', "human miner", 
        "hobbitish miner", "hawk", "stacker", "mill worker", 'The General',
        'bouncer'
        #"robed pilgrim",  # Removed for red/blue balance
        #"miner's mule"
        ]
    lvl3_red_monsters = [
        "large kobold", "insane kobold", "kobold scout", 'drunk'
        ]
    lvl4_monsters = [ # 45-60 exp
        "actor", "grip", "theatre goer", "merchant", "journeyman", "logger", 
        'trader', "butcher", "young knight", "acrobat", "militia soldier", 
        "carpenter", "stagehand", 'hungry spider', 'cook', 'joiner', "ranch hand",
        "old rancher", "tired ranch hand", "drinking ranch hand",
        "busy ranch hand", "sawmill operator", 'vulture'
        #"auctioneer", # They pile up so bad!  
        # Definitely need smart chasing or a path that runs extra around the 
        # market (after healing)
        #"actress", # For blue balance
        #'miner'
        ]
    # hungry spiders are hostile
    lvl4_red_monsters = [
        "kobold shaman", "drunken trouble-maker", "kobold champion", "hungry spider"]
    lvl5_monsters = [
        "dwarven farm hand", "dwarven barmaid", "fort sentry", "fur trader", 
        "aristocrat", "rancher sentry",
        # "vicar",
        "nobleman", "lyrist", "orange picker", "logger",
        "veteran", "bruiser", "axeman", "seeker", "hunter", "bull", "lay priest", "protector",
        "battered knight", 'bruiser',
        "aspirant"  # grey
    ]
    lvl5_red_monsters = [
        'large bandit', "kobold guard", "mugger", 'large spider'
    ]
    lvl6_monsters = [  # 100+ exp
        "dwarven field worker", "dwarven bartender", "school teacher",
        'lyrist', "nobleman", "seeker", "bull", "hunter", 'usher',
        'sword swallower', 'archer', "mime artist",
        "yard supervisor", 'sawmill supervisor', "large spider", "blacksmith",
        "farm foreman", "Old Man James", "dwarven traveller",
        "Goourd", "tourney organiser"
        #'sentry' stand in pairs unfortunately...
    ]
    lvl6_red_monsters = [ #1574 for gnoll camp
        'gnoll sentry', "bandit swordsman", "gnoll spearsman", "gnoll raider"
    ]
    lvl7_monsters = [ # ~200 exp
        "dwarven cook", "swordsman", 'fort sergeant', 'oremaster', 
        'giant spider', "rock spider", "Aldo", "dwarven trader",
        "gnoll chaplain", "Cheryn", "robed priest", "orc scout",
        'bouncer',
        "dwarven shepherd"  # grey
    ] # giant spiders are hostile
    lvl8_monsters = [
        # There are 2 amethyst guards and 3 amber guards of this level
        "Alaran the Market Manager", "hauler", "Farmer Malbon", "sonneteer", "Tag",
        "mine manager", "artificer", "Dini Stonehammer", "Olmer",
        "Thereze", "Farmer Viladin", "Rancher Renstone", "berzerker",
        "dwarven hunter", "initiate", "berserk orc",
        "old knight", "dusty warrior",  # dusty blue        
        'hedge knight', 'refinery supervisor', 'owlbear'
        "elven trader",   # pale blue
    ]
    lvl9_monsters = [ # ~300 exp
        "director", "Elder Barthrodue", "Farmer Calmor",
        "orc warrior", 'giant beetle'
        'white knight' # respect the knights! (+1 difficulty)
    ]
    lvl10_monsters = [ # 350+
        'wounded knight', # -2 difficulty
        'The Master of Ceremonies', # 280
        "Kelluran", "Jerrek",  # all grey
        "Farmer McDermott", "abbot", # 445
        'Rimark', 'Dame Brethil', 'dwarven blacksmith', 'silver knight', 'Commander Rilmenson'
    ]
    lvl11_monsters = [
        "dwarven adventurer",  # dusty blue
        "enchantress", 'Brotain', 'minstrel', 'brutalizer', 'Gregor'
    ]
    lvl12_monsters = [
        "barbarian shaman", "barbarian warrior", # grey
        "Gorban", # dusty blue
        'The Amber Mage', 'The Saga Teacher', 'Hurn the Smith',
        'Horbuk', 'The Floor Manager'
    ]
    lvl13_monsters = [
        'The Dojo Administrator'
    ]
    lvl14_monsters = [
        'cave troll guard'
    ]
    # A list of monsters redundant to the above lists that
    # I may want to kill even if they are too low of level.
    # Mostly hostiles and things that don't let you loot.
    preferred_lvl_1_2_monsters = [
        "oaf", "wanderer", #"acolyte", 
        "thug", "spiv", "kobold sentry", "tired hooker", 
        "blond hooker", "angry hooker", "sultry hooker", 
        "journeyman" 
    ] 

    def set_monster_kill_list(self):
        self.MONSTER_KILL_LIST = []

        if self.level <= 7:
            self.MONSTER_KILL_LIST.extend(self.lvl1_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl1_red_monsters)

        if self.level > 3:
            self.MONSTER_KILL_LIST.extend(self.lvl2_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl2_red_monsters)
        if self.level > 4:
            self.MONSTER_KILL_LIST.extend(self.lvl3_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl3_red_monsters)
        if self.level > 6:
            # self.MONSTER_KILL_LIST = [m for m in self.MONSTER_KILL_LIST \
            #                           if m not in self.lvl1_monsters    \
            #                           and m not in self.lvl2_monsters]
            self.MONSTER_KILL_LIST.extend(self.preferred_lvl_1_2_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl4_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl4_red_monsters)
        if self.level > 8:
            self.MONSTER_KILL_LIST.extend(self.lvl5_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl5_red_monsters)
        if self.level > 9:
            self.MONSTER_KILL_LIST.extend(self.lvl6_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl6_red_monsters)
        if self.level > 11:
            self.MONSTER_KILL_LIST.extend(self.lvl7_monsters)
        if self.level > 12:
            self.MONSTER_KILL_LIST.extend(self.lvl5_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl5_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl6_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl6_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl7_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl8_monsters)
            # self.MONSTER_KILL_LIST.extend(self.lvl9_monsters)


# todo: I don't like caps anymore
# I think that's because these don't feel like global settings anymore, since 
# the program is bigger.

# Drops -
#  Alaran, Aldo, Farmer Calmor for rings (platinum, gold, etc.)