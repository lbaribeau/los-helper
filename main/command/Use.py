
from threading import Thread

from command.ThreadingMixin2 import ThreadingMixin2
from comm import RegexStore
from misc_functions import magentaprint

class Use(ThreadingMixin2):
    # Erhm, maybe I don't want a Potion thread because it will use too many pots if a prompt is delayed.
    # Solution - wait for prompt in the thread.
    command = 'use'
    cooldown_after_success = 0.81  # .80 too fast
    cooldown_after_failure = 0.81
    # It's tempting to try to make Inventory smart enough to use healing items...
    success_regexes = [RegexStore.potion_drank]  # Todo: add rods/buffs  (Might be made simpler with a different class, ie. UseRod)
    failure_regexes = []  # TODO: I believe flasks can fail
    error_regexes = [RegexStore.use_what, RegexStore.cant_use]

    def __init__(self, character, telnetHandler):
        self.character = character
        self.end_thread_regexes = self.error_regexes
        super().__init__(telnetHandler)
        self.prompt_flag = False
        self.regex_cart.append(RegexStore.prompt)
        self.prefer_big = False

    def notify(self, r, m):
        super().notify(r, m)
        if r in RegexStore.prompt:
            self.prompt_flag = True

    def healing_potion(self):
        # big_pots = ['large restorative', 'scarlet potion']
        # small_pots = ['chicken soup', 'small restorative', 'small flask', 'white potion']
        pots = ['chicken soup', 'small restorative', 'white potion', 'small flask', 'large restorative', 'scarlet potion']

        if self.prefer_big:
            pots.reverse()

        # # if 'bowl of chicken soup' in self.character.inventory.inventory:
        # if self.character.inventory.has('bowl of chicken soup'):
        #     self.character.inventory.use('bowl of chicken soup')
        #     # self.execute(self.character.inventory.)
        #     self.wait_for_flag()
        for pot in pots:
            # magentaprint("Use pot: " + str(pot))
            if self.character.inventory.has(pot):
                # self.character.inventory.use(pot)   # I want the 'result' feature of Command so I can't use Inventory here.
                # self.execute(self.character.inventory.)
                # self.character.inventory.remove_from_qty_dict(self.character.inventory.inventory, (pot, 1))
                # self.execute(self.character.inventory.get_reference(pot))
                # ref = self.character.inventory.get_2nd_word_reference(pot)
                # magentaprint('Use.healing_potion() ref: ' + str(ref))
                # if ref:  # not sure why 'has' or get ref is currently problematic... (error no target)
                #     self.execute(ref)
                #     # self.wait_for_flag()
                # else:
                #     continue
                # self.execute(pot)  # execute should definitely take a reference
                self.execute(self.character.inventory.get_reference(pot))
                # Inventory notices on its own 'a small restorative disintegrates'
                # self.wait_for_flag()  # Waiting to get the inventory upkeep right
                # if self.success or self.failure:
                #     self.character.inventory.remove(pot)
                # return True
                # break
                return True

        return False  # Ran out of pots.  use.result also provides return information

    # def can_heal(self):
    #     pots = ['chicken soup', 'small restorative', 'small flask', 'white potion', 'scarlet potion', 'large restorative']

    def run(self):
        while not self.stopping:
            magentaprint("Sending '" + str(self.command) + "' in " + str(round(self.wait_time())) + " seconds.")
            self.wait_until_ready()
            if not self.stopping:
                if self.healing_potion():
                    self.wait_loop('prompt_flag')
                else:
                    self.stop()
            self.wait_until_ready()

        # Make sure SmartCombat gets notified first so that it can stop us when the prompt comes in with HP above threshold
        # so potion_drank has to be after Prompt.
        # Erhm... that doesn't seem good enough, even though they'll likely come in the same chunk.
        # I feel like smart combat should do the stopping, because we don't want to worry about mob damage here.
        # We should wait_for_prompt() and be later in the subscriber list.

    def spam_pots(self, prefer_big=False):
        self.stopping = False
        self.prefer_big = prefer_big
        if not self.thread or not self.thread.is_alive():
            # not is_alive() means it won't look at stopping anymore so we're good.
            self.thread = Thread(target=self.run, args=())
            self.thread.daemon = True
            self.thread.start()
        # else:
        #     # Well the other thread CAN stil be sleeping from a kill error.  (ie misspelled target)
        #     # That puts it into a 3 second sleep, then the timer gets corrected 0.3s after.
        #     # So.... maybe it must poll fast... or we need signals... do we use that thread or a new thread??
        #     # Maybe we write its code smarter to handle this case... don't sleep till after the cooldown's verified
        #     magentaprint("Command will be sent in " + str(round(self.wait_time())) + " seconds.")

    def by_name(self, name):
        self.execute(self.character.inventory.get_reference(name))  # error checking...
