
from comm import RegexStore as R
from misc_functions import magentaprint

class RingWearingReaction(object):
    def __init__(self, inventory, command_handler):
        self.inventory = inventory
        self.command_handler = command_handler
        # self.regexes = R.get_ring
        # self.regex_cart =  [R.get_ring]
        # self.regexes = [r"(?s)You get [\da-zA-Z]+?an? .+? ring((,.+?\.)|(\.))"]
        # self.regexes = [r"You get a copper ring\."]
        self.regexes = R.get_ring

    def notify(self, regex, match):
        magentaprint("RingWearingReaction notify.")
        self.command_handler.process('wear ' + self.inventory.first_usable_ring_ref())
