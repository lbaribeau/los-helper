
import re
import collections

from misc_functions import magentaprint
from fake.FakeItem import FakeItem

class FakeInventory(object):
    def __init__(self, l):
        self.l = sorted(FakeItem(s) for s in l)

        magentaprint("Fake inventory list: " + str(self.l))
        self.numbers = [
            'a', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
            'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'
        ] + [str(n) for n in range(20, 200)]

    def output_string(self):
        if len(self.l) <= 0:
            return "You currently have no carried inventory.\n\r"
        else:
            # return "You have: " + ", ".join([self.mini_inventory_string(i) for i in self.inventory]) + '.'
            return "You have: " + self.item_string() + '.\n\r'

    def item_string(self):
        output = ''

        for i in sorted(set(self.l)):  # set returns only unique values - so I get one iteration per item name
            count = self.l.count(i)
            if count == 1:
                if re.match(r'^[aeiou]', i.name):
                    output += 'an ' + i.name
                elif i.name == 'title deeds' or i.name == 'chicken soup' or i.name == 'bolos' or 'l armour' in i.name:
                    output += 'some ' + i.name
                else:
                    output += 'a ' + i.name
            else:
                if i.name == 'title deeds' or i.name == 'chicken soup' or i.name == 'bolos' or 'l armour' in i.name:
                    output += self.numbers[count-1] + 'sets of ' + i.name
                elif i.name.endswith('fe'):
                    output += self.numbers[count-1] + ' ' + i.name[:len(i.name)-2] + 'ves'
                elif i.name.endswith('h') or i.name.endswith('j') or i.name.endswith('s') or i.name.endswith('u') or i.name.endswith('x'):
                    output += self.numbers[count-1] + ' ' + i.name + 'es'
                # elif i.name.endswith('y'):  # Unfortunately the server prefers "red berrys"
                else:
                    output += self.numbers[count-1] + ' ' + i.name + 's'
            output += ', '

        return output[:len(output)-2]

    def remove(self, ref):
        # if item in self.l:
        #     self.l.remove(item)
        self.remove_by_index(self.index(ref))

    def remove_by_index(self, i):
        self.l.pop(i)

    def add(self, item):
        if isinstance(item, str):
            item = FakeItem(item)

        for i in range(0, len(self.l)):
            if self.l[i] > item:
                self.l.insert(i, item)
                return

        self.l.append(item)
        # self.l.append(FakeItem(item))
        # self.l.sort()  # We want to keep broken items sorted properly by inserting manually

    def add_broken(self, item):
        if isinstance(item, str):
            item = FakeItem(item)

        item.usable = False
        self.add(item)

    def index(self, ref):
        if len(ref.split()) >= 2:
            refw, n = ref.split()[0], int(ref.split()[1])
        else:
            refw, n = ref, 1

        # magentaprint("FakeInventory n: " + str(n))

        for i in sorted(list(set(self.l))):
            # magentaprint("FakeInventory i, l.count(i): %s, %s" % (str(i), str(self.l.count(i))))
            if any(w.startswith(refw) for w in i.name.split()):
                if n <= self.l.count(i):
                    return self.l.index(i) + n - 1
                else:
                    n = n - self.l.count(i)

    def get(self, ref):
        i = self.index(ref)

        if i is not None:
            return self.l[i]

    def set_usable(self, ref, val=True):
        self.get(ref).usable = val

    def unset_usable(self, ref):
        self.get(ref).usable = False

    def has(self, item_string):
        for i in self.l:
            if i.name == item_string:
                return True

        return False

    def remove_all(self, name):
        self.l = [x for x in self.l if x.name != name]

    def add_many(self, name, qty):
        for i in range(0,qty):
            self.add(name)
            # ... the easy way

    def count(self, item_string):
        return self.l.count(item_string)
