
import threading

from command.ThreadingMixin2 import ThreadingMixin2
from comm import RegexStore as R
from misc_functions import magentaprint

class Consume(threading.Event):
    # This is a merger for use, eat, drink and does things like waiting for those commands to return (success or fail) and implements a cooldown
    # Let's have this one support wait for the prompt
    # That actually seems like a great way to wait for a command in general
    # healing_potion() is like execute
    # We might not need everything from Command... maybe just threading.Event...

    # Let's inherit Command so we can implement notify on the prompt and we can wait() for the prompt
    # healing_potion is like execute
    # It'll use use, drink, or eat

    # def __init__(self, use, drink, eat):
    def __init__(self, use, drink, eat):
        super().__init__() # threading.Event
        self.use = use
        self.drink = drink
        self.eat = eat

        self.inventory = self.use.inventory
        self.prefer_big = False
        self.use_golden = False
        self.regex_cart = R.prompt # So we can wait() for prompt
        # self.prompt_flag = False

    # def notify(self, r, m):
    #     # if r in R.prompt:
    #     self.prompt_flag = True # I'm not sure we even use this... this object only gets notified on prompt now
    #     super().notify(r, m) # threading.Event

    # def execute(self, target):
    #     item = self.inventory.get(target)
    #     if item in ['chicken soup', 'white potion', 'scarlet potion','golden potion','small restorative','large restorative']:
    #         self.command='use'
    #     elif item in ['philtre of health']:
    #         self.command='drin'
    #     elif item in ['tree root']:
    #         self.command='eat'
        # Do we really want to do it this way... no... use the command objects that have the right regexes on them

    def granite_potion(self):
        if self.inventory.has('crystal vial'):
            self.drink.execute(self.inventory.get_reference('crystal vial'))
            return True
        elif self.inventory.has('granite potion'):
            self.drink.execute(self.inventory.get_reference('granite potion'))
            return True
        return False

    def healing_potion(self):
        # big_pots = ['large restorative', 'scarlet potion']
        # small_pots = ['chicken soup', 'small restorative', 'small flask', 'white potion']
        pots = [
            'chicken soup', 
            'small restorative', 
            'white potion', 
            'small flask', 
            'philtre of health',
            'scarlet potion',
            'large restorative', 
            'tree root'
        ] # 'golden potion' (leave that manual)

        if self.use_golden:
            pots.append('golden potion')

        if self.prefer_big:
            # I think self.prefer_big needs to be an argument to healing_potion()
            pots.reverse()

        # # if 'bowl of chicken soup' in self.inventory:
        # if self.inventory.has('bowl of chicken soup'):
        #     self.inventory.use('bowl of chicken soup')
        #     # self.execute(self.inventory.)
        #     self.wait_for_flag()
        for pot in pots:
            # magentaprint("Use pot: " + str(pot))
            if self.inventory.has(pot):
                # self.inventory.use(pot)   # I want the 'result' feature of Command so I can't use Inventory here.
                # self.execute(self.inventory.)
                # self.inventory.remove_from_qty_dict(self.inventory.inventory, (pot, 1))
                # self.execute(self.inventory.get_reference(pot))
                # ref = self.inventory.get_2nd_word_reference(pot)
                # magentaprint('Use.healing_potion() ref: ' + str(ref))
                # if ref:  # not sure why 'has' or get ref is currently problematic... (error no target)
                #     self.execute(ref)
                #     # self.wait_for_flag()
                # else:
                #     continue
                # self.execute(pot)  # execute should definitely take a reference
                # self.execute(self.inventory.get_reference(pot))
                magentaprint("Consume.healing potion for {0}.".format(pot))
                # self.prompt_flag=False
                self.clear() # This works like .execute (.execute_and_wait will run this and wait for threading.Event to set when prompt comes)
                if pot == 'philtre of health':
                    # self.command = 'drin'
                    magentaprint("Switch to self.drink for philtre of health")
                    # self.execute(self.inventory.get_reference('philtre of health'))
                    self.drink.execute(self.inventory.get_reference('philtre of health'))
                    # self.command = 'use'
                    # So we aren't waiting here for errors...
                elif pot == 'tree root':
                    magentaprint("Switch to self.eat for tree root")
                    # self.execute(self.inventory.get_reference('philtre of health'))
                    self.eat.execute(self.inventory.get_reference('tree root'))
                else:
                    self.use.execute(self.inventory.get_reference(pot))
                # Inventory notices on its own 'a small restorative disintegrates'
                # self.wait_for_flag()  # Waiting to get the inventory upkeep right
                # if self.success or self.failure:
                #     self.inventory.remove(pot)
                # return True
                # break
                return True

        return False  # Ran out of pots.  use.result also provides return information

    def small_healing_potion(self):
        pots = ['chicken soup', 'small restorative', 'white potion', 'small flask']

        for pot in pots:
            if self.inventory.has(pot):
                self.clear()
                self.use.execute(self.inventory.get_reference(pot))
                return True

        return False

    # def can_heal(self):
    #     pots = ['chicken soup', 'small restorative', 'small flask', 'white potion', 'scarlet potion', 'large restorative']

    def wait_time(self):
        return max(self.use.wait_time(), self.drink.wait_time())
        # return max(self.use.wait_time(), self.drink.wait_time(), self.eat.wait_time)
    def wait(self):
        self.use.wait()
        self.drink.wait() # Should return instantly unless flag got cleared by execute
        # self.eat.wait()
    def wait_until_ready(self):
        # This is cooldowns on commands
        self.use.wait_until_ready()
        self.drink.wait_until_ready()
        # self.eat.wait_until_ready()
    def execute_and_wait(self):
        self.use.result   = ''
        self.drink.result = ''
        # self.eat.result = ''
        success = self.healing_potion()
        # self.healing_potion() # Why not success = ... maybe we should check consume.success
        self.wait()
        return success
        # if success:
        #     # self.wait()
        #     return success
        # else:
        #     return False

    @property
    def error(self):
        return self.use.error | self.drink.error # | self.eat.error
    @property
    def success(self):
        return self.use.success | self.drink.success # | self.eat.success
    @property
    def failure(self):
        return self.use.failure | self.drink.failure # | self.eat.success

class PotionThreadHandler(ThreadingMixin2):
    # Erhm, maybe I don't want a Potion thread because it will use too many pots if a prompt is delayed.
    # Solution - wait for prompt in the thread.
    # I think I was worried about that before I knew there was a cooldown

    def __init__(self, consume):
        self.end_thread_regexes = consume.use.error_regexes + consume.drink.error_regexes # ThreadingMixin2
        # self.end_thread_regexes = consume.use.error_regexes + consume.drink.error_regexes + eat.error_regexes
        super().__init__() # self.thread
        self.consume = consume
        # self.regex_cart.append(R.prompt)
        # self.regex_cart = R.prompt
        # We haven't done rods yet
        # self.drink = drink
        # self.eat = eat

    def run(self):
        magentaprint("Sending consume command (use, drink, maybe eat) in " + str(round(self.consume.wait_time())) + " seconds.")
        self.consume.wait_until_ready()
        # self.prompt_flag = False
        # self.clear() # threading.Event for prompt
        while not self.stopping:
            # if not self.stopping and self.consume.healing_potion():
            if self.consume.healing_potion():
                self.consume.wait() # Wait for prompt in case it's slow, we can wait for it
                # while not self.prompt_flag:
                #     self.clear()
                #     self.wait() # (Multiple notifications to wait for before this was its own object)
                # Loop back and pot again after prompt flag (expect to be stopped externally)
                # self.wait_loop('prompt_flag')
                # self.wait() # threading.Event for prompt text
                # Implement cooldown after failure, cooldown after success?
                # self.consume.wait_until_ready()
                self.consume.wait_until_ready() # cooldown
                # self.prompt_flag = False
                # self.clear() # threading.Event for prompt
            else:
                magentaprint("Potion thread ended! No pots left!")
                return False # consume didn't have anything

        # Make sure SmartCombat gets notified first so that it can stop us when the prompt comes in with HP above threshold
        # so potion_drank has to be after Prompt.
        # Erhm... that doesn't seem good enough, even though they'll likely come in the same chunk.
        # I feel like smart combat should do the stopping, because we don't want to worry about mob damage here.
        # We should wait_for_prompt() and be later in the subscriber list.
        # ... I don't like having to worry about the subscriber list... at worst it's one extra potion though.

    def wait_until_ready(self):
        # self.use.wait_until_ready()
        # # self.eat.wait_until_ready()
        # self.drink.wait_until_ready()
        self.consume.wait_until_ready()
        # Asuume shared cooldown on drinking, using, eating?

    def use_granite(self):
        self.wait_until_ready()
        return self.consume.granite_potion()

    def spam_pots(self, prefer_big=False, use_golden=False):
        self.stopping = False
        self.consume.prefer_big = prefer_big
        self.consume.use_golden = use_golden
        if not self.thread or not self.thread.is_alive():
            # not is_alive() means it won't look at stopping anymore so we're good.
            self.thread = threading.Thread(target=self.run, args=())
            self.thread.daemon = True # daemon means that the program can exit even if this thread is alive
            self.thread.start()
        # else:
        #     # Well the other thread CAN stil be sleeping from a kill error.  (ie misspelled target)
        #     # That puts it into a 3 second sleep, then the timer gets corrected 0.3s after.
        #     # So.... maybe it must poll fast... or we need signals... do we use that thread or a new thread??
        #     # Maybe we write its code smarter to handle this case... don't sleep till after the cooldown's verified
        #     magentaprint("Command will be sent in " + str(round(self.wait_time())) + " seconds.")

# Can I double inherit like this... I think so... they have a common parent, I need to remove from inventory
# Better would be simple Use, Drink, Eat objects
# Then the thread spam process should be another object
# Right now we have a Use thread when we should have a potion thread

# (These comments were moved off of PotionThreadHandler, which doesn't use inventory)
# We need to tell inventory when we've deleted an item (TODO)
# Inherit CommandThatRemovesFromInventory
# Move off of ThreadingMixin2
# In notify, notice if an item has 'disintegrated'
# Since inventory doesn't know which one we used
# (When does that matter? small inhalers and white amulets don't disintegrate)
