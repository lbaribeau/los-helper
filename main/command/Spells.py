
from comm import RegexStore
from misc_functions import magentaprint
from command.Command import SimpleCommand

burn = 'burn'
rumble = 'rum'
blister = 'blis'
hurt = 'hu'
dustgust = 'dust'
fireball = 'fireb'
waterbolt = 'water'
crush = 'crush'

vigor = 'v'
mendwounds = 'm'
light = 'l'
showaura = 'show'

lvl1 = [burn, rumble, blister, hurt]
lvl2 = [fireball, crush, waterbolt, dustgust]

class Spells(SimpleCommand):
    command = 'spells'

    def __init__(self, telnetHandler, character):
        self.telnetHandler = telnetHandler
        self.character = character
        # self.regex_list = [RegexStore.spells1[0], RegexStore.spells2[0], RegexStore.spells3[0], RegexStore.spells4[0]]
        # magentaprint(str(self.regex_cart))
        # magentaprint(str(self))
        self.regex_cart = [RegexStore.spells]
        self.init()

    def init(self):
        self.regex_checker = [False, False, False, False, False]
        self.spells = []

    def notify(self, regex, M_obj):
        # self.character.spells = ' '.join((M_obj.group('black'), M_obj.group('white'), M_obj.group('misc'), M_obj.group('buffs'))).lower().split()
        # # self.character.spells = (M_obj.group('black')).lower().split()
        # magentaprint("Spells.notify()")
        # magentaprint(M_obj.group(0))
        # magentaprint(M_obj.group(1))
        # # self.character.spells = (M_obj.group('black')).lower().split()
        # magentaprint(str(self.character.spells))
        # for r in self.regex_cart:
        #     if regex in r:
        #         self.regex_checker[self.regex_cart.index()]
        self.regex_checker[self.regex_cart[0].index(regex)] = True

        # magentaprint("Groups: " + str(M_obj.groups()), True)
        groups = list(M_obj.groups())
        while None in groups:
            groups.remove(None)
        # spells = ' '.join(M_obj.groups()).lower().split()
        spells = ' '.join(groups).lower().split()
        while 'none' in spells:
            spells.remove('none')
        while '|' in spells:
            magentaprint(str(spells))
            spells.remove('|')
        magentaprint('Spells: ' + str(spells), True)
        # if 'level' in spells:
        #     try:
        #         # spells.remove('level')
        #         # spells.remove('earth')
        #         # spells.remove('wind')
        #         # spells.remove('water')
        #         # spells.remove('fire')
        #         # spells.remove('astral')
        #         # spells.remove('1')
        #         # spells.remove('2')
        #         # spells.remove('3')
        #         # spells.remove('4')
        #         # spells.remove('5')
        #     except:
        #         magentaprint("Spells.notify() error removing the extraneous.")

        self.spells.extend(spells)

        # if all(self.regex_checker):
        if sum(self.regex_checker) >= 1:
            self.character.spells = self.spells
            magentaprint(str(self.character.spells), True)
            self.init()
            super().notify(regex, M_obj)
