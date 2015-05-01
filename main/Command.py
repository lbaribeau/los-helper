
import time
import itertools

from BotReactions import BotReactionWithFlag
from misc_functions import magentaprint
import RegexStore

# I need to rewrite Command because the current version has too much registering/unregistering.
# Working from a copy of Command.py...

    # XXXXXXXXXXX NOPE
    # - The main thing that I want out of this class is to provide 'blocking' calls.
    # - That is, the ability to issue the command to the server and wait for the response. 
    # - That may seem unnecessary, but without a class that does it well, lag can be a 
    # - little frustrating.  BotReactions provides this pretty much on its own, 
    # - but there is a little bit more common code to encapsulate here.
    # Actually, there isn't... this is purely for cooldown stuff.

    # Ummmm... is this even necessary??? There's no common code to Info and Whois...
    # This code has to be for commands that keep an object in the list, which is 
    # all the combat abilities and perhaps a Go ability... I think one-time 
    # commands can just copy Info and Whois.

class Command(BotReactionWithFlag):
    # The main point of this is to write code for the Kill, Cast, Ability, and 
    # Go timers... ie execute_and_block_serious()

    # So we're expecting one instance of these objects in the reaction list to 
    # keep the timing class variables up to date. (notify)  Call super just to 
    # keep wait_for_flag() legitimate.

    # Maybe write code to use 'command' ??? might help with inheritance...

    # Subclasses must set 
    # - success_regexes
    # - failure_regexes
    # - cooldown_on_success
    # - cooldown_on_failure
    # Subclasses must have
    # - timer
    # because this ain't the proper scope
    # X - actually... give it a shot!

    timer = 0
    # success_regexes = []
    failure_regexes = []
    error_regexes = []
    # Maybe have an inheritance level for commands without cooldowns?  Meh for now.
    cooldown_after_success = 0  # Rename to cooldown_on_success (todo)
    cooldown_after_failure = 0

    # def __init__(self, mudReaderHandler, telnetHandler, spell=None, target=None):
    def __init__(self, telnetHandler):
        self.telnetHandler = telnetHandler

        self.please_wait_time = -1  # This variable is in case the server tells us to wait
                                    # Keep at -1 unless a "Please wait" message is given

        # self.regexes = self.regexes + self.success_regexes
        # self.regexes = self.success_regexes[:]

        self.regexes = list(itertools.chain.from_iterable(self.success_regexes + self.failure_regexes + self.error_regexes))
        # s = self.success_regexes[0] if isinstance(self.success_regexes[0], list) else self.success_regexes
        # f = self.failure_regexes[0] if isinstance(self.failure_regexes[0], list) else self.failure_regexes
        # e = self.error_regexes[0] if isinstance(self.error_regexes[0], list) else self.error_regexes
        # self.regexes = list(itertools.chain.from_iterable(s, f, e))

        # self.regexes.extend(self.success_regexes)
        # self.regexes.extend(self.failure_regexes)
        # self.regexes.extend(self.error_regexes)
        # magentaprint(str(self.__class__) + " regexes: " + str(self.regexes))
        self.regexes.extend(RegexStore.please_wait)
        self.regexes.extend(RegexStore.please_wait2)

        # self.regex_cart = [
        #     self.success_regexes, self.failure_regexes, self.error_regexes
        # ] + RegexStore.please_wait + RegexStore.please_wait2
        # self.regex_cart = self.success_regexes + self.failure_regexes + self.error_regexes + \
        #     [RegexStore.please_wait, RegexStore.please_wait2]
        # self.regex_cart.extend(self.success_regexes + self.failure_regexes + self.error_regexes + \
        #     [RegexStore.please_wait, RegexStore.please_wait2])
        self.regex_cart = self.success_regexes + self.failure_regexes + self.error_regexes + \
            [RegexStore.please_wait, RegexStore.please_wait2]
        # magentaprint(str(self.__class__) + " init regex_cart: " + str(self.regex_cart))
        # self.result = 'success/failure/error'

    def notify(self, regex, M_obj):
        # magentaprint("Notify on Command " + str(self))
        # 'success' and 'fail' could be renamed to 'long cooldown' and 'short cooldown'
        # Abilities like Turn and Touch might need more code here...
        # We need 'success' 'fail' and 'error' with no cooldown on 'error'
        # ... well here goes nothing.
        # The plan for cooldowns is set it up for success when the command is sent, 
        # but correct it when the text comes back and we know the result.

        magentaprint(str(self) + " command notified, regex - " + regex[:30] + "...")

        # if regex in itertools.chain(self.success_regexes):
        if regex in itertools.chain.from_iterable(self.success_regexes):
            self.result = 'success'
            self.please_wait_time = -1
        # elif regex in [item for sublist in self.failure_regexes for item in self.failure_regexes]
        # elif regex in itertools.chain(*self.failure_regexes):
        elif regex in itertools.chain.from_iterable(self.failure_regexes):
            self.result = 'failure'
            self.please_wait_time = -1
            self.notify_failure(regex, M_obj)
            # [item for sublist in l for item in sublist]
        # elif regex in list(itertools.chain(self.error_regexes)):
        elif regex in itertools.chain.from_iterable(self.error_regexes):
            self.result = 'error'
            self.clear_timer()
        elif regex in RegexStore.please_wait:
            self.please_wait_time = int(M_obj.group(1))
            self.notify_please_wait()
        elif regex in RegexStore.please_wait2:
            self.please_wait_time = 60*int(M_obj.group(1)) + int(M_obj.group(2))
            self.notify_please_wait()

        super().notify(regex, M_obj)   # maintains wait_for_flag()

    def notify_failure(self, regex, M_obj):
        # This gets overriden by Cast
        self.__class__.timer = self.__class__.timer - self.cooldown_after_success + self.cooldown_after_failure

    def notify_please_wait(self):
        if not self.__class__._waiter_flag:
            self.result = 'Please wait ' + str(self.please_wait_time)
            self.__class__.timer = time.time() + self.please_wait_time  # Ehrm sometimes this makes it so you can't move

    @classmethod
    def clear_timer(cls):
        # Like when the command is ready to be issued
        cls.timer = time.time() - max(cls.cooldown_after_success, cls.cooldown_after_failure)

    @classmethod
    def start_timer(cls):
        # Like when command was just sent
        cls.timer = time.time() + cls.cooldown_after_success

    @classmethod
    def up(cls):
        return cls.timer < time.time()

    @classmethod
    def wait_time(cls):
        return cls.timer - time.time()

    @classmethod
    def send(cls, telnetHandler, target=None):
        # This function will be called by command handler when the human user uses the command 
        # and will do the things that the user wants.  If the cooldown is close, it'll wait that 
        # little bit before sending.  It updates the cooldown timer.

        # target needs to be a class variable at the lower class level (__class__.target)
        # command is also set by the child class
        #  X - target as a class variable is used only by CombatObject for threading...
        #    - target for Command must be a function argument (no class variable)

        # magentaprint("Command.send: cls.timer - time.time(): %.1f" % round(cls.timer - time.time(), 1))

        cls._waiter_flag = False
            # We set the waiter flag here because the 'Please wait' notify uses it to 
            # know that the 'Please wait' corresponds to the current command

        if cls.timer - time.time() < 3.0:
            # time.sleep(max(0, cls.timer - time.time()))
            cls.wait_until_ready()
        else:
            magentaprint("Command: not ready for %.1f seconds." % round(cls.timer - time.time(), 1))
            telnetHandler.write("") 
            return

        # cls.success = False
        # cls.failure = False
        # cls.error = False
        # cls.please_wait_time = -1

        telnetHandler.write(cls.compose_command(target))

        cls.start_timer()

    @classmethod
    def compose_command(cls, target=None):
        # Overridden by Go which isn't always "go ____" ie. "out", "up", "d", n/s/e/w
        return cls.command + " " + target if target else cls.command

    def execute(self, target=None):
        # Same as send() but gets called from instance
        # (send() doesn't need an instance but needs telnetHandler put in)
        self.result = ''
        self.send(self.telnetHandler, target)
        # self.wait_for_flag()  # Just expect caller to call wait.

    def super_execute(self, target=None):
        self.execute(target)
        self.wait_for_flag()
        while self.result == "Please wait 1":
            self.execute(target)
            self.wait_for_flag()

    @classmethod
    def wait_until_ready(cls):
        # magentaprint(str(cls) + " wait_until_ready waiting " + str(max(0, cls.timer - time.time())))
        time.sleep(max(0, cls.timer - time.time()))  # timer is a class variable







