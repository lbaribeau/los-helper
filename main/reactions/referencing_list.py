
# from main.misc_functions import magentaprint
from print_magenta import magentaprint
from reactions.game_object import GameObject
# from db.GenericMudObject import GenericMudObject

class ReferencingList(object):
    # This is a structure that should help with any set of objects the way the mud server deals with them:
    #  - inventory, mob list, equipment, shop list...
    # these all have similar "word n" object targeting mechanisms, ie. ring 5.

    # We may need MobList and/or ItemList to inherit this to provide specific processes

    def __init__(self, initializer=None):
        if not initializer:
            self.list = []
        elif isinstance(initializer, 'str'.__class__):
            self.list = self.parse(initializer)
        elif isinstance(initializer[0], 'str'.__class__):
            self.list = sorted(GameObject(s) for s in initializer)
        else:
            self.list = sorted(initializer)

        # Children need to support parse methods

        # magentaprint("Referencing list: " + str(self.list))
        self.numbers = [
            'a', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
            'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'
        ] + [str(n) for n in range(20, 200)]

    def add(self, obj_or_string):
        if isinstance(obj_or_string, 'str'.__class__):
            obj = GameObject(obj_or_string)  # This probably causes problems - overwrite add
        else:
            obj = obj_or_string

        # magentaprint("RefList adding %s." % str(obj))
        for i in range(0, len(self.list)):
            if self.list[i] > obj:
                self.list.insert(i, obj)
                # magentaprint("RefList inserted %s at index %s." % (str(obj), str(i)))
                return

        # magentaprint("RefList appended %s." % str(obj))
        # self.list.append(FakeItem(item))
        # self.list.sort()  # We want to keep broken items sorted properly by inserting manually
        # self.list.append(obj)
        self.list = sorted(self.list + [obj])

    def add_from_list(self, list):
        # Could be made more efficient by separating sorting from obj/string managing in add()
        for x in list:
            self.add(x)

    def remove(self, obj):
        # magentaprint("ReferencingList removing " + str(obj))
        self.list.remove(obj)

    def remove_by_ref(self, ref):
        # if item in self.list:
        #     self.list.remove(item)
        self.remove_by_index(self.index(ref))

    def remove_by_index(self, ind):
        self.list.pop(ind)

    def remove_from_list(self, list):
        for x in list:
            self.remove(x)

    def index(self, ref):
        # magentaprint("RefList.index() ref: " + ref)
        if len(ref.split(' ')) >= 2:
            refw, n = ref.split(' ')[0], int(ref.split(' ')[1])
        else:
            refw, n = ref, 1

        # magentaprint("Ref list n: " + str(n))

        # for obj in sorted(list(set(self.list))):
        # magentaprint("RefList list: " + str(self.list))
        # magentaprint("RefList unique list: " + str(sorted(list(set(x.name for x in self.list)))))
        for name in sorted(list(set(x.name for x in self.list))):
            # magentaprint("RefList name: %s, list.count(obj): %s" % (name, str(self.list.count(name))))
            if any(w.startswith(refw) for w in name.split(' ')):
                if n <= self.list.count(name):
                    # magentaprint("RefList.index returning " + str(self.list.index(name)+n-1))
                    return self.list.index(name) + n - 1
                else:
                    n = n - self.list.count(name)

        # for obj in self.list:
        #     if any(w.startswith(refw) for w in obj.name.split(' ')):

    def get(self, ref):
        i = self.index(ref)

        if i is not None:
            return self.list[i]

    def set_unusable(self, ref):
        self.get(ref).unusable = True

    def has(self, string):
        for i in self.list:
            if i.name == string:
                return True

        return False

    def remove_all(self, name):
        self.list = [x for x in self.list if x.name != name]

    def add_many(self, name, qty):
        for i in range(0,qty):
            self.add(name)
            # ... the easy way

    def count(self, obj):
        return self.list.count(obj)
        # return self.list.count(GenericMudObject(string))

    def __len__(self):
        return len(self.list)

    def to_string(self):
        return str(self.list)

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def sort(self):
        self.list.sort()

    def get_object_of_type(self, model, data, level=-1):
        for obj in self.list:
            if obj.is_of_type(model, data, level):
                for instance in self.dictionary[obj].objs:
                    if not instance.is_unusable:
                        return str(obj.obj)

    def get_reference(self, obj, first_or_second_word=1):
        if isinstance(obj, 'str'.__class__):
            return self.get_first_reference(obj, first_or_second_word)
        else:
            # Assume the exact object
            count_similar_obj = 0
            for list_obj in self.list:
                if obj is list_obj:
                    # return _reference_string(obj.name, count_similar_obj+1)
                    first_ref = self.get_first_reference(str(obj), first_or_second_word)
                    word = first_ref.split(' ')[0]
                    ref_n = int(first_ref.split(' ')[1]) if len(first_ref.split(' ')) >= 2 else 1
                    return self._reference_string(word, ref_n + count_similar_obj)
                    # return self._reference_string(first_ref[0], ref_n + count_similar_obj)

                if str(obj) == str(list_obj):
                    count_similar_obj = count_similar_obj + 1

    def get_first_reference(self, name, first_or_second_word=1):
        words = name.strip().split(' ')
        # self.inventory.sort()  # I think we can assume that proper housekeeping has been done
        # Algorithm: Use the first word in the item.  Count the items in the inventory that also 
        # use that word.  Return a word/int pair that will serve as a usable reference (ie. 'steel 6')
        i = 1
        word = words[0] if first_or_second_word == 1 or len(words) <= 1 else words[1]

        # for obj in self.list:
        for list_name in sorted(list(set(str(x) for x in self.list))):
            if word in list_name.split(' '):
                if name == list_name:
                    return word if i == 1 else word + ' ' + str(i)
                else:
                    # i = i + len(self.inventory.dictionary[k].objs)
                    i = i + self.count(list_name)

        return None

    def get_2nd_word_reference(self, item_name):
        return self.get_reference(item_name, 2)

    def get_last_reference(self, item_name, first_or_second_word=1):
        # Often you want the most recent thing in the stack
        starting_point = self.get_reference(item_name, first_or_second_word)
        if starting_point is None:
            return None
        c = self.count(item_name)
        # magentaprint("RefList get_last_reference counted " + str(c))
        ref_split = starting_point.split(' ')
        if len(ref_split) > 1:
            return starting_point.split(' ')[0] + ' ' + str(int(ref_split[1]) + c - 1)
        else:
            if c <= 1:
                return starting_point.split(' ')[0]  # Had a buggy c as 0 case - and the served targets odd things with n=0
            else:
                return starting_point.split(' ')[0] + ' ' + str(c)
        # There would be less code if I didn't treat '1' specially (I prefer 'potion' not 'potion 1' for the 1st potion)

    def get_unique_references(self, exception_list=[]):
        references = []
        # magentaprint("RefList.get_unique_references() on: " + str(self.list))
        # magentaprint("RefList.get_unique_references() on len %s, list %s " % (str(len(self.list)), str(sorted(list(set(x.name for x in self.list))))))

        for name in sorted(list(set(str(x) for x in self.list))):
            if name not in exception_list:
                first_ref = self.get_reference(name)
                last_ref = self.get_last_reference(name)
                if first_ref is not None and last_ref is not None:
                    first_num = int(first_ref.split(' ')[1]) if len(first_ref.split(' ')) >= 2 else 1
                    # Nonetype has no attribute split
                    last_num = int(last_ref.split(' ')[1]) if len(last_ref.split(' ')) >= 2 else 1
                    word = first_ref.split(' ')[0]
                    for num in range(first_num, last_num + 1):
                        # magentaprint("RefList get_unique_references word: %s, num: %s" % (word, str(num)))
                        if num == 1:
                            references.append(word)
                        else:
                            references.append(word + ' ' + str(num))
                else:
                    magentaprint("RefList get_unique_refs error expecting %s in inventory." % name)

        # magentaprint("RefList get_unique_references returning: "  + str(references))

        return references

    def _reference_string(self, word, i):
        # Reference string given the int - this is just a code-saving method
        if i <= 1:
            return word
        else:
            return word + ' ' + str(i)

    def to_dict(self):
        d = {}
        for name in sorted(list(set(str(x) for x in self.list))):
            d[name] = self.count(name)
        return d

    # def __str__(self):
    #     return str(self.to_dict)

    # def extend(self, new_entries):
    #     # new_entries_sorted = sorted(new_entries)
    #     # for e in new_entries_sorted:
    #     self.list = sorted(self.list + new_entries)

    def __contains__(self, item):
        return item in self.list

    def append(self, new_entry):
        self.list = sorted(self.list + [new_entry])

    def reset(self):
        self.list = []

    def __iter__(self):
        return iter(self.list)
