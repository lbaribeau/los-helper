
import itertools

import RegexStore
# from misc_functions import magentaprint

class MudEvent(object):
    def __init__(self, regexes):
        self.regexes = regexes
        self.subscribers = []
        # for r in regexes:
        #     magentaprint("MudEvent regex " + str(r))






