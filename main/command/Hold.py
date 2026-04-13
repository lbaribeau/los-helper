
from command.CommandThatRemovesFromInventory import CommandThatRemovesFromInventory
from comm import RegexStore as R
import itertools

class Hold(CommandThatRemovesFromInventory):
    """ CommandThatRemovesFromInventory gets us .execute(target), which will remove it from inventory
    Inventory already sees "You remove..." and adds things to itself, such as armour that was removed.
    We are also going to mainting the equipment dictionary ['holding'] here.
    That way LargeTorchManager can handle if something is being held."""
    command = 'hold'
    success_regexes = [
        R.you_hold
    ]
    failure_regexes = [
        # We have kind of a loose definition of failure and error here so it doesn't really matter
        # I guess try to put common scenarios together like
        # Ok I didn't know the weapon was broken, fair enough
        # Ok my targeting was way off 
        R.already_holding ,
        # R.doesnt_fit    , # Could something be too small or large like armour? Don't think so
        R.broken          , 
        R.class_prevents  ,
        R.not_yet           # You are not yet adept enough to use this!
    ]
    error_regexes = [
        R.you_cant_hold,
        R.dont_have,
        # Should we remove from inventory in this case??? I guess... 
        # R.in_combat,  # i believe you can hold in combat
        # or reset the entire inventory
    ]

    def __init__(self, telnetHandler, inventory, eq_command):
        super().__init__(telnetHandler, inventory)
        self.eq=eq_command

    def notify(self, regex, match):
        if regex in R.broken:
            item = self.inventory.get(self._sent_target)
            if item:
                item.usable = False
        # elif regex in R.no_room:
        #     # item = self.character.inventory.get(self._sent_target)
        #     # if item:
        #     #     item.name.split(' ')[1] == 'ring'
        #     if self.character.inventory.get(self._sent_target).name.split(' ')[1] == 'ring':
        #         self.ring_wearing_reaction.rings_worn = 8
        # Implement 'eq' maintenance
        # if regex in itertools.chain.from_iterable(self.success_regexes)
        if regex in itertools.chain.from_iterable(self.success_regexes):
            # Something like "You hold the large torch" I guess
            self.eq.dict['holding']=self.inventory.get_item_name_from_reference(self._sent_target) # ie. 'torch 2'
        super().notify(regex, match) # Removes it from inventory if success
        # Yeah there's kind of an issue where
        # We want to call super at the end to set wait flage
        # But it'd need to be called at the beginning to use self.success properly (set self.regex)
        # So when overwriting notify we can't inherit everything


    # @property
    # def no_room(self):
    #     return self.result in R.no_room

    # Ok on success we should be in good shape
    # Let's keep eq up to date I guess

