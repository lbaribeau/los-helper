
from command.Command import Command
from comm import RegexStore

class Use(Command):
    command = 'use'
    cooldown_after_success = 0.34
    cooldown_after_failure = 0.34
    # It's tempting to try to make Inventory smart enough to use healing items...
    success_regexes = [RegexStore.potion_drank]  # Todo: add rods/buffs  (Might be made simpler with a different class, ie. UseRod)
    failure_regexes = []  # TODO: I believe flasks can fail
    error_regexes = [RegexStore.use_what]

    def __init__(self, character, telnetHandler):
        super().__init__(telnetHandler)
        self.character = character

    def healing_potion(self):
        pots = ['chicken soup', 'small restorative', 'small flask', 'white potion', 'large restorative', 'scarlet potion']
        # # if 'bowl of chicken soup' in self.character.inventory.inventory:
        # if self.character.inventory.has('bowl of chicken soup'):
        #     self.character.inventory.use('bowl of chicken soup')
        #     # self.execute(self.character.inventory.)
        #     self.wait_for_flag()
        for pot in pots:
            if self.character.inventory.has(pot):
                # self.character.inventory.use(pot)   # I want the 'result' feature of Command so I can't use Inventory here.
                # self.execute(self.character.inventory.)
                # self.character.inventory.remove_from_qty_dict(self.character.inventory.inventory, (pot, 1))
                self.execute(self.character.inventory.get_reference(pot))
                # Inventory notices on its own 'a small restorative disintegrates'
                # self.wait_for_flag()  # Waiting to get the inventory upkeep right
                # if self.success or self.failure:
                #     self.character.inventory.remove(pot)
                # return True
                break

        return False  # Ran out of pots.  use.result also provides return information



