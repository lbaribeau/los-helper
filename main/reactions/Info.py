
from BotReactions import BotReactionWithFlag
from Aura import Aura

from misc_functions import magentaprint

class Info(BotReactionWithFlag):
    header = "     (\S+) the (.+?), a (.+?) of the (1st|2nd|3rd|\d\d?th) level    "
    your_preferred = "Your preferred alignment is (.+?)     "
    first =  "\|       Str : (\d+) +\|  \|     Sharp   : (\d+) *%  \|  \|     Earth : (\d+) *%     \|\n\r" + \
            " \|       Dex : (\d+) +\|  \|     Thrust  : (\d+) *%  \|  \|     Wind  : (\d+) *%     \|\n\r" + \
            " \|       Con : (\d+) +\|  \|     Blunt   : (\d+) *%  \|  \|     Fire  : (\d+) *%     \|\n\r" + \
            " \|       Int : (\d+) +\|  \|     Pole    : (\d+) *%  \|  \|     Water : (\d+) *%     \|\n\r" + \
            " \|       Pty : (\d+) +\|  \|     Missile : (\d+) *%  \|  \|    Astral : (\d+)"
    second = \
                                       "   Exp : (\d+) +\|  \| GameTime : +(\d+:\d\d:\d\d) +\|\n\r" + \
        " \|    Max HP : (\d+) +\|  \|    Gold : (\d+) +\|  \| Game Age : (\d+) +\|\n\r" + \
        " \|   Curr MP : \d+ +\|  \|  -Needed to Level-  \|  \| +\|\n\r" + \
        " \|    Max MP : (\d+) +\|  \|     Exp : (\d+) +\|  \|   Weight : (\d+) +\|\n\r" + \
        " \|        AC : (-?\d+) +\|  \|    Gold : (\d+) +\|  \|  Objects : (\d+)"

    regexes = [header, your_preferred, first, second]

    got_first = False
    got_second = False

    def __init__(self, mudReaderHandler, telnetHandler, character):
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        self.character = character

    def execute(self):
        self.got_first = False
        self.got_second = False
        self.mudReaderHandler.register_reaction(self)
        self.telnetHandler.write("info")
        self.wait_for_flag()
        self.mudReaderHandler.unregister_reaction(self)

    def notify(self, regex, M_obj):
        # pass in character, or just edit self?
        if regex is self.header:
            self.character.name = M_obj.group(1)
            self.character.race = M_obj.group(2)
            self.character.title = M_obj.group(3)
            # self.character.level = int(re.search("\d+",M_obj.group(4)).group(0))
            self.character.level = int(M_obj.group(4)[:len(M_obj.group(4))-2])
        elif regex is self.your_preferred:
            self.character.preferred_alignment = M_obj.group(1)
            # self.character.AURA_PREFERRED_SCALE = self.auras.index(preferred_alignment)
            self.character.AURA_PREFERRED_SCALE = Aura(M_obj.group(1)).auras.index(M_obj.group(1))
            self.character.AURA_PREFERRED = M_obj.group(1)
            magentaprint(self.character.preferred_alignment)
            magentaprint(self.character.AURA_PREFERRED_SCALE)
            magentaprint(self.character.AURA_PREFERRED)
        elif regex is self.first:
            self.got_stats_skills = True
            self.character.str = M_obj.group(1)
            self.character.dex = M_obj.group(4)
            self.character.con = M_obj.group(7)
            self.character.int = M_obj.group(10)
            self.character.pty = M_obj.group(13)
            self.character.sharp = M_obj.group(2)
            self.character.thrust = M_obj.group(5)
            self.character.blunt = M_obj.group(8)
            self.character.pole = M_obj.group(11)
            self.character.missile = M_obj.group(14)
            self.character.earth = M_obj.group(3)
            self.character.wind = M_obj.group(6)
            self.character.fire = M_obj.group(9)
            self.character.water = M_obj.group(12)
            self.character.astral = M_obj.group(15)
            self.got_first = True
            # magentaprint(self.character.astral)
        elif regex is self.second:
            self.character.exp = int(M_obj.group(1))
            self.character.gametime = M_obj.group(2)
            self.character.maxHP = int(M_obj.group(3))
            self.character.gold = int(M_obj.group(4))
            self.character.age = int(M_obj.group(5))
            self.character.maxMP = int(M_obj.group(6))
            self.character.exp_to_level = int(M_obj.group(7))
            self.character.weight = int(M_obj.group(8))
            self.character.AC = int(M_obj.group(9))
            self.character.gold_to_level = int(M_obj.group(10))
            self.character.objects = int(M_obj.group(11))
            self.got_second = True
            self.__waiter_flag = True
            # magentaprint("Objects: " + str(self.character.objects))

        @property 
        def success(self):
            return got_first and got_second



    # stats_skills = \
    #     "\|       Str : (\d+) +\|  \|     Sharp   : (\d+) *%  \|  \|     Earth : (\d+) *%     \| +\n\r" + \
    #   " +\|       Dex : (\d+) +\|  \|     Thrust  : (\d+) *%  \|  \|     Wind  : (\d+) *%     \| +\n\r" + \
    #   " +\|       Con : (\d+) +\|  \|     Blunt   : (\d+) *%  \|  \|     Fire  : (\d+) *%     \| +\n\r" + \
    #   " +\|       Int : (\d+) +\|  \|     Pole    : (\d+) *%  \|  \|     Water : (\d+) *%     \| +\n\r" + \
    #   " +\|       Pty : (\d+) +\|  \|     Missile : (\d+) *%  \|  \|    Astral : (\d+) *%"
    # sharp_earth =    "     Sharp   : (\d+) *%  |  |     Earth : (\d+) *%     |" 
    # thrust_water =   "     Thrust  : (\d+) *%  |  |     Water : (\d+) *%     |"
    # blunt_fire =     "     Blunt   : (\d+) *%  |  |     Fire  : (\d+) *%     |"
    # pole_wind =      "     Pole    : (\d+) *%  |  |     Wind  : (\d+) *%     |"
    # missile_astral = "     Missile : (\d+) *%  |  |     Astral: (\d+) *%     |"  # Check these, wouldn't want to crash at 100%
    # regexes = [self.header, self.your_preferred, self.sharp_earth, self.thrust_water, self.blunt_fire, self.pole_wind, self.missile_astral]
  
        #         magentaprint("Nonetype...")
        #         magentaprint(M_obj)
        #         magentaprint(M_obj.group(0))
        #         magentaprint(M_obj is None)
        #         magentaprint(M_obj.group(1) is None)
        #         # Why am I even getting here with a bad regex. 
        #         # 
        #         magentaprint(M_obj.groupdict())
        #         magentaprint(M_obj.start())
        #         magentaprint(M_obj.end())
        #         magentaprint(M_obj.pos)
        #         magentaprint(M_obj.endpos)
        #         if M_obj:
        #             magentaprint("M_obj")
        #         else:
        #             magentaprint("not M_obj")
        #         magentaprint(M_obj.group(1))
        #         magentaprint(M_obj.group(2))
        #         magentaprint(M_obj.group(3))

    # Doing it in one regex!?  There seems to be a max length issue of some sort.  It stops working at 
    # the C in "Curr HP"
    #         info = "\|       Str : (\d+) +\|  \|     Sharp   : (\d+) *%  \|  \|     Earth : (\d+) *%     \|\n\r" + \
    #               " \|       Dex : (\d+) +\|  \|     Thrust  : (\d+) *%  \|  \|     Wind  : (\d+) *%     \|\n\r" + \
    #               " \|       Con : (\d+) +\|  \|     Blunt   : (\d+) *%  \|  \|     Fire  : (\d+) *%     \|\n\r" + \
    #               " \|       Int : (\d+) +\|  \|     Pole    : (\d+) *%  \|  \|     Water : (\d+) *%     \|\n\r" + \
    #               " \|       Pty : (\d+) +\|  \|     Missile : (\d+) *%  \|  \|    Astral : (\d+) *%     \|\n\r" + \
    #               r" \\=====================[/]  \\=====================[/]  \\======================[/]\n\r" + \
    #               "(\s)*\n\r" + \
    #               r" [/]===== Status 1 ======\\  [/]====== Status 2 =====\\  [/]=====  Status 3 ======\\" + "\n\r" + \
    #               " \|   Curr HP : \d+ +\|  \|     Exp : (\d+) +\|  \| GameTime : +(\d+:\d\d:\d\d) +\|\n\r"
    #               " \|    Max HP : (\d+) +\|  \|    Gold : (\d+) +\|  \| Game Age : (\d+) +\|\n\r" + \
    #               " \|   Curr MP : \d+ +\|  \|  -Needed to Level-  \|  \| +\|\n\r" + \
    #               " \|    Max MP : (\d+) +\|  \|     Exp : (\d+) +\|  \|   Weight : (\d+) +\|\n\r" + \
    #               " \|        AC : (-?\d+) +\|  \|    Gold : (\d+) +\|  \|  Objects : (\d+)"
    #               r" [/]===== Status 1 ======\\  [/]====== Status 2 =====\\  [/]=====  Status 3 ======\\\n\r"

