
# import statistics as stats  # python 3.4
import math

from reactions.BotReactions import BotReactionWithFlag
import comm.RegexStore as R
from misc_functions import magentaprint
from reactions.referencing_list import ReferencingList

class Mobs(BotReactionWithFlag):
# class Mobs(BotReactionWithFlag, ReferencingList):
    # I will give this object MONSTER_LIST because that provides a place for possible extended functionality
    # in the future, such as correcting targets. (Ok we wrote MobTargetDeterminator)

    # The main reason for this object is too further clean up MudReaderThread, which is ALMOST readable/maintainable now.
    # Cartography initializes this upon entry of a new area
    regex_cart = [
        R.mob_arrived, R.mob_died,    R.mob_fled,     R.mob_defeated, R.mob_wandered, R.mob_left,
        R.mob_joined1, R.mob_joined2, R.mob_attacked, R.you_attack,   R.mob_aggro
    ]

    def __init__(self):
        super().__init__() # threading.Event
        self.list = ReferencingList([])
        self.attacking = []
        self.singles = ['a', 'an', 'the']
        self.numbers = [
            'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 
            'thirteen', 'fourteen', 'fifteen' , 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty'
        ]
        self.numbers.extend([str(i) + " " for i in range(21, 200)])
        self.damage = []
        self.chase = ''
        self.chase_exit = ''

    def read_match(self, m):
        if m.group('mob1'):
            return m.group('mob1').strip()
        elif m.group('mob2'):
            # magentaprint("Mobs mob2")
            if m.group('mob2').startswith('The '):
                return m.group('mob2').partition(' ')[2].strip()
            else:
                return m.group('mob2').strip()
        elif m.group('mob3'):
            # magentaprint("Mobs mob3")
            return m.group('mob3').strip()

    def read_mobs(self, arrived_mobs):
        mob_parse  = arrived_mobs.partition(' ')
        first_word = mob_parse[0]

        if first_word.lower() in self.singles:
            # Note that lower() doesn't modify first_word; it just returns the lowered string.
            # We'll keep the case on first word so Jerrek gets added to the monster list with capitol J so he matches the monster lists
            return [mob_parse[2]]
        elif first_word.lower() in self.numbers:
            #magentaprint("Mobs mobs: " + arrived_mobs + ", first_word: " + first_word)
            return [remove_plural(mob_parse[2])] * (int(self.numbers.index(first_word.lower())) + 2)
        else:
            # Named mob
            magentaprint("Mobs arrived no article: first_word " + first_word + " mobs: " + arrived_mobs)
            # self.list.append(mob_parse[0])
            return [mob_parse[0]]

    def notify(self, r, m_obj):
        # We'll let Cartography handle the initialization of monster_list with the area regex since it already does a great job.
        #magentaprint("mobs.list " + str(self.list) + "; notification from regex: " + str(r[0:min(10, len(r))]))
        if r in R.mob_arrived:
            self.list.add_from_list(self.read_mobs(m_obj.group('mobs')))
        elif r in R.mob_died:
            magentaprint("Mobs noticed " + str(self.read_match(m_obj)) + " died, it's in the self.list: " + str(self.read_match(m_obj) in self.list))
            if self.read_match(m_obj) in self.list:
                self.list.remove(self.read_match(m_obj))
            magentaprint("Mobs removed it from the list, now is it in attacking: {0}".format(self.read_match(m_obj) in self.attacking))
            if self.read_match(m_obj) in self.attacking:
                self.attacking.remove(self.read_match(m_obj))  
                # TODO: if a mob is one-shot, it's not removed because the You attacked notify is after
            magentaprint('Mobs damage ' + str(self.damage) + ', s=' + str(sum(self.damage)) + ', m=' + str(round(self.mean(self.damage), 1)) + ', stdev=' + str(round(self.stdev(self.damage), 1)) + ', h=' + str(round(1 - sum([x == 0 for x in self.damage])/max(len(self.damage),1), 2)))
            # m = sum(self.damage) / max(len(self.damage), 1)
            # s = sum(self.damage - [m]*len(self.damage))
            # magentaprint('Mobs damage ' + str(self.damage) + ', s=' + str(sum(self.damage)) + ', m=' + str(stats.mean(self.damage)) + ', stdev=' + str(stats.stdev(self.damage)) + ', h=' + str(round(1 - sum([x == 0 for x in self.damage])/len(self.damage), 2)))
        elif r in R.mob_fled:  # Leave mobs.attacking populated. (?)  might help to chase mobs that don't block you (chase currently relies on that.)
            if self.read_match(m_obj) in self.list:
                self.list.remove(self.read_match(m_obj))
            self.chase = self.read_match(m_obj)
            self.chase_exit = m_obj.group('exit')
        elif (r in R.mob_wandered or r in R.mob_left) and self.read_match(m_obj) in self.list:
            self.list.remove(self.read_match(m_obj))
        elif r in R.mob_joined1 or r in R.mob_joined2:
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
            #c = self.attacking.count(self.read_match(m_obj))
            if self.attacking.count(self.read_match(m_obj)) == 0:
                self.attacking.append(self.read_match(m_obj))
            # TODO: remember if 1st and 2nd mobs are attacking and ensure attacking has length 2 if necessary
            if 'd' in m_obj.groupdict().keys():
                self.damage.append(int(m_obj.group('d')))
            else:
                self.damage.append(0)
        if r in R.you_attack or r in R.mob_aggro:
            self.damage = []

            self.attacking.append(self.read_match(m_obj))
        if self.attacking:
            magentaprint("mobs.attacking " + str(self.attacking))
        super().notify(r, m_obj)

    def parse_mob_string(self, s):
        # You see (two kobold children, a dustman).
        # (Two lay followers) just arrived.
        s = s.replace("\n\r", ' ')
        # comma_items = [comma_item.strip().lower() for comma_item in s.split(',')]

        # return [Mobs.remove_plural(m.strip()) for m in mob_match.group(1).split(',')]
        m_list = []
        # for c in comma_items:
        for comma_item in s.split(','):
            # Make sure to keep capitols in names, but don't miss any comparisons because of capitols at the beginnings of sentences
            M = comma_item.strip()
            m = M.lower()

            #if m[len(m)-4:len(m)-2] == ' (' and m[len(m)-1] == ')':
            if m[-4:-2] == ' (' and m[-1] == ')':
                # m = remove_good_evil(m)
                magentaprint("Mobs.parse_mob_string reduced {0} to {1}".format(M,M[:-4]))
                m = m[:-4]
                M = M[:-4]
            # It seems like this part gets done elsewhere
            # It turns Cheryn into Ch and Olmer into O somewhere

            if any(m.startswith(single + ' ') for single in self.singles):
                # m_dict[m.partition(' ')[2]] = 1
                m_list.extend([M.partition(' ')[2]])
                # number_check = [m.startswith(n) for n in numbers]
            elif any(m.startswith(n + ' ') for n in self.numbers):
                m_list.extend([remove_plural(M.partition(' ')[2])] * (self.numbers.index(M.split(' ')[0]) + 2))
            else:
                magentaprint("Mobs.parse_mob_string appending " + M)
                m_list.append(M)

            # for n in range(0, len(numbers)):
            #     if c.startswith(numbers[n] + ' '):
            #         # m_dict[m.partition(' ')[2]] = n + 2
            #         c_singular = remove_plural(c)
            #         m_list.extend([c_singular.partition(' ')[2]] * (n + 2))
            #         break

        # return list(m_dict.keys())
        return m_list

    def get_reference_from_mob_match_object(self, match_object):
        return self.get_reference(self.read_match(match_object))

    def get_reference(self, target):
        return self.list.get_reference(target)

    # Todo: Why are these part Mobs? Shouldn'they be misc functions?
    def mean(self, a):
        return sum(a)/max(len(a),1)

    def stdev(self, a):
        # stdev excluding zeroes
        m = self.mean(a)
        l = len(a) - sum([x==0 for x in a])
        # return math.sqrt(1/len(a) * sum([(x-m)^2 for x in a]))
        return math.sqrt(1/max(l,1) * sum([pow((x-m),2) for x in a]))

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

def remove_good_evil(m):
    if m.lower().endswith(' (g)') or m.lower().endswith(' (e)'):
        return m[0:len(m)-5]
