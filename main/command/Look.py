
from command.Command import Command
from comm import RegexStore as R
from misc_functions import magentaprint

class Look(Command):
    command = 'l'
    # durability = 0  # 0 for broken, >0 for not broken
    # success_regexes = [R.broken, R.terrible_condition, R.bad_condition, R.poor_condition, 
    #     R.fair_condition, R.fine_condition, R.good_condition, R.excellent_condition, R.pristine_condition]
    success_regexes = [
        R.broken,
        R.unusable,
        R.condition
    ]
    failure_regexes = [
    ]
    error_regexes = [
        R.not_here
    ]

    @property
    def broken(self):
        return self.result in R.broken or self.result in R.unusable

    # @property
    # def durability(self):
    #     return 0 if result in R.broken else 1 if result in R.terrible_condition else 2 if result in R.bad_condition else 3 if result in R.poor_condition else 4 if result in R.fair_condition else 5 if result in R.fine_condition else 6 if result in R.good_condition else 7 if result in R.excellent_condition else 8 if result in R.pristine_condidtion else None

    def notify(self, r, m):
        # So this is getting called too often... (check executing)
        item = self.inventory.get(self._sent_target)
        if self._executing and item:
            # magentaprint("Look notify")
            if r in R.condition:
                self.condition = m.group(1)
                if not item.usable:
                    magentaprint("Look noticed usable was wrong!") # (Could raise an exception here to track juicy bugs))
                    self.inventory.set_usable(self._sent_target)
            elif r in R.broken or r in R.unusable:
                if item.usable:
                    magentaprint("Look noticed usable was wrong!")
                    self.inventory.set_broken(self._sent_target)

        # So how do we know that we aren't looking at the held weapon or armour
        # Equipment gets looked at if not in inventory
        super().notify(r,m)

    def execute(self, target=None):
        self.condition = ''
        super().execute(target)

    def __init__(self, inventory, telnetHandler):
        self.inventory = inventory
        super().__init__(telnetHandler)
