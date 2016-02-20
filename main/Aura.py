
# from command.Command import Command

class Aura(object):

<<<<<<< HEAD
    auras = ['demonic red', 'ominous red', 'ghastly red', 'blood red', 'murky red',
              'red', 'rusty', 'dusty red', 'grey',
              'dusty blue', 'pale blue', 'blue',
              'deep blue', 'bright blue', 'shimmering blue', 'blazing blue',
              'blazing blue', 'heavenly blue']
             # 0-8 red, 9 grey, 10-18 blue
=======
    auras = [
        'demonic red', 'ominous red', 'ghastly red', 'blood red', 'murky red',
        'red', 'rusty', 'dusty red', 'grey',
        'dusty blue', 'pale blue', 'blue',
        'deep blue', 'bright blue', 'shimmering blue', 'blazing blue', 'heavenly blue'
    ]
    # 0-7 red, 8 grey, 9-16 blue  (17 total)
    # note... never uses "an"  (ie. "You glow with _a_ ominous red aura")
>>>>>>> master

    def __init__(self, s):
        if s in self.auras:
            self.s = s
        else:
            magentaprint("Error: created an aura with an invalid name: " + s)

    # Add/subtract integers with auras for intuitive results
    def __add__(self, other):
        return self.clamp(self.auras.index(self.s) + other)

    __radd__ = __add__

    def __sub__(self, other):
        return self.clamp(self.auras.index(self.s) - other)

    def __rsub__(self, other):
        return self.clamp(other - self.auras.index(self.s))

    def __lt__(self, other):
        return self.auras.index(self.s) < self.auras.index(other.s)

    def __le__(self, other):
        return self.auras.index(self.s) <= self.auras.index(other.s)

    def __eq__(self, other):
        return self.auras.index(self.s) == self.auras.index(other.s)

    def __ne__(self, other):
        return self.auras.index(self.s) != self.auras.index(other.s)

    def __ge__(self, other):
        return self.auras.index(self.s) >= self.auras.index(other.s)

    def __gt__(self, other):
        return self.auras.index(self.s) > self.auras.index(other.s)

    def clamp(self, i):
        return max(0, min(i,len(self.auras)))

