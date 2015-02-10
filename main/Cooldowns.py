
from BotReactions import BotReaction

from Command import Kill

class Cooldowns(BotReaction):
    """ This class watches for messages from the server indicating 
    a problem with a kill or cast command which means that the cooldown 
    can be reset, like a mistyped target or spell name.

    This object will persist forever and be set up by LosHelper.  I am 
    also creating Kill and Cast objects whose lifetimes are very short.  
    """

    # Class variables
    # kill_cooldown = 3.0
    # cast_cooldown = 6.0  # Gets overridden by mage/cleric
    # kill_clock = time.time() - kill_cooldown
    # cast_clock = time.time() - cast_cooldown
    # move_clock = time.time() - move_cooldown

    # hasting = False

    reset_kill_clock = [
        "Attack what\?"
    ]

    reset_cast_clock = [
        "That spell does not exist\.",
        "You don't know that spell\.",
        "You cannot meet the casting cost!",
        "Spell name is not unique\.",
        "Cast what\?",
        "Cast at whom\?",
        "They are not here\.",
        "Your spell fails\."
    ]

    set_hasting = [
        "You feel yourself moving faster\.",
        "You're already hastened\."
    ]

    unset_hasting = [
        "You feel slower\."
    ]

    set_kill_clock_for_haste = [
        "You feel yourself moving faster\.",
        "You're already hastened\.",
        "You feel slower\."
    ]

    def __init__(self, mudReaderHandler, telnetHandler):
        self.regexes.extend([
            self.reset_kill_clock, 
            self.reset_cast_clock, 
            self.set_kill_clock_for_haste
        ])

    def notify(self, regex, M_obj):
        if regex in self.reset_kill_clock:
            # self.kill_clock = time.time() - self.kill_cooldown
            Kill.timer = time.time() - self.kill_cooldown
        if regex in self.reset_cast_clock:
            self.cast_clock = time.time() - self.cast_cooldown
        if regex in self.set_hasting:
            self.hasting = True
            self.kill_cooldown = 2.0
        if regex in self.unset_hasting:
            self.hasting = False
            self.kill_cooldown = 3.0
            #self.kill_clock = self.kill_clock + 1  #Try this if there are issues coming out of haste

    @staticmethod
    def wait_for_attack_ready(self):
        magentaprint("Cooldowns.wait_for_attack_ready sleeping " + str(round(self.attack_wait_amount(), 1)))
        time.sleep(self.attack_wait_amount())

    @staticmethod
    def wait_for_cast_ready(self):
        magentaprint("wait_for_cast_ready sleeping " + str(round(self.cast_wait_amount(), 1)))
        time.sleep(self.cast_wait_amount())

    @staticmethod
    def attack_wait_amount(self):
        attack_period = 2.0 if self.hasting else 3.0
        return self.wait_amount(self.kill_clock, self.kill_period)

    @staticmethod
    def attack_ready(self):
        return self.attack_wait_amount() <= 0

    @staticmethod
    def cast_wait_amount(self):
        return self.wait_amount(self.cast_clock, self.cast_period)

    @staticmethod
    def cast_ready(self):
        return self.cast_wait_amount() <= 0

    @staticmethod
    def wait_for_move_ready(self):
        self.wait_for_attack_ready()
        self.wait_for_cast_ready()
        # time.sleep(max(0, self.MOVE_WAIT - (time.time() - character.MOVE_CLK)))
        time.sleep(self.wait_amount(self.move_clock, self.move_period))

    @staticmethod
    def move_ready(self):
        return self.cast_ready() and \
               self.attack_ready() and \
               time.time() > self.move_clock + self.move_period

    @staticmethod
    def busy_loop(flag):
        flag = False
        while not flag:
            time.sleep(0.02)

    @staticmethod
    def wait_amount(self, time_triggered, period):
        return max(time_triggered + period - time.time(), 0)


# Send() on class Kill needs to provide a non-blocking kill call for the Human player.  
# Will this call make an object?  Maybe yes!  
