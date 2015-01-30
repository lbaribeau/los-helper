
import time, sys, operator
import CharacterClass
from misc_functions import *

class Character(object):

    # This is a class that holds a bunch of data,
    # mostly obtained by the MUD read thread.
    race = None
    title = None
    _class = None
    level = None
    preferred_alignment = None
    BLACK_MAGIC = True
    FAVOURITE_SPELL = "fireball"
    SPELL_COST = 7
    KNOWS_VIGOR = True
    #WEAPON_SKILLS = [0, 0, 0, 0, 0] #sharp, thrust, blunt, pole, missile
    #MAGIC_SKILLS= [0, 0, 0, 0, 0]
    SKILLS = {} 
    AURA_LIST = ['demonic red', 'ominous red', 'ghastly red', 'murky red',
                 'red', 'rusty', 'dusty red', 'grey',
                 'dusty blue', 'pale blue', 'blue',
                 'deep blue', 'bright blue', 'shimmering blue', 'heavenly blue', 'blazing blue', 'blood red']

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

    # Indices will be sharp, thrust, blunt, pole, missile, earth, water, wind, fire, astral
    # note... never uses "an"  (ie. "You glow with _a_ ominous red aura")

    AURA_SCALE = 9
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

    if _class == "Cle" or _class == "Mag":
        CAST_PERIOD = 3

    ATTACK_WAIT = ATTACK_PERIOD   # Used by timer.  Same as ATTACK_PERIOD.
                                # Amount of time to wait to walk after attacking

    MOVE_WAIT = 0.33
    if sys.platform == 'win32':
        MOVE_WAIT = 0.29
 
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

    WEAPON1="ball"
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

    TRYING_TO_MOVE = True
    EXIT_REGEX="self.character.EXIT_REGEX"
    AREA_ID = None
    LAST_DIRECTION = None

    LEVEL_UP_REQUIREMENTS = [512, 1024, 2048, 4096] #Half of this is the gold requirement

    START_TIME = time.time()
    chase_mob = ""
    chase_dir = ""

    weapon_model = "Blunt"
    weapon_proficiency = "0"
    weapon_level = "1"
    armor_level = "1"
    spell_model = "Fire"
    spell_proficiency = "0"

    def configure_equipment_and_spell_preferences(self):
        if self.weapons is not None:
            self.weapon_model, self.weapon_proficiency = key_with_max_val(self.weapons)

        if self.magic is not None:
            self.spell_model, self.spell_proficiency = key_with_max_val(self.magic)

        if self.level is not None:
            if self.level <= 4:
                self.armor_level = 1
            else: #more testing needs to be done to determine what other levels are available
                self.armor_level = 2

    def configure_health_and_mana_variables(self):
        if self.level <= 2:
            self.HEALTH_TO_HEAL = 11
            self.HEALTH_TO_FLEE = 4
            self.MAX_MANA = 3
            self.MANA_TO_ENGAGE = 3
        elif self.level <= 3:
            self.HEALTH_TO_HEAL = 20
            self.HEALTH_TO_FLEE = 9
            self.MAX_MANA = 12
            self.MANA_TO_ENGAGE = 4
        elif self.level <= 4:
            self.HEALTH_TO_HEAL = 25
            self.HEALTH_TO_FLEE = 15
            self.MAX_MANA = 15
            self.MANA_TO_ENGAGE = 9
        elif self.level <= 5:
            self.HEALTH_TO_HEAL= 30
            self.HEALTH_TO_FLEE = 15
            self.MAX_MANA = 12
            self.MANA_TO_ENGAGE = 12          
        elif self.level <= 6:
            self.HEALTH_TO_HEAL = 35 # 43
            self.HEALTH_TO_FLEE = 15
            self.MAX_MANA = 18
            self.MANA_TO_ENGAGE = 12   
        elif self.level <= 7:
            self.HEALTH_TO_HEAL= 45
            self.HEALTH_TO_FLEE = 8 
            self.MAX_MANA = 21
            self.MANA_TO_ENGAGE = 12
        elif self.level <= 8:
            self.HEALTH_TO_HEAL= 45
            self.HEALTH_TO_FLEE = 30
            self.MAX_MANA = 24
            self.MANA_TO_ENGAGE = 15        
        else:
            #self.HEALTH_TO_HEAL = 62
            #self.HEALTH_TO_FLEE = 27
            #self.MAX_MANA = 27 - 4 + 1
            #self.MANA_TO_ENGAGE = 18
            self.HEALTH_TO_HEAL = 70
            self.HEALTH_TO_FLEE = 40
            self.MAX_MANA = 4
            self.MANA_TO_ENGAGE = 0
    
    ### Monster stuff ###

    lvl1_monsters = [ # 1-8 exp
        "dustman", "small girl", "young boy", "old woman", "old man", 
        "townsman", "stall holder", "duck", "hedgehog", "piglet", 
        'streetsweeper', "shopper", "window shopper", "window cleaner", 
        "waitress", "housewife", "squirrel", "milk maid", "rabbit", 
        "one man band", "heather seller", "irate teenager", 'peasant', 
        'one-armed beggar', "village elder", "small dog", "tribesman", 
        "searcher", "delivery boy", "traveller", "wanderer", "villager", 
        "vagrant", "dropout", "tramp", "serf", 'dishwasher'
        ]     
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
        "angry kobold", 'red axer', 'pickpocket', 'thug'
        ] 
    # pickpockets drop leather collars and masks
    # red axer drops studded leather collar
    # cat might be lvl 1 not sure
    # thugs hostile.  They drop leather collar
    lvl3_monsters = [ # 25-35 exp
        "market official", "street trader", "field worker", "harvester", 
        "horse", "cow", "doorman", "stilt walker",  "messenger", "cashier",
        "thatcher",  "tax inspector", 'journeyman', "human miner", 
        "hobbitish miner", "hawk", "stacker", "mill worker"
        #"robed pilgrim",  # Removed for red/blue balance
        #"miner's mule"
        ]
    lvl3_red_monsters = [
        "large kobold", "insane kobold", "kobold scout", 'drunk'
        ]
    lvl4_monsters = [ # 45-60 exp
        "actor", "grip", "theatre goer", "merchant", "journeyman", "logger", 
        'trader', "butcher", #"young knight", because of targetting this could get confused with old / white etc...
        "acrobat", "militia soldier", 
        "carpenter", "stagehand", 'hungry spider', 'cook', 'joiner', "ranch hand",
        "old rancher", "tired ranch hand", "drinking ranch hand",
        "busy ranch hand",
        #"auctioneer", # They pile up so bad!  
        # Definitely need smart chasing or a path that runs extra around the 
        # market (after healing)
        "actress", # For blue balance
        #'miner'
        ]
    # hungry spiders are hostile
    lvl4_red_monsters = [
        "kobold shaman", "drunken trouble-maker", "kobold champion", "hungry spider"]
    lvl5_monsters = [
        "dwarven farm hand", "dwarven barmaid", "fort sentry", "fur trader", 
        "aristocrat", "rancher sentry"]
    lvl5_red_monsters = [
        'large bandit', "kobold guard", "mugger", 'large spider'
        ]
    lvl6_monsters = [
        "dwarven field worker", "dwarven bartender", "school teacher",
        'lyrist', "nobleman", "seeker", "bull", "hunter", 'usher',
        'sword swallower', 'archer', "mime artist",
        "yard supervisor", "sawmill operator", "large spider"
        #'sentry' stand in pairs unfortunately...
        ] # bull and hunter might be wrong (too high).
    lvl6_red_monsters = [ #1574 for gnoll camp
        'gnoll sentry', "bandit swordsman", "gnoll spearsman", "gnoll raider"
        ]
    lvl7_monsters = [
        "dwarven cook", "swordsman", 'fort sergeant', 'oremaster', 
        'giant spider', "rock spider"
        ] # giant spiders are hostile
    lvl8_monsters = [
        'owlbear',
        #'mine manager'
        ]
    lvl9_monsters = [
        "dwarven blacksmith"
        ]

    lvl10_blue_monsters = [ #1913 Red Tent, #1904 / #1912 Knights Tent, #1909
        "old knight", "hedge knight", "white knight", #too tough for bot
        "battered knight",
        #'silver knight' deflects attacks a.k.a. takes 50% dmg and shouldn't be fought by melee
        ]
    # A list of monsters redundant to the above lists that
    # I may want to kill even if they are too low of level.
    # Mostly hostiles and things that don't let you loot.
    preferred_lvl_1_2_monsters = [
        "oaf", "wanderer", #"acolyte", 
        "thug", "spiv", "kobold sentry", "tired hooker", 
        "blond hooker", "angry hooker", "sultry hooker", 
        "journeyman" ] 

    def set_monster_kill_list(self):
        self.MONSTER_KILL_LIST = []
        self.MONSTER_KILL_LIST.extend(self.lvl1_monsters)
        self.MONSTER_KILL_LIST.extend(self.lvl1_red_monsters)

        if self.level > 3:
            self.MONSTER_KILL_LIST.extend(self.lvl2_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl2_red_monsters)
        if self.level > 4:
            self.MONSTER_KILL_LIST.extend(self.lvl3_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl3_red_monsters)
        if self.level > 5:
            self.MONSTER_KILL_LIST = [m for m in self.MONSTER_KILL_LIST \
                                      if m not in self.lvl1_monsters    \
                                      and m not in self.lvl2_monsters]
            self.MONSTER_KILL_LIST.extend(self.preferred_lvl_1_2_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl4_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl4_red_monsters)
        if self.level > 7:
            self.MONSTER_KILL_LIST.extend(self.lvl5_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl5_red_monsters)
        if self.level > 8:
            self.MONSTER_KILL_LIST.extend(self.lvl6_monsters)
            self.MONSTER_KILL_LIST.extend(self.lvl6_red_monsters)
        if self.level > 10:
            self.MONSTER_KILL_LIST.extend(self.lvl7_monsters)
        if self.level > 12:
            self.MONSTER_KILL_LIST.extend(self.lvl10_blue_monsters)


# todo: I don't like caps anymore
# I think that's because these don't feel like global settings anymore, since 
# the program is bigger.
