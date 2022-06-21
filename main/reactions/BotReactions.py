
from misc_functions import magentaprint 
import time

""" A BotReaction is an object that defines 'regexes' and 'notify' and
gets registered with the MudReader, which will call notify with a regex
in the list is matched."""

class BotReaction(object):
    pass
    # def __init__(self):
    #     self.unregistered = False
    # Hmmm, do I want everyone to inherit "self.unregistered = False" or
    # do I just want to task MudReaderHandler.register_reaction() with
    # tacking that on?  Currently, it works because both are sort of
    # happening, but it'd be kind of nice to get that inheritance in,
    # but it's also quite unnecessary.  MudReaderHandler doing it
    # is super flexible too, you could just throw anything in there.

# class BotReaction(object):
#     # Not defining init to allow for multiple inheritance
#     # def __init__(self, regexes):
#     #     if isinstance(regexes, str):
#     #         regexes = [regexes]
#     #     self.regexes = regexes
#     def notify(self, regex, M_obj):
#         """ This function is called by MudReaderThread when regex was
#         matched.  MudReaderThread gives the regex back so that the Reaction
#         can know which was matched, and M_obj is given so that the matching
#         text can be used.
#         """
#         raise NotImplementedError()
    def wait_loop(self, flag_name):
        start_time = time.time()
        run_time = 0

        while not getattr(self, flag_name) and run_time < self.good_MUD_timeout:
            time.sleep(0.05)
            run_time = time.time() - start_time

        if not getattr(self, flag_name):
            magentaprint(str(self) + ".wait_loop() timed out!")
            return False
        else:
            setattr(self, flag_name, False)
            return True

def wait_for_a_flag(class_with_flag):
    # magentaprint("wait_for_flag() called on " + str(class_with_flag) + " starting " + str(class_with_flag._waiter_flag) + ".")
    # I dunno why this always gets to 8 seconds and doesn't detect the flag.
    class_with_flag._waiter_flag = False  # Use __class__ for writing or else it will make an instance level flag
    start_time = time.time()
    run_time = 0

    # if not hasattr(class_with_flag, 'stopping'):
    #     class_with_flag.stopping = False

    # while not class_with_flag._waiter_flag and run_time < class_with_flag.good_MUD_timeout and not class_with_flag.stopping:
    # Often we are waiting for a flag while 'stopping', since targets get changed... (?)
        # Maybe that can be addressed. - I should call 'keep going' whenever changing targets.
        # Well SmartCombat doesn't use use threads
    while not class_with_flag._waiter_flag and run_time < class_with_flag.good_MUD_timeout:
        time.sleep(0.05)
        run_time = time.time() - start_time

    if not class_with_flag._waiter_flag:
        magentaprint("BotReaction.wait_for_flag() timed out!" + str(class_with_flag))
        return False  # Timed out
    else:
        class_with_flag._waiter_flag = False
        return True


class BotReactionWithFlag(BotReaction):
    """ wait_for_flag() is useful when you send a telnet command and
    want to wait for the server's response to that command. """

    _waiter_flag = True
    good_MUD_timeout = 5.0  # *Needs to be long enough to handle lag

    # def __init__(self):
        # regexes must also get set
        # self.unregistered = False

    def notify(self, regex, M_obj):
        """ Subclasses should implement notify and also ensure that _waiter_flag
        gets set."""
        # magentaprint("BotReactionWithFlag setting _waiter_flag on " + str(self) + " from " + str(self._waiter_flag))
        self.__class__._waiter_flag = True

    def wait_for_flag(self):
        # magentaprint("Waiting for flag " + str(self), end="")
        wait_for_a_flag(self.__class__)

        # self._waiter_flag = False
        # start_time = time.time()
        # run_time = 0
        # magentaprint("Waiting for flag " + str(self), end="")

        # while not self._waiter_flag and run_time < self.good_MUD_timeout:
        #     time.sleep(0.05)
        #     run_time = time.time() - start_time

        # # magentaprint("... done waiting.", timestamp=False)

        # if not self._waiter_flag:
        #     magentaprint("BotReactionWithFlag.wait_for_flag() timed out! " + str(self))
        #     return False  # Timed out
        # else:
        #     self._waiter_flag = False
        #     return True

    # @staticmethod
    # def wait_for_class_flag():
    #     wait_for_a_flag(__class__)

    @classmethod
    def wait_for_class_flag(cls):
        # magentaprint("wait_for_class_flag on " + str(cls))
        # magentaprint(str(cls._waiter_flag))
        wait_for_a_flag(cls)
        # magentaprint("wait_for_class_flag done ")


    # * A high MUD_timeout allows for big lag, which is nice.
    # You can get stuck on the road if you get impatient and send extra commands.
    # Remember that commands don't timeout unless there's lag or a regex is
    # missing, so having this high shouldn't slow anything down.  If it does,
    # a regex can be handled better.

# class BotReactionWithClassFlag(BotReaction):
#     """ This reaction provides a flag that can be watched at the class level,
#     so you don't need to have the reaction object on hand to watch the flag."""


class GenericBotReaction(object):
    """ BotReaction which takes telnet_commands as an additional argument,
    and uses it to define notify.  This type of BotReaction can't make
    use of M_obj."""

    def __init__(self, regexes, commandHandler, telnet_commands):

        if isinstance(regexes, str):
            regexes = [regexes]

        self.regexes = regexes
        self.commandHandler = commandHandler

        if isinstance(telnet_commands, str):
            self.telnet_commands = [telnet_commands]
        else:
            self.telnet_commands = telnet_commands

    def notify(self, regex, M_obj):
        for cmd in self.telnet_commands:
            self.commandHandler.process(cmd)

# add init with character and commandHandler
# make a reaction type for kill thread
