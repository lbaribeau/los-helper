
from command.Command import Command
from comm import RegexStore as R
from misc_functions import magentaprint


# "### Balancedbarb just made a level!"
# "Congratulations, you made a level!"

class Train(Command):
    command = 'trai'
    success_regexes = [
        R.train_success # [r'Congratulations, you made a level\!']
    ]
    failure_regexes = [
        R.no_gold,
        R.not_enough_xp # [r"You need \d+ more experience\."]
    ]
    error_regexes = [
        R.not_training_location  # [r'This is not your training location\.']
    ]

    # def __init__(self, telnetHandler, inventory):
    #     self.inventory = inventory   
    #     super().__init__(telnetHandler)

    def notify(self, regex, match):
        self.result = regex
        magentaprint("Train object notify")
        # magentaprint("Repair(Command) notify(), _sent_target is: " +str(self._sent_target)+"... trying that on inventory.get or .remove_by_ref")
        # if self.success:
        #     self.inventory.get(self._sent_target).usable = True
        # if self.failure:
        #     self.inventory.remove_by_ref(self._sent_target)
        super().notify(regex, match)
        
