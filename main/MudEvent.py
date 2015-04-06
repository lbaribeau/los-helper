
import itertools

import RegexStore
from misc_functions import magentaprint

# magentaprint("MudEvent: RegexStore: " + str(dir(RegexStore)))

class MudEvent(object):
    def __init__(self, regexes):
        self.regexes = regexes
        self.subscribers = []

# magentaprint("MudEvent: Chained RegexStore: " + itertools.chain(dir(RegexStore)))






