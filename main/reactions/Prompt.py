
from comm import RegexStore as R
from misc_functions import magentaprint
from datetime import datetime

class Prompt(object):
    def __init__(self):
        self.regex_cart = [R.prompt]
        self.hp = 100
        self.mp = 100
        self.prev_hp = 100
        self.prev_mp = 100
        self.tick_timelog = [datetime.now()]
        
    def notify(self, regex, match):
        # Maybe we want hp/mp deltas clumped (prev_hp == hp on black magic cast...)
        #magentaprint("Prompt notify got HP:{0} and MP:{1}".format(match.group(1), match.group(2)))
        #if int(match.group(1)) != self.hp or int(match.group(2)) != self.mp:

        self.prev_hp = self.hp
        self.prev_mp = self.mp
        self.hp = int(match.group(1))
        self.mp = int(match.group(2))

        #if self.prev_hp != self.hp or self.prev_mp != self.mp:
            #magentaprint("Prompt changed HP to {0} from {1}, MP to {2} from {3}.".format(self.hp, self.prev_hp, self.mp, self.prev_mp))
        if self.hp_delta() or self.mp_delta():
            if len(self.tick_timelog) < 300:
                self.tick_timelog.append(datetime.now())
            magentaprint("Prompt delta: [{0}, {1}], time: {2}".format(self.hp_delta(), self.mp_delta(), self.tick_timelog[-1]-self.tick_timelog[-2]))

        # self.prev_hp = self.hp if int(match.group(1)) != self.hp else self.prev_hp
        # self.prev_mp = self.mp if int(match.group(2)) != self.mp else self.prev_mp
        # self.hp = int(match.group(1))
        # self.mp = int(match.group(2))

    def hp_delta(self):
        return self.hp - self.prev_hp
        
    def mp_delta(self):
        return self.mp - self.prev_mp
