################################################################################
import time

class Character:

    # This is a class that holds a bunch of data,
    # mostly obtained by the MUD read thread.

    def __init__(self):
        # character init function sets variables to default (initial)
        # values.  
    
#        self.char_class = ""
        self.LEVEL = 8
#        self.preferred_alignment = "grey"
#        self.weapon_skills = [0, 0, 0, 0, 0] #sharp, thrust, blunt, pole, missile
#        self.magic_skills = [0, 0, 0, 0, 0]
        self.EXPERIENCE = 0
        self.GOLD = 0
        
        self.BLACK_MAGIC = True
        self.FAVOURITE_SPELL = "hurt"
        
        self.ATTACK_PERIOD = 3 #sec
        self.ATTACK_PERIOD_HASTE = 2 #sec
        self.CAST_PERIOD = 6
        #self.CAST_PERIOD_MAGE = 3

        self.ATTACK_WAIT = self.ATTACK_PERIOD   # Used by timer.  Same as ATTACK_PERIOD.
                                    # Amount of time to wait to walk after attacking
        self.MOVE_WAIT = 0.3
        self.CAST_WAIT = self.CAST_PERIOD

        # Game environment variables.
        self.HASTING = False 

        self.WEAPON1=""
        self.WEAPON2=""
                                
        # These variables is a floating point seconds variable used
        # to monitor when the next move can be made.  The idea is
        # to prevent "Please wait 1 second." and instead delay the
        # user's command by exactly the right amount.  Assume this
        # is what the user wants if it is less than a second.

        # Up to date time.time() value of last action.
        self.ATTACK_CLK = -self.ATTACK_WAIT
        self.MOVE_CLK = -self.MOVE_WAIT
        self.CAST_CLK = -self.CAST_WAIT # Last successful cast

        self.HEALTH = 0
        self.MANA = 0

        if(self.LEVEL <= 2):
            self.HEALTH_TO_HEAL = 15
            self.HEALTH_TO_FLEE = 6
            self.MAX_MANA = 3
            self.MANA_TO_ENGAGE = 3
        elif(self.LEVEL <= 3):
            self.HEALTH_TO_HEAL = 27
            self.HEALTH_TO_FLEE = 9
            self.MAX_MANA = 9
            self.MANA_TO_ENGAGE = 3
        elif(self.LEVEL <= 4):
            self.HEALTH_TO_HEAL = 31
            self.HEALTH_TO_FLEE = 11
            self.MAX_MANA = 12
            self.MANA_TO_ENGAGE = 9
        elif(self.LEVEL <= 5):
            self.HEALTH_TO_HEAL= 37
            self.HEALTH_TO_FLEE = 11
            self.MAX_MANA = 15
            self.MANA_TO_ENGAGE = 6           
        elif(self.LEVEL <= 6):
            self.HEALTH_TO_HEAL= 43
            self.HEALTH_TO_FLEE = 17
            self.MAX_MANA = 18
            self.MANA_TO_ENGAGE = 12     
        elif(self.LEVEL <= 7):
            self.HEALTH_TO_HEAL= 50
            self.HEALTH_TO_FLEE = 20
            self.MAX_MANA = 21
            self.MANA_TO_ENGAGE = 15        
        elif(self.LEVEL <= 8):
            self.HEALTH_TO_HEAL= 50
            self.HEALTH_TO_FLEE = 20
            self.MAX_MANA = 24
            self.MANA_TO_ENGAGE = 15        
        else:
            self.HEALTH_TO_HEAL = 58
            self.HEALTH_TO_FLEE = 26
            self.MAX_MANA = 27
            self.MANA_TO_ENGAGE = 6

        self.MONSTER_LIST=[]

        # All lists are mutually exclusive except for 'preferred' (bottom)
        # 1-8 exp
        self.__lvl1_monsters = [
            "dustman", "small girl", "young boy", "old woman",
            "old man", "townsman", "stall holder", "duck", "hedgehog", 
            "piglet", 'streetsweeper', 
            "shopper", "window shopper", "window cleaner",
            "waitress", "housewife", "squirrel", "milk maid", "rabbit", 
            "one man band",
            "heather seller", "irate teenager", 'peasant', 'one-armed beggar',
            "village elder", "small dog", "tribesman", "searcher", 
            "delivery boy",
            "traveller", "wanderer", "villager", "rich kid", "vagrant",
            "dropout", "tramp", "serf", 'dishwasher']     
        self.__lvl1_red_monsters = [
            "old kobold", "kobold child", "kobold dam", ]
        # 8-15 exp
        self.__lvl2_monsters = [
            "hawker", "barmaid", "smelly beggar", "black crow"
            "sheep", "goose", "penitent", "singer", "musician", "spiv",
            "bidder", "dairy cow", "scholar", "juggler",  "acolyte",
            "shepherd", "gazelle", 'dancer', 'jongleur',
            'tabby cat', 'clerk', 'stablehand', 'bladesman'] 
        # acolytes are good (chalices) but can cause
        # some difficulty... they pile up north of the
        # chapel and kill you when you least expect
        self.__lvl2_red_monsters = [ 
			"kobold sentry", "blond hooker", "sultry hooker", 
			"kobold", "spiv",
            "kobold miner", "kobold archer", 'angry hooker',
            "angry kobold", 'red axer', 'pickpocket', 'thug'
        	] 
        # pickpockets drop leather collars and masks
        # red axer drops studded leather collar
        # cat might be lvl 1 not sure
        # thugs hostile.  They drop leather collar

        # 25-35 exp
        self.__lvl3_monsters = [
            "market official", "robed pilgrim", 
            "street trader", "field worker", "harvester", "horse", "cow",
            "doorman", "stilt walker",  "messenger", "cashier",
            "thatcher",  "tax inspector", "theatre goer", 
            "drunken miner", 'journeyman',
            ]
        self.__lvl3_red_monsters = [
            "large kobold", "insane kobold", "kobold scout",
            'drunk'
            ]
        # 45-60 exp
        self.__lvl4_monsters = [
            "actor", "actress", "grip","merchant", 
            "journeyman", "logger", 'trader',
            "butcher", "young knight", "acrobat", 
            "logger", #"auctioneer", # auctioneers are darn annoying, leave them out!
            "militia soldier", "carpenter", "stagehand",
            'hungry spider', 'cook']
        # hungry spiders are hostile
        self.__lvl4_red_monsters = [
            "kobold shaman", "drunken trouble-maker", "kobold champion"]
        
        self.__lvl5_monsters = [
			"dwarven farm hand", "dwarven barmaid", 
            ]
        self.__lvl5_red_monsters = [
            'large bandit',
			"kobold guard", "mugger", 'large spider'
			]
        # kobold guard and mugger are in groups of three and 
        # aren't actually level 5...
        self.__lvl6_monsters = [
			"dwarven field worker", "dwarven bartender", "school teacher",
			'lyrist', "nobleman", "fort sentry", "fur trader", 
			"bandit swordsman", "bull", "hunter", 'usher',
            'sword swallower', 'archer'
			]
        self.__lvl6_red_monsters = [
            'gnoll sentry'
            ]
            # bull and hunter might be wrong (too high).
        self.__lvl7_monsters = [
			"dwarven cook", "swordsman", 'fort sergeant',
			'oremaster', 
			'giant spider'
			]
        # giant spiders are hostile
        self.__lvl8_monsters = [
            'owlbear'
			]
        self.__lvl9_monsters = [
			"dwarven blacksmith"
			]
        
        # A list of monsters redundant to the above lists that
        # I may want to kill even if they are too low of level.
        # Mostly hostiles and things that don't let you loot.
        self.__preferred_lvl_1_2_monsters = [
            "oaf", "wanderer", #"acolyte", 
            "thug", "spiv", "kobold sentry", "tired hooker", 
            "blond hooker", "angry hooker", "journeyman" ] 
        # prefer kobold sentry for missile weapon drops (bow/spear)
        
        
        
        self.MONSTER_KILL_LIST = []
        
        if(self.LEVEL < 4):
            self.MONSTER_KILL_LIST.extend(self.__lvl1_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl1_red_monsters)
        elif(self.LEVEL < 6):
            self.MONSTER_KILL_LIST.extend(self.__lvl1_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl1_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl2_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl2_red_monsters)
        elif(self.LEVEL < 7):
            self.MONSTER_KILL_LIST.extend(self.__lvl1_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl1_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl2_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl2_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl3_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl3_red_monsters)
        elif(self.LEVEL < 8):
            self.MONSTER_KILL_LIST.extend(self.__preferred_lvl_1_2_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl1_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl2_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl3_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl3_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl4_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl4_red_monsters)
        elif(self.LEVEL < 9):
            self.MONSTER_KILL_LIST.extend(self.__preferred_lvl_1_2_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl1_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl2_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl3_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl3_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl4_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl4_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl5_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl5_red_monsters)
        else:
            self.MONSTER_KILL_LIST.extend(self.__preferred_lvl_1_2_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl1_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl2_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl3_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl3_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl4_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl4_red_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl5_monsters)
            self.MONSTER_KILL_LIST.extend(self.__lvl5_red_monsters)


        self.INVENTORY_LIST = []
        # should probably depend on level.
        self.KEEP_LIST = ["large bag", "large sack", "silver chalice",
            "steel bottle", 'war hammer'
            "adamantine sword", 'adamantine axe', "claymore", 
            "poison ring", "spider leg", "small restorative", 
            "spear", "bolos", 'javelin', 
            "heathen amulet",
            "hard cap", "hard gloves", "hard boots", "panteloons",
            "travellers cross", "leather mask", "leather collar",
            "studded leather collar", "mountain boots with crampons",
            "mountain gloves",
            "chain mail armour", 'chain mail sleeves', 'chain mail leggings', 
            'chain mail gloves', 'chain mail hood', 'chain mail boots', 
            "ring mail armour", "ring mail sleeves", "ring mail leggings", 
            "ring mail hood", "ring mail gauntlets", "leather collar", 
            "furry cloak", 
            'heavy crossbow', 'lion charm', 
            'glowing potion' ] 
       
        self.MUD_RETURN_ITEM_SOLD = False

        self.MOBS_JOINED_IN = []
        self.MOBS_ATTACKING = []

        self.SUCCESSFUL_GO = False
        self.GO_BLOCKING_MOB = ""
        self.GO_PLEASE_WAIT = False
        self.GO_NO_EXIT = False
        self.GO_TIMEOUT = False
        
        self.MINIMUM_SLEEP_BETWEEN_COMMANDS=0.4

        self.AURA_LIST = ['demonic red', 'ominous red', 'ghastly red', 'murky red',
                     'red', 'rusty', 'dusty red', 'grey',
                     'dusty blue', 'pale blue', 'blue',
                     'deep blue', 'bright blue', 'heavenly blue']
        # note... never uses "an"  (ie. "You glow with _a_ ominous red aura")
        
        self.AURA_SCALE = 8 #grey
        self.AURA = self.AURA_LIST[self.AURA_SCALE]
        
        self.AURA_PREFERRED_SCALE = 10 # pale blue
        self.AURA_PREFERRED = self.AURA_LIST[self.AURA_PREFERRED_SCALE]
        
        self.START_TIME = time.time()
        
