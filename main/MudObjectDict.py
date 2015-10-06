import collections
from Exceptions import *
from misc_functions import *

class MudObjectDict():
    dictionary = {}

    def __init__(self):
        self.dictionary = {}

    def __len__(self):
        return self.count()

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def to_string(self):
        return str(self.dictionary)

    def sort(self):
        self.dictionary = collections.OrderedDict(sorted(self.dictionary.items()))

    def count(self, obj=None):
        count = 0

        if (obj is not None):
            if obj in self.dictionary.keys():
                count = len(self.dictionary[obj])
        #count everything
        else:
            for obj,qty in self.dictionary.items():
                olist = self.dictionary[obj]
                count += len(olist.objs)

        magentaprint("MudObjectDict counted " + str(count) + " " + str(obj) + ".")
        return count

    def add(self, obj_dict):
        for obj, qty in obj_dict.items():
            MudObjectDict.add_to_qty_dict(self.dictionary, (obj, qty))

        # magentaprint("MudObjectDict added " + str(obj_dict.keys()))
        self.sort()

    def remove(self, obj_dict):
        for keyvalue in obj_dict:
            try:
                MudObjectDict.remove_from_qty_dict(self.dictionary, (keyvalue, obj_dict[keyvalue]) )
            except Exception as e:
                magentaprint(e)
                magentaprint("Couldn't remove '" + str((keyvalue, obj_dict[keyvalue])) + "' from inventory.")
                # magentaprint("obj_string: <" + obj_string + ">")

    def get_object_of_type(self, model, data, level=-1):
        for obj in self.dictionary:
            if obj.is_of_type(model, data, level):
                for instance in self.dictionary[obj].objs:
                    if not instance.is_unusable:
                        return obj.obj.name

    def get_unique_references(self, exception_list = []):
        references = collections.OrderedDict(sorted({}))
        numbered_references = []

        for obj,qty in self.dictionary.items():
            if obj in exception_list:
                # magentaprint("Found in exception_list " +  str(obj), False)
                for index, gobj in enumerate(qty.objs):
                    qty.objs[index].conserve = True
            self.add_to_qty_dict(references, (obj.reference, qty))

        for obj,qty in references.items():
            i = 0
            while i < int(qty):
                cur_gobj = qty.objs[i]
                i += 1
                if not cur_gobj.conserve:
                    numbered_references.append(obj + " " + str(i))

        numbered_references.reverse()

        # magentaprint(numbered_references, False)

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
        ''' key/value pair (list of two)
        First item is the key (string)
        Second item is the quantity to remove (int)
        If the quantity is high enough to remove all of that item, then the item name also gets removed from the dictionary.
        '''
        # Problem:  Not working
        # Example: One small knife.  Drop small knife correctly.  18 small knives now in dictionary.  (18 small restoratives the entire time.)
        # ''' For (key, qty) pairs. '''

        # magentaprint(str(keyvalue))

        if keyvalue[0] in d:
            if keyvalue[1].qty >= d[keyvalue[0]].qty:
                del d[keyvalue[0]]
            else:
                d[keyvalue[0]].remove() #keyvalue[1]
        else:
            magentaprint("Couldn't remove " + str(keyvalue[0]), False)
        
        # if keyvalue[0] in d:
        #     if keyvalue[1] >= d[keyvalue[0]]:
        #         del d[keyvalue[0]]
        #     else:
        #         d[keyvalue[0]] = d[keyvalue[0]] - keyvalue[1]


