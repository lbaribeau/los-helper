
import time
from itertools import chain

from reactions.BotReactions import BotReactionWithFlag
from misc_functions import magentaprint
from comm import RegexStore

# This does success/fail, cooldowns, and wait_for_flag support.

    # The main thing that I want out of this class is to provide 'blocking' calls.
    # That is, the ability to issue the command to the server and wait for the response.
    # That may seem unnecessary, but without a class that does it well, lag can be a
    # little frustrating.  BotReactions provides this pretty much on its own,
    # but there is a little bit more common code to encapsulate here.
    # Actually, there isn't... this is purely for cooldown stuff.

    # Ummmm... is this even necessary??? There's no common code to Info and Whois...
    # This code has to be for commands that keep an object in the list, which is
    # all the combat abilities and perhaps a Go ability... I think one-time
    # commands can just copy Info and Whois.

class SimpleCommand(BotReactionWithFlag):
    # Command with no cooldown, no success/fail, only execute.
    # ie. whois, info, spells
    # eq maybe
    def __init__(self, telnetHandler):
        super().__init__() #threading.Event
        self.telnetHandler = telnetHandler

    # @classmethod
    # Better use an object, not the class variables
    def send(self, telnetHandler, target=None):
        #self.
        if target:
            telnetHandler.write(self.command + ' ' + target)
        else:
            telnetHandler.write(self.command)

    def execute(self, target=None):
        # Same as send() but gets called from instance
        # (send() doesn't need an instance but needs telnetHandler put in)
        self.clear()
        self.send(self.telnetHandler, target)
        # self.wait_for_flag()  # Just expect caller to call wait.

    def execute_and_wait(self, target=None):
        self.execute(target)
        self.wait_for_flag()

class Command(SimpleCommand):
    # The main point of this is to write code for the Kill, Cast, Ability, and
    # Go timers... ie execute_and_block_serious() (persistent_execute())

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

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)

        self.please_wait_time = -1  # This variable is in case the server tells us to wait
                                    # Keep at -1 unless a "Please wait" message is given
        self.result = ''

        # self.regexes = self.regexes + self.success_regexes
        # self.regexes = self.success_regexes[:]

        self.regexes = list(chain.from_iterable(self.success_regexes + self.failure_regexes + self.error_regexes))
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
        self.regex_cart = \
            self.success_regexes + \
            self.failure_regexes + \
            self.error_regexes +   \
            [RegexStore.please_wait, 
            RegexStore.please_wait2]
        # magentaprint(str(self.__class__) + " init regex_cart: " + str(self.regex_cart))
        # self.result = 'success/failure/error'
        self._executing = False
        self._sent_target = None

    def notify(self, regex, M_obj):
        self.notify_success_fail_or_error(regex, M_obj)
        self._executing = False
        super().notify(None, None)  # maintains wait_for_flag()

    def notify_success_fail_or_error(self, regex, M_obj):
        # 'success' and 'fail' could be renamed to 'long cooldown' and 'short cooldown'
        # Abilities like Turn and Touch might need more code here...
        # We need 'success' 'fail' and 'error' with no cooldown on 'error'
        # ... well here goes nothing.
        # The plan for cooldowns is set it up for success when the command is sent, 
        # but correct it when the text comes back and we know the result.

        # magentaprint(str(self) + " command notified, regex - " + regex[:30] + "...")
        # if regex in itertools.chain(self.success_regexes):
        self.result = regex
        self.M_obj = M_obj

        if self.success:
            self.please_wait_time = -1
        # elif regex in [item for sublist in self.failure_regexes for item in self.failure_regexes]
        # elif regex in itertools.chain(*self.failure_regexes):
        elif self.failure:
            self.please_wait_time = -1
            self.notify_failure(regex, M_obj)
            # [item for sublist in l for item in sublist]
        # elif regex in list(itertools.chain(self.error_regexes)):
        elif self.error and self._executing:
            # if (regex in RegexStore.not_here and not self._waiter_flag) or regex not in RegexStore.not_here:  
            # if (regex in RegexStore.not_here and not self._waiter_flag) or regex not in RegexStore.not_here:  
            #magentaprint(str(self) + " clearing timer... wf is " + str(self._waiter_flag) + ', class wf is ' + str(self.__class__._waiter_flag) + 'regex is ' + regex[0:10] + '...')
            #magentaprint(str(self) + " clearing timer... wf is " + str(self.is_set()) + ', class wf is ' + str(self.__class__._waiter_flag) + 'regex is ' + regex[0:10] + '...')
            magentaprint(str(self) + " clearing timer... wf is " + str(self.is_set()) + 'regex is ' + regex[0:10] + '...')
            self.clear_timer()
        elif self.please_wait1:
            self.please_wait_time = int(M_obj.group(1))
            self.notify_please_wait()
        elif self.please_wait2:
            self.please_wait_time = 60*int(M_obj.group(1)) + int(M_obj.group(2))
            self.notify_please_wait()

    @property
    def success(self):
        return self.result in chain.from_iterable(self.success_regexes)
    @property
    def failure(self):
        return self.result in chain.from_iterable(self.failure_regexes)
    @property
    def error(self):
        return self.result in chain.from_iterable(self.error_regexes)
    @property
    def please_wait1(self):
        return self.result in RegexStore.please_wait
    @property
    def please_wait2(self):
        return self.result in RegexStore.please_wait2
    @property
    def please_wait(self):
        return self.please_wait1 or self.please_wait2

    # @classmethod
    def notify_failure(self, regex, M_obj):
        # This gets overriden by Cast
        self.timer = self.timer - self.cooldown_after_success + self.cooldown_after_failure

    def notify_please_wait(self):
        # A problem with Please wait is we can be notified even when it's from a different command.
        # It's pretty tough to keep things straight,
        # and it's pretty cool to use the info to deal with things properly.
        # Better do a hard check if the amount it says to wait makes sense.
        # It's particularly important for cast and kill, less so for abilities.
        # Cast and kill could set their timer on startup while abilties shouldn't. 
        # if not self.__class__._waiter_flag:
        if self._executing:
            # if self.__class__.timer:
            #     if abs(self.please_wait_time - self.wait_time()) < 2:
            #         self.result = 'Please wait ' + str(self.please_wait_time)
            #         self.__class__.timer = time.time() + self.please_wait_time  # Ehrm sometimes this makes it so you can't move
            #         # This reduces the error caused by the known bug to 2 sec.
            #         # It's not "complete" but 2 sec of error is much better.
            #         # However, if timer is ever wrong, it will never be corrected with a Please wait.
            #         # And the timer of an ability could get set wrong...
            #         # we should implement the Time command as a corrective measure.
            # else:
            #     self.result = 'Please wait ' + str(self.please_wait_time)
            #     self.__class__.timer = time.time() + self.please_wait_time

            # magentaprint(str(self) + " Command.notify_please_wait(), please_wait_time is " + str(self.please_wait_time) + ", self.wait_time is " + str(round(self.wait_time(), 1)))
            magentaprint("Command {} notify_please_wait() with {}, wait time was {}. ".format(self.__class__.__name__, self.please_wait_time, round(self.wait_time(), 1)))

            # if not self.__class__.timer or (self.__class__.timer and abs(self.please_wait_time - self.wait_time()) < 2):
            # if not self.__class__.timer or (self.__class__.timer and abs(self.please_wait_time - self.wait_time()) < 2):
            # timer gets set on execute() so we can assume it's set
            if self.please_wait_time <= max(self.cooldown_after_success, self.cooldown_after_failure):
            # If it's a big time it must be an ability - using the cooldown as a ceiling would help a little.
                # self.result = 'Please wait ' + str(self.please_wait_time)
                # self.result = self.please_wait1
                # self.__class__.timer = time.time() + self.please_wait_time  # Ehrm sometimes this makes it so you can't move
                # self.__class__.timer = time.time() + min(self.please_wait_time, self.cooldown_after_success, self.cooldown_after_failure) 
                # self.__class__.timer = time.time() + self.please_wait_time
                self.timer = time.time() + self.please_wait_time
                # We get false positives on this because the waiter flag is not a good indication that Please Wait belongs to us.
                # If we were careful about when it gets unset (when super().notify() is called,) we could potentially use that trick
                # Clipping with the cooldowns helps a bit.
                magentaprint("Command {} set wait time to {}".format(self.__class__.__name__, round(self.wait_time(), 0)))

    # @classmethod
    def clear_timer(self):
        # Like when the command is ready to be issued
        # magentaprint('Clearing timer: ' + str(cls))
        self.timer = time.time() - max(self.cooldown_after_success, self.cooldown_after_failure)

    # @classmethod
    def start_timer(self):
        # Like when command was just sent
        self.timer = time.time() + self.cooldown_after_success

    # @classmethod
    def up(self):
        return True if not self.timer else self.timer < time.time()
        # return cls.timer < time.time()

    # @classmethod
    def wait_time(self):
        # return cls.timer - time.time()
        # return 0 if not cls.timer else cls.timer - time.time()
        if not self.timer:
            # magentaprint(str(cls) + ".wait_time() returning 0 because timer is None.")
            return 0
        else:
            # magentaprint(str(cls) + ".wait_time() returning " + str(round(max(0, cls.timer - time.time()), 1)) + ".")
            return max(0, self.timer - time.time())

    # @classmethod
    # def send(cls, telnetHandler, target=None):
    #     # This function will be called by command handler when the human user uses the command 
    #     # and will do the things that the user wants.  If the cooldown is close, it'll wait that 
    #     # little bit before sending.  It updates the cooldown timer.

    #     # target needs to be a class variable at the lower class level (__class__.target)
    #     # command is also set by the child class
    #     #  X - target as a class variable is used only by CombatObject for threading...
    #     #    - target for Command must be a function argument (no class variable)

    #     # magentaprint("Command.send: cls.timer - time.time(): %.1f" % round(cls.timer - time.time(), 1))

    #     cls._waiter_flag = False 
    #         # We set the waiter flag here because the 'Please wait' notify uses it to 
    #         # know that the 'Please wait' corresponds to the current command
    #     # Eh we need 'self' for threading.Event - need objects for state (an object)

    #     if cls.wait_time() < 3.0:
    #         # time.sleep(max(0, cls.timer - time.time()))
    #         cls.wait_until_ready()
    #     else:
    #         magentaprint("Command: not ready for %.1f seconds." % round(cls.timer - time.time(), 1))
    #         telnetHandler.write("") 
    #         return

    #     # cls.success = False
    #     # cls.failure = False
    #     # cls.error = False
    #     # cls.please_wait_time = -1

    #     telnetHandler.write(cls.compose_command(target))

    #     cls.start_timer()
    def send(self, telnetHandler, target=None):
        # We need 'self' for threading.Event - need objects for state (an object)
        # self._waiter_flag = False 
        self.clear()
        # Well we won't know which command Please wait is for

        if self.wait_time() < 3.0:
            # time.sleep(max(0, self.timer - time.time()))
            self.wait_until_ready()
        else:
            magentaprint("Command: not ready for %.1f seconds." % round(self.timer - time.time(), 1))
            telnetHandler.write("") 
            return

        # cls.success = False
        # cls.failure = False
        # cls.error = False
        # cls.please_wait_time = -1

        telnetHandler.write(self.compose_command(target))

        self.start_timer()

    # @classmethod
    def compose_command(self, target=None):
        # Overridden by Go which isn't always "go ____" ie. "out", "up", "d", n/s/e/w
        return self.command + " " + target if target else self.command

    def execute(self, target=None):
        # Same as send() but gets called from instance
        # (send() doesn't need an instance but needs telnetHandler put in)
        # magentaprint("Command set _sent_target to {0}".format(target))
        self.result = ''
        self._executing = True
        self._sent_target = target # Some cases want to know what the target was when the regex comes back (remove from inventory)
        super().execute(target)  # sets the waiter flag and calls send

    def execute_and_wait(self, target=None):
        super().execute_and_wait(target)
        return self.success

    def persistent_execute(self, target=None):  # wait until ready?
        self.execute_and_wait(target)
        # while self.result == "Please wait 1":
        while self.please_wait1:
            self.execute_and_wait(target)

    # @classmethod
    def wait_until_ready(self):
        if self.wait_time() > 0:
            magentaprint("Command (" + self.__class__.__name__ + ") .wait_until_ready(self): " + str(round(self.wait_time(), 1)) + " seconds.")
        # return if not cls.timer else time.sleep(max(0, cls.wait_time()))
        # time.sleep(max(0, cls.timer - time.time()))  # timer is a class variable
        time.sleep(self.wait_time())
