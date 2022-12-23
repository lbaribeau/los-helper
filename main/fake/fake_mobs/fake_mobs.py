
# from fake.fake_mobs.fake_mob import FakeMob
from fake.FakeItem import FakeItem
from misc_functions import magentaprint

class FakeMob(object):
    def __init__(self, fake_character, socket_output_array):
        self.char = fake_character
        self.socket_output = socket_output_array
        self.rng = 0

    def do_combat(self):
        self.increment_rng()
        magentaprint("FakeMob rng: " + str(self.rng))
        if self.rng == 0:
            self.mobdead()
            return True
        else:
            self.sub_combat(self.rng)

    def increment_rng(self):
        self.rng = (self.rng + 1) % 3

    def mobdead(self):
        self.socket_output.append('Your attack overwhelms the ' + self.name + ' and he collapses!\nYour enemy, the ' + self.name + ' has been defeated.\nYou gain 11 experience.\n')

class Actor(FakeMob):
    def __init__(self, fake_character, socket):
        super().__init__(fake_character, socket)
        self.name = 'actor'  # This part could be automated, parsing the class name

    def sub_combat(self, rng):
        self.socket_output.append('[%s H %s M]: The %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
        if rng == 1:
            self.socket_output.append("Your iron ring fell apart.\n\r")
            ring = FakeItem('iron ring')
            ring.usable = False
            self.char.inv.add(ring)

class TabbyCat(FakeMob):
    def __init__(self, fake_character, socket):
        super().__init__(fake_character, socket)
        self.name = 'tabby cat'

    def do_combat(self):
        magentaprint("Fake rng: " + str(self.rng))
        self.rng = (self.rng + 1) % 5  # He only needs to hit you twice unless you heal super quick
        if self.rng == 1:
            self.rng1()
        if self.rng == 4:
            self.mobdead()
            return True
        # elif self.rng == 1:
        #     self.char.hp = max(self.char.hp - 60, 0)
        #     self.socket_output.append('[%s H %s M]: The tabby cat painfully head-butts you for 60 damage.\n\r' % (self.char.hp, self.char.mp))
        #     if self.char.hp == 0:
        #         self.char.hp = 1
        #         self.socket_output.append("You are overwhelmed by the tabby cat's attack and you collapse!\n\r")
        elif not self.rng % 2:
            dmg = self.char.hp - 2
            self.char.hp = 2
            # self.socket_output.append('[%s H %s M]: The %s painfully head-butts you for %s damage.\n\r' % (self.char.hp, self.char.mp, self.name, dmg))
            self.socket_output.append('The %s painfully head-butts you for %s damage.\n\r' % (self.name, dmg))
            # self.socket_output.append('[%s H %s M]: ' % (self.char.hp, self.char.mp))
            # if self.char.hp == 0:
            #     self.char.hp = 1
            #     self.socket_output.append("You are overwhelmed by the tabby cat's attack and you collapse!\n\r")
        self.socket_output.append('[%s H %s M]: ' % (self.char.hp, self.char.mp))

    def rng1(self):
        if self.char.inv.has('scarlet potion'):
            # self.socket_output.append('[%s H %s M]: You drop %s scarlet potions.' % (self.char.hp, self.char.mp, self.char.inv.count('scarlet potion')))
            if self.char.inv.count('scarlet potion') > 20:
                self.socket_output.append('[%s H %s M]: You drop %s scarlet potions.\n\r' % (self.char.hp, self.char.mp, self.char.inv.count('scarlet potion')))
            elif self.char.inv.count('scarlet potion') == 1:
                self.socket_output.append('[%s H %s M]: You drop a scarlet potion.\n\r' % (self.char.hp, self.char.mp))
            else:
                self.socket_output.append(
                    '[%s H %s M]: You drop %s scarlet potions.\n\r' % (self.char.hp, self.char.mp, [
                        'two','three','four','five','six','seven','eight','nine','ten','eleven','twleve','thirteen',
                        'fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty'][self.char.inv.count(
                        'scarlet potion') - 2
                        ])
                )
            self.char.inv.remove_all('scarlet potion')

class Stablehand(TabbyCat):
    def __init__(self, fake_character, socket):
        super().__init__(fake_character, socket)
        self.name = 'stablehand'

    def rng1(self):
        self.socket_output.append('[%s H %s M]: You get nineteen scarlet potions.\n\r' % (self.char.hp, self.char.mp))
        self.char.inv.add_many('scarlet potion', 19)

    # def do_combat(self):
    #     if self.rng == 1:
    #         self.socket_output.append('[%s H %s M]: You get 20 scarlet potions.\n\r' % (self.char.hp, self.char.mp))
    #     super().do_combat()

class BarbarianWarrior(FakeMob):
    def __init__(self, fake_character, socket):
        super().__init__(fake_character, socket)
        self.name = 'barbarian warrior'

    def sub_combat(self, rng):
        self.socket_output.append('[%s H %s M]: The %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
        if rng == 2:
            self.socket_output.append('[%s H %s M]: Your chain mail armour fell apart.\n\r' % (self.char.hp, self.char.mp))
            self.char.inv.add_broken('chain mail armour')

class Tardan(FakeMob):
    def __init__(self, fake_character, socket):
        super().__init__(fake_character, socket)
        self.name = 'Tardan'
    def sub_combat(self, rng):
        magentaprint('Tardan rng is {0}'.format(rng))
        if rng == 1:
            # self.socket_output.append('I am going to break your armour and then drop some of the same.')
            self.socket_output.append('[%s H %s M]: %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
        if rng == 2:
            self.socket_output.append('[%s H %s M]: %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
            self.socket_output.append('[%s H %s M]: Your chain mail armour fell apart.\n\r' % (self.char.hp, self.char.mp))
            self.char.inv.add_broken('chain mail armour') # This is the inventory on the fake side - real inventory will also do this
        if rng == 3:
            self.socket_output.append('[%s H %s M]: %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
    def mobdead(self):
        self.socket_output.append(''                                                +\
            'You heave your maul hammer at Tardan, smashing him for 19 damage.\n\r' +\
            'Your attack overwhelms Tardan and he collapses!\n\r'                   +\
            'Your enemy, Tardan has been defeated.\n\r'                             +\
            'You gain 560 experience.\n\r'                                          +\
            'Tardan was carrying: 99 gold coins, some chain mail armour.\n\r')

class BanditSentry(FakeMob):
    def __init__(self, fake_character, socket):
        super().__init__(fake_character, socket)
        self.name = 'bandit sentry'
    def sub_combat(self, rng):
        if rng == 1:
            # self.socket_output.append('I am going to break your armour and then drop some of the same.')
            self.socket_output.append('[%s H %s M]: %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
        if rng == 2:
            self.socket_output.append('[%s H %s M]: %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
            self.socket_output.append('[%s H %s M]: ' % (self.char.hp, self.char.mp))
            self.socket_output.append('A bandit just arrived.\n\rThe bandit attacks you.\n\rThe bandit sentry punches you for 1 damage.\n\r')
        if rng == 3:
            self.socket_output.append('[%s H %s M]: %s throws a wild punch at you, but it misses.\n\r' % (str(self.char.hp), str(self.char.mp), str(self.name)))
    def mobdead(self):
        self.socket_output.append(''                                                +\
            'You heave your maul hammer at the bandit sentry, smashing it for 19 damage.\n\r' +\
            'Your attack overwhelms the bandit sentry and it collapses!\n\r'                   +\
            'Your enemy, the bandit sentry has been defeated.\n\r'                             +\
            'You gain 50 experience.\n\r'                                          +\
            'The bandit sentry was carrying: 20 gold coins, a horn bow.\n\r')

# class Spiv(FakeMob):
#     def __init__(self, fake_character, socket):
#         super().__init__(fake_character, socket)
#         self.name = 'spiv'
# This was going to be for... You can't carry everything.\n\rYou get ...
# Which I broke when I added ^ to R.you_get
# But I fixed it already




