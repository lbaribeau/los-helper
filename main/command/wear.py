
from command.CommandThatRemovesFromInventory import CommandThatRemovesFromInventory
from comm import RegexStore as R

class Wear(CommandThatRemovesFromInventory):
    command = 'wear'
    success_regexes = [
        R.you_wear
    ]
    failure_regexes = [
        R.broken, 
        R.doesnt_fit, 
        R.no_room, 
        R.class_prevents,
        R.not_yet
    ]
    error_regexes = [
        R.wear_what, 
        R.in_combat, 
        R.dont_have # Should we remove from inventory in this case??? I guess... 
        # or reset the entire inventory
        # Right now I'm just going to hope that dont_have doesn't happen
        # It's only for the bot that we would remove from inventory
    ]

    # def __init__(self, telnetHandler, inventory, ring_wearing_reaction):
    #     super().__init__(telnetHandler, inventory)
    #     self.ring_wearing_reaction = ring_wearing_reaction

    # def __init__(self, telnetHandler, inventory, equipment_command):
    #     super().__init__(telnetHandler, inventory)
    #     self.eq = equipment_command

    def notify(self, r, m):
        # if r in R.you_wear:
        #     self.eq # Ohhhh sh&$#*$&# not so easy to know the slot!
        if r in R.broken:
            item = self.inventory.get(self._sent_target)
            if item:
                item.usable = False
        # elif r in R.no_room:
        #     # item = self.character.inventory.get(self._sent_target)
        #     # if item:
        #     #     item.name.split(' ')[1] == 'ring'
        #     if self.character.inventory.get(self._sent_target).name.split(' ')[1] == 'ring':
        #         self.ring_wearing_reaction.rings_worn = 8
        super().notify(r, m)

    @property
    def no_room(self):
        return self.result in R.no_room

    # I think "wear" (command) should update equipment...  yeah... so call that not implemented yet
    # I guess the bot doesn't really keep track, it just calls 'eq' when it wants to know, like a full re-init instead of maintaining

