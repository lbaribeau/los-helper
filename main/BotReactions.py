
from misc_functions import magentaprint 
import time

class BotReaction(object):
    """ This type of object has a list of regexes and defines notify.  
    It gets registered with the MudReader and the notify 
    gets executed when the Mud sends text matching any regex. """

    unregistered = False # MudReaderHandler uses this variable as part of the unregister procedure

    # Not defining init to allow for multiple inheritance
    # def __init__(self, regexes):
    #     if isinstance(regexes, str):
    #         regexes = [regexes]
    #     self.regexes = regexes

    def notify(self, regex, M_obj):
        """ This function is called by MudReaderThread when regex was 
        matched.  MudReaderThread gives the regex back so that the Reaction 
        can know which was matched, and M_obj is given so that the matching 
        text can be used.  
        """
        raise NotImplementedError()


class BotReactionWithFlag(BotReaction):
    """ wait_for_flag() is useful when you send a telnet command and 
    want to wait for the server's response to that command. """

    _waiter_flag = True
    good_MUD_timeout = 8.0  #* (see footnote)

    def notify(self, regex, M_obj):
        """ Subclasses should implement notify and also ensure that _waiter_flag
        gets set."""
        self._waiter_flag = True

    def wait_for_flag(self):
        self._waiter_flag = False
        start_time = time.time()
        run_time = 0
        magentaprint("Waiting for flag " + str(self), end="")

        while not self._waiter_flag and run_time < self.good_MUD_timeout:
            time.sleep(0.05)
            run_time = time.time() - start_time

        # magentaprint("... done waiting.", timestamp=False)

        if not self._waiter_flag:
            magentaprint("BotReactionWithFlag.wait_for_flag() timed out! " + str(self))
            return False  # Timed out
        else:
            self._waiter_flag = False
            return True

    # * A high MUD_timeout allows for big lag, which is nice. 
    # You can get stuck on the road if you get impatient and send extra commands.
    # Remember that commands don't timeout unless there's lag or a regex is 
    # missing, so having this high shouldn't slow anything down.  If it does, 
    # a regex can be handled better.


class GenericBotReaction(BotReaction):
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

class WieldReaction(BotReaction):
    """ notify will execute wield commands."""
    
    def __init__(self, character, commandHandler):
        # Note: regex should specify the weapon string in a group.
        self.regexes = [ "Your (.+?) breaks and you have to remove it\.",
                         "Your (.+?) shatters\."]
        self.character = character
        self.commandHandler = commandHandler

    def notify(self, regex, M_obj):
        magentaprint("Reequiping weapon..." + M_obj.group(1))
        self.reequip_weapon(M_obj.group(1))
        
    def reequip_weapon(self, weapon):        
        if self.character.WEAPON1 == self.character.WEAPON2:
            self.commandHandler.process("wie " + weapon)
            self.commandHandler.process("seco " + weapon)
        else:
            if weapon == self.character.WEAPON1:
                self.commandHandler.process("wie " + weapon)
            else:
                self.commandHandler.process("seco " + weapon)
