from misc_functions import *
# from command.Command import Command

class Aura(object):

    auras = ['demonic red', 'ominous red', 'ghastly red', 'blood red', 'murky red',
              'red', 'rusty', 'dusty red', 'grey',
              'dusty blue', 'pale blue', 'blue',
              'deep blue', 'bright blue', 'shimmering blue', 'blazing blue',
              'blazing blue', 'heavenly blue']
             # 0-8 red, 9 grey, 10-18 blue

    def __init__(self, s):
        if s in self.auras:
            self.s = s
        else:
            magentaprint("Error: created an aura with an invalid name: " + s)

    # Add/subtract integers with auras for intuitive results
    # Adding/subtracting only works with integers
    # ex: red + 3 = grey

    def __add__(self, other):
        # return self.clamp(self.auras.index(self.s) + other)
        return self.clamp(self.index() + other)

    __radd__ = __add__

    def __sub__(self, other):
        return self.clamp(self.index() - other)

    def __rsub__(self, other):
        return self.clamp(other - self.index())

    def __str__(self):
        return self.auras[self.index()]

    # Comparators work with other Aura types and other strings
    def __lt__(self, other):
        # if isinstance(other, str):
        #     return self.index() < self.auras.index(other)
        # elif isinstance(other, int):
        #     return self.index() < other
        # else:
        #     # if other.__class__ == ''.__class__:
        #     return self.index() < other.index
        return self.index() < self.get_index_from_unknown_type(other)

    def __le__(self, other):
        # return self.auras.index(self.s) <= self.auras.index(other.s)
        return self.index() <= self.get_index_from_unknown_type(other)

    def __eq__(self, other):
        return self.index() == self.get_index_from_unknown_type(other)

    def __ne__(self, other):
        return self.index() != self.get_index_from_unknown_type(other)

    def __ge__(self, other):
        return self.index() >= self.get_index_from_unknown_type(other)

    def __gt__(self, other):
        return self.index() > self.get_index_from_unknown_type(other)

    def clamp(self, i):
        return max(0, min(i,len(self.auras)))

    def index(self):
        return self.auras.index(self.s)

    def get_index_from_unknown_type(self, unk):
        if isinstance(unk, str):
            return self.auras.index(unk)
        elif isinstance(unk, int):
            return unk
        else:
            return unk.index()

