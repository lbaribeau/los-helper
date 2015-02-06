import collections
from Exceptions import *
from misc_functions import *

class MudObjectDict():
    dictionary = {}
    parser_func = None

    def __init__(self, parser_func):
        self.parser_func = parser_func

    def sort(self):
        self.dictionary = collections.OrderedDict(sorted(self.dictionary.items()))

    def count(self):
        count = 0

        for obj in self.dictionary.items():
            magentaprint(obj, False)
            olist = self.dictionary[obj]
            count += len(olist.objs)

        return count


    def add(self, obj_string):
        objs = self.parser_func(obj_string)

        for obj, qty in objs.items():
            MudObjectDict.add_to_qty_dict(self.dictionary, (obj, qty))

        self.sort()

    def remove(self, obj_string):
        objs = self.parser_func(obj_string)

        for keyvalue in objs:
            try:
                MudObjectDict.remove_from_qty_dict(self.objs, (keyvalue, objs[keyvalue]) )
            except Exception as e:
                magentaprint(e)
                magentaprint("Couldn't remove '" + str((keyvalue, objs[keyvalue])) + "' from inventory.")
                magentaprint("obj_string: <" + obj_string + ">")

    def get_unique_references(self, exception_list = []):
        references = []
        numbered_references = []

        for obj in self.dictionary:
            references.append(obj.reference)

        for objs in self.inventory:
            if (objs not in exception_list):
                prev_objss_with_same_reference = references.count(objs.reference)

                numbered_references.extend([objs.reference + " " +
                 str(n) for n in range(prev_objss_with_same_reference, prev_objss_with_same_reference + int(self.dictionary[objs]))])

        # numbered_references.sort() 
        numbered_references.reverse() 
        return numbered_references

    @staticmethod
    def add_to_qty_dict(d, keyvalue):
        ''' For (key, qty) pairs. '''

        if keyvalue[0] in d:
            d[keyvalue[0]].add(keyvalue[1])
        else:
            d[keyvalue[0]] = keyvalue[1]

    @staticmethod
    def remove_from_qty_dict(d, keyvalue):
        ''' For (key, qty) pairs. '''

        magentaprint(str(keyvalue))

        if keyvalue[0] in d:
            if keyvalue[1].qty >= d[keyvalue[0]].qty:
                del d[keyvalue[0]]
            else:
                d[keyvalue[0]].remove() #keyvalue[1]
        else:
            magentaprint("Couldn't remove " + str(keyvalue[0]), False)