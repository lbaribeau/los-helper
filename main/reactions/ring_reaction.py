
from comm import RegexStore as R
from misc_functions import magentaprint

class RingWearingReaction(object):
    # def __init__(self, inventory, command_handler):
    def __init__(self, wear, inventory):
        self.inventory = inventory
        # self.command_handler = command_handler
        # # self.regexes = R.get_ring
        # # self.regex_cart =  [R.get_ring]
        # # self.regexes = [r"(?s)You get [\da-zA-Z]+?an? .+? ring((,.+?\.)|(\.))"]
        # # self.regexes = [r"You get a copper ring\."]
        # self.regexes = R.get_ring + R.armour_break + R.end_combat
        self.regexes = R.you_get + R.armour_breaks + R.ze_mob_died
        self.wear = wear
        # self.broken_ring
        # self.full_rings = False
        self.rings_worn = 0

    def notify(self, regex, match):
        magentaprint("RingWearingReaction notify {0}".format(match.re.pattern))
        # self.command_handler.process('wear ' + self.inventory.first_usable_ring_ref())
        # This doesn't mark broken rings though... and for some reason it gets notified many times.
        # if regex in R.get_ring:
        # Do we know if inventory has been notified yet?
        if regex in R.you_get + R.ze_mob_died and self.rings_worn < 8:
            self.try_wearing_rings()
            # self.wear.execute('all')
        elif regex in R.armour_breaks:
            if len(match.group(1).split(' ')) >= 2:
                if match.group(1).split(' ')[1] == 'ring':
                    # self.broke_ring = True # This is because we can't wear in combat
                    # self.try_wearing_a_ring()
                    # self.full_rings = False
                    self.rings_worn = self.rings_worn - 1
                    magentaprint("RingWearingReaction noticed " + match.group(1) + '.')

    def try_wearing_rings(self):
        ring = self.inventory.first_usable_ring_ref()
        # while ring and self.rings_worn < 8:
        if ring and self.rings_worn < 8:
            # self.wear.execute_and_wait(ring) # Sometimes ya gotta wait for that server text
            self.wear.execute(ring) # I don't think waiting works
            # Eh this barely works - what if we get two or three rings
            # self.wear.execute('all')
            # if self.wear.success:
            #     self.rings_worn = self.rings_worn + 1
            # elif self.wear.result in R.no_room:
            #     self.rings_worn = 8
            # ring = self.inventory.first_usable_ring_ref()

    # def try_wearing_a_ring(self):
    #     # We call this from notify, so don't use execute_and_wait
    #     # Keep notify fast if possible
    #     ref = self.inventory.first_usable_ring_ref()
    #     if ref:
    #         self.wear.execute(ref)
    #     # This won't work in combat!
    #     # That's why SmartCombat doesn't this
    #     # We could do it here though by matching end combat
