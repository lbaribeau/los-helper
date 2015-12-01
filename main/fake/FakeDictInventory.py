
import re

class FakeDictInventory(object):
    # Problem with dict: all items of the same name are lumped together so you can have individual data for each
    def __init__(self, d):
        self.d = d
        self.numbers = ['two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen']
    
    def output_string(self):
        if len(self.d.keys()) <= 0:
            return "You currently have no carried inventory."
        else:
            # return "You have: " + ", ".join([self.mini_inventory_string(i) for i in self.inventory]) + '.'
            return "You have: " + self.dict_string() + '.\n\r'

    def dict_string(self):
        s = ''
        for k in sorted(self.d.keys()):
            if self.d[k] == 1:
                if re.match(r'^[aeiou]', k):
                    s += 'an ' + k
                elif k == 'title deeds':
                    s += 'some ' + k
                else:
                    s += 'a ' + k
            else:
                if k == 'title deeds' or k == 'chicken soup' or k == 'bolos' or 'l armour' in k:
                    s += self.numbers[self.d[k]-2] + ' sets of ' + k
                elif k.endswith('fe'):
                    s += self.numbers[self.d[k]-2] + ' ' + k[:len(k)-2] + 'ves'
                elif k.endswith('h') or k.endswith('j') or k.endswith('s') or k.endswith('u') or k.endswith('x'):
                    s += self.numbers[self.d[k]-2] + ' ' + k + 'es'
                # elif k.endswith('y'):  # Unfortunately the server prefers "red berrys"
                else:
                    s += self.numbers[self.d[k]-2] + ' ' + k + 's'
            s += ', '
        return s[:len(s)-2]

    def remove(self, item):
        if item in self.d.keys():
            if self.d[item] > 1:
                self.d[item] = self.d[item] - 1
            else:
                del self.d[item]

    def add(self, item):
        if item in self.d.keys():
            self.d[item] = self.d[item] + 1
        else:
            self.d[item] = 1
