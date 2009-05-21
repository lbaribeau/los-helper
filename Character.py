

class Character():

    # This is a class that holds a bunch of data,
    # mostly obtained by the MUD read thread.

    def __init__(self):
        # character init function sets variables to default (initial)
        # values.  
    
        self.ATTACK_PERIOD = 3 #sec
        self.ATTACK_PERIOD_HASTE = 2 #sec
        self.CAST_PERIOD = 6
        #self.CAST_PERIOD_MAGE = 3

        # Constants
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

        self.HEALTH_TO_HEAL = 52
        self.HEALTH_TO_FLEE = 20 # Note: if the bot flees, it stops forever.
        self.MAX_MANA = 24
        self.MANA_TO_ENGAGE = 6

        # Bot variables
        self.MONSTER_CHECK_FLAG = 0
        self.MONSTER_LIST=[]
#        self.MONSTER_KILL_LIST = [ "dustman", "small girl", "young boy", "old woman",
#            "old man", "townsman", "stall holder", "duck", "hedgehog", "piglet",
#            "shopper", "window shopper", "old kobold", "kobold child", "kobold dam", 
#            "waitress", "housewife", "squirrel", "milk maid", "rabbit", "one man band",
#            "heather seller", "irate teenager", "blond hooker", "sultry hooker",
#            "village elder", "small dog", "tribesman", "searcher", "delivery boy",
#            "oaf", "traveller", "wanderer", "villager", "rich kid", "vagrant",
#            "dropout", "tramp", "serf", "wanderer", "vagrant", 
                                                  # Vagrant can be near coral guards.
        
 #           "hawker", "kobold sentry", "barmaid", "smelly beggar", "spiv", "black crow",
        self.MONSTER_KILL_LIST = ["old kobold", "kobold child", "kobold dam", "blond hooker", 
            "sultry hooker", "kobold sentry", "spiv",
            "oaf", "journeyman", 
            "sheep", "goose", "penitent", "singer", "musician", "acolyte",
            "bidder", "dairy cow", "scholar", "juggler", 
            "shepherd", "gazelle", "kobold miner", "kobold archer", "angry kobold",
        #MONSTER_KILL_LIST = [ "oaf", "acolyte", "journeyman", "spiv","kobold child",
        #                      "wanderer", "kobold sentry", "kobold miner", 
            "market official", "pickpocket", "robed pilgrim", "merchant", "large kobold",
            "kobold guard", "street trader", "field worker", "harvester", "horse", "cow",
            "doorman", "stilt walker",  "messenger", "cashier", "kobold",
            "thatcher",  "tax inspector",
            "actor", "actress", "theatre goer", "kobold shaman", 
            "journeyman", "logger", "insane kobold", "kobold scout", "drunken trouble-maker", 
            "kobold champion", "butcher", "young knight", "acrobat", "drunken miner",
            "logger", #"auctioneer", # auctioneers are darn annoying, leave them out!
            "militia soldier", "carpenter", "stagehand", # "kobold priest", #priests make me too good.
            "nobleman", 
            "fort sentry", "fur trader", "hunter",
            "bandit swordsman", "large bandit", "bull",]#, "usher"]#,
            #"sentry", "farm foreman"]  # 140 experience... but bad idea! (there are two next to eachother & they join)

        self.INVENTORY_CHECK_FLAG = 0
        self.INVENTORY_LIST = []
        self.KEEP_LIST = ["large bag", "silver chalice", "steel bottle",
                     "adamantine sword", "claymore", "poison ring", 
                     "spider leg", "scimitar", "small restorative", 
                     "spear", "bolos", 'javelin', "leaf blade", "heathen amulet", 
                     "chain mail armour", 'chain mail sleeves', 'chain mail leggings', 
                     'chain mail gloves', 'chain mail hood', 'chain mail boots', 
                     "ring mail armour", "ring mail sleeves", "ring mail leggings", 
                     "ring mail hood", "ring mail gauntlets", "leather collar", 
                     "furry cloak", "white amulet", "white potion", 
                     "stilleto", 'rapier', 'heavy crossbow'] 
                    #"brass ring", "copper ring", "silver ring",
                     #"diamantium ring", "platinum ring", "iron ring"]
        self.SELL_LIST = []
        self.DROP_LIST = []  # global because 'bot.go' function calls sell_items and
                        # drop_items and is in no position to pass parameters

        self.SELL_CHECK_FLAG = 0
        self.MUD_RETURN_ITEM_SOLD = False

        self.EXPERIENCE = 0
        self.GOLD = 0

        self.MOBS_JOINED_IN = []

        self.CHECK_GO_FLAG = 0
        self.SUCCESSFUL_GO = False
        self.BLOCKING_MOB = ""

        self.AURA_CHECK_FLAG = 0
        self.AURA_LIST = ['demonic red', 'ominous red', 'ghastly red', 'murky red',
                     'red', 'rusty', 'dusty red', 'grey',
                     'dusty blue', 'pale blue', 'blue',
                     'deep blue', 'bright blue', 'heavenly blue']
        # note... never uses "an"  (ie. "You glow with _a_ ominous red aura")
        self.AURA = "grey"
        self.AURA_SCALE = 8
        self.AURA_PREFERRED = "pale blue"
        self.AURA_PREFERRED_SCALE = 10
        