

class GameObject(object):
    # def __getitem__(self, key):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.obj.name
        else:
            return self.name == other

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.name < other.name
        else:
            return self.name < other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 0
        # return self.name

# class FakeItem(object):
#     def __init__(self, name):
#         self.name = name
#         self.unusable = False

#     def to_string(self):
#         return self.__str__()

#     def __str__(self):
#         return self.name

#     def __repr__(self):
#         return self.name

#     def __eq__(self, other):
#         if other.__class__ == 'str'.__class__:
#             return self.name == other
#         else:
#             return self.name == other.name

#     def __lt__(self, other):
#         if other.__class__ == 'str'.__class__:
#             return self.name < other
#         else:
#             return self.name < other.name

#     def __ne__(self, other):
#         if other.__class__ == 'str'.__class__:
#             return self.name > other
#         else:
#             return self.name > other.name

#     def __hash__(self):
#         return 0
