
from reactions.BotReactions import BotReactionWithFlag
import comm.RegexStore as R
from misc_functions import magentaprint

singles = ['a ', 'an ', 'some ', 'The ']
numbers = ['two ', 'three ', 'four ', 'five ', 'six ', 'seven ', 
    'eight ', 'nine ', 'ten ', 'eleven ', 'twelve ', 'thirteen ', 'fourteen ', 
    'fifteen ' , 'sixteen ', 'seventeen ', 'eighteen ', 'nineteen ', 'twenty ']
numbers.extend([str(i) + " " for i in range(21, 200)])
  
def remove_plural(m):
    # if mob_string.endswith('s'):
    #     mob_string = mob_string[0:len(mob_string)-1]
    # elif mob_string.endswith('ses'):
    #     mob_string = mob_string[0:len(mob_string)-3]
    # m = mob_string

    # if capitals:
    #     singles = [s.title() for s in singles]
    #     numbers = [n.title() for n in numbers]
    # else:
    #     singles = [s.lower() for s in singles[0:2]]
    #     singles.append('The ')
    #     numbers = [n.lower() for n in numbers]

    # if any([m.startswith(s) for s in singles]):
    #     # m_dict[m.partition(' ')[2]] = 1
    #     return m.partition(' ')[2]
    # number_check = [m.startswith(n) for n in numbers]
    if m.endswith('sses'):
        return m[0:len(m)-2]
    elif m.endswith('s'):
        return m[0:len(m)-1]
    elif m.endswith('children'):
        return m[0:len(m)-3]
    elif m.endswith(' mice'):
        return m[0:len(m)-4] + 'mouse'
    else:
        return m

        # for n in range(0, len(numbers)):
        #     if m.startswith(numbers[n]):
        #         # m_dict[m.partition(' ')[2]] = n + 2
        #         m_list.extend([m.partition(' ')[2]] * (n + 2))

class Mobs(BotReactionWithFlag):
    # I will give this object MONSTER_LIST because that provides a place for possible extended functionality 
    # in the future, such as correcting targets.

    # The main reason for this object is too further clean up MudReaderThread, which is ALMOST readable/maintainable now. 
    regex_cart = [
        R.mob_arrived, R.mob_died, R.mob_fled, R.mob_defeated, R.mob_wandered, R.mob_left, 
        R.mob_joined1, R.mob_joined2, R.mob_attacked, R.you_attack, R.mob_aggro
    ]

    def __init__(self):
        self.list = []
        self.attacking = []
        self.singles = ['a', 'an', 'the']
        self.numbers = ['two', 'three', 'four', 'five', 'six', 'seven', 
                        'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 
                        'fifteen' , 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty']
        self.numbers.extend([str(i) + " " for i in range(21, 200)])

    def read_match(self, m):
        if m.group('mob1'):
            return m.group('mob1').strip()
        elif m.group('mob2'):
            magentaprint("Mobs mob2")
            if m.group('mob2').startswith('The '):
                return m.group('mob2').partition(' ')[2].strip()
            else:
                return m.group('mob2').strip()
        elif m.group('mob3'):
            magentaprint("Mobs mob3")
            return m.group('mob3').strip()

    def notify(self, r, m_obj):
        # We'll let Cartography handle the initialization of monster_list with the area regex since it already does a great job.
        if r in R.mob_arrived:
            # article = m_obj.group('N').lower() if m_obj.group('N') else None
            # magentaprint("Mob arrived " + m_obj.group('mobs'))
            # magentaprint("Mobs " + m_obj.group('N') + ' ' + m_obj.group('mobs') + " just arrived.")
            mob_parse = m_obj.group('mobs').partition(' ')
            first_word = mob_parse[0].lower()
            if first_word in self.singles:
                # self.list.append(' '.join(mob_parse m_obj.group('mob'))
                self.list.append(mob_parse[2])
            elif first_word in self.numbers:
                magentaprint("Mobs mobs: " + m_obj.group('mobs') + ", first_word: " + first_word)
                # self.list.extend([remove_plural(m_obj.group('mobs'))] * (int(self.numbers.index(first_word)) + 2))
                self.list.extend([remove_plural(mob_parse[2])] * (int(self.numbers.index(first_word)) + 2))
            else:
                # Named mob
                magentaprint("Mobs arrived no article: first_word " + first_word + " mobs: " + str(m_obj.group('mobs')))
                # self.list.append(m_obj.group('mobs'))
                self.list.append(mob_parse[0])
            # if article in self.singles:
            #     self.list.append(m_obj.group('mob'))
            # elif article in self.numbers:
            #     magentaprint("Mobs mobs: " + m_obj.group('mob') + ", article: " + m_obj.group('N'))
            #     self.list.extend([remove_plural(m_obj.group('mob'))] * (int(self.numbers.index(m_obj.group('N'))) + 2))

            #     # if ',' not in m_obj.group('mob'):
            #     #     # Doesn't handle commas or The
            #     #     # self.list.extend([remove_plural(m_obj.group('mob'), capitals=True)] * (int(self.numbers.index(m_obj.group('N'))) + 2))
            #     #     magentaprint("Mobs mobs " + m_obj.group('mob') + ", N " + m_obj.group('N'))
            #     #     self.list.extend([remove_plural(m_obj.group('mob'))] * (int(self.numbers.index(m_obj.group('N'))) + 2))
            #     # else:
            #     #     magentaprint("Mobs mobs " + m_obj.group('mob'))
            #     #     self.list.extend(self.parse_mob_string(m_obj.group('mob')))
            #     # # qty = self.numbers.index(m_obj.group('N')) + 2
            # else:
            #     # Named mob
            #     magentaprint("Mobs arrived no article: N " + str(m_obj.group('N')) + " mobs: " + str(m_obj.group('mob')))
            #     self.list.append(m_obj.group('mob'))
        elif r in R.mob_died:
            # if m_obj.group('mob') in self.list:
            #     self.list.remove(m_obj.group('mob'))
            # if m_obj.group('mob') in self.attacking:
            #     self.attacking.remove(m_obj.group('mob'))
            if self.read_match(m_obj) in self.list:
                self.list.remove(self.read_match(m_obj))
            if self.read_match(m_obj) in self.attacking:
                self.attacking.remove(self.read_match(m_obj))
        elif r in R.mob_fled:  # Leave mobs.attacking populated. (?)  might help to chase mobs that don't block you (chase currently relies on that.)
            # if m_obj.group('mob') in self.list:
            #     self.list.remove(m_obj.group('mob'))
            if self.read_match(m_obj) in self.list:
                self.list.remove(self.read_match(m_obj))
        # elif (r in R.mob_wandered or r in R.mob_left) and m_obj.group('mob') in self.list:
        #     magentaprint("Mobs: " + str(m_obj.group(0)))
        #     self.list.remove(m_obj.group('mob'))
        elif (r in R.mob_wandered or r in R.mob_left) and self.read_match(m_obj) in self.list:
            self.list.remove(self.read_match(m_obj))
        elif r in R.mob_joined1 or r in R.mob_joined2:
            # self.attacking.append(m_obj.group('mob'))
            self.attacking.append(self.read_match(m_obj))
        elif r in R.mob_attacked:
            # c = self.attacking.count(m_obj.group('mob').strip())
            # if c == 0:
            #     self.attacking.append(m_obj.group('mob'))
            # # Commenting incorrect code
            # # else:
            # #     if m_obj.group('nth'):
            # #         nth = int(m_obj.group('nth')[0:len(m_obj.group('nth'))-2])
            # #         self.attacking.extend([m_obj.group('mob')] * max(nth - c, 0))
            c = self.attacking.count(self.read_match(m_obj))
            if c == 0:
                self.attacking.append(self.read_match(m_obj))
        # elif r in R.you_attack or r in R.mob_aggro:
        #     magentaprint('Mob engaged ' + str(m_obj.group('mob')))
        #     self.attacking.append(m_obj.group('mob'))
        elif r in R.you_attack:
            # self.attacking.append(m_obj.group('mob'))
            self.attacking.append(self.read_match(m_obj))
        elif r in R.mob_aggro:
            self.attacking.append(self.read_match(m_obj))
        magentaprint("mobs.list " + str(self.list))
        magentaprint("mobs.attacking " + str(self.attacking))
        super().notify(r, m_obj)

    def parse_mob_string(self, s):
        # You see (two kobold children, a dustman).
        # (Two lay followers) just arrived.
        s = s.replace("\n\r", ' ')
        comma_items = [comma_item.strip().lower() for comma_item in s.split(',')]

        # return [Mobs.remove_plural(m.strip()) for m in mob_match.group(1).split(',')]
        m_list = []
        for c in comma_items:
            if any([c.startswith(s + ' ') for s in self.singles]):
                # m_dict[m.partition(' ')[2]] = 1
                m_list.extend([c.partition(' ')[2]])
                continue
            # number_check = [m.startswith(n) for n in numbers]

            if any(c.startswith(n + ' ') for n in self.numbers):
                m_list.extend([remove_plural(c.partition(' ')[2])] * (self.numbers.index(c.split(' ')[0]) + 2))
            else:
                m_list.append(c)

            # for n in range(0, len(numbers)):
            #     if c.startswith(numbers[n] + ' '):
            #         # m_dict[m.partition(' ')[2]] = n + 2
            #         c_singular = remove_plural(c)
            #         m_list.extend([c_singular.partition(' ')[2]] * (n + 2))
            #         break





        # return list(m_dict.keys())
        return m_list 



