from misc_functions import magentaprint 

class BotReaction(object):
    """ This type of object has a list of regexes and defines notify.  
    It gets registered with the MudReader and the notify 
    gets executed when the Mud sends text matching any regex.
    """
    def abstract():
        import inspect
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        raise NotImplementedError(caller + ' must be implemented in subclass')
    
    def __init__(self, regexes):
        if isinstance(regexes, str):
            regexes = [regexes]

        self.regexes = regexes
        self.unregistered = False # MudReaderHandler uses this variable as part of the unregister procedure
        self.good_MUD_timeout = 1.2 
    
    def notify(self, regex, M_obj):
        """ This function is called by MudReaderThread when regex was 
        matched.  MudReaderThread gives the regex back so that the Reaction 
        can know which was matched, and M-obj is given so that the matching 
        text can be used.  
        """
        abstract()


class GenericBotReaction(BotReaction):
    """ BotReaction which takes telnet_commands as an additional argument, 
    and uses it to define notify.  This type of BotReaction can't make 
    use of M_obj."""
    
    def __init__(self, regexes, commandHandler, telnet_commands):
        super(GenericBotReaction, self).__init__(regexes)

        if isinstance(telnet_commands, str):
            self.telnet_commands = [telnet_commands]
        else:
            self.telnet_commands = telnet_commands

        self.commandHandler = commandHandler
        
    def notify(self, regex, M_obj):
        for cmd in self.telnet_commands:
            self.commandHandler.process(cmd) 
            
# add init with character and commandHandler
# make a reaction type for kill thread

class WieldReaction(BotReaction):
    """ notify will execute wield commands."""
    
    def __init__(self, character, commandHandler):
        # Note: regex should specify the weapon string in a group.
        super(WieldReaction, self).__init__([
            "Your (.*?) breaks and you have to remove it\.",
            "Your (.*?) shatters\."]
            )
        self.character = character
        self.commandHandler = commandHandler

    def notify(self, regex, M_obj):
        magentaprint("Reequiping weapon..." + M_obj.group(1))
        self.reequip_weapon(M_obj.group(1))
        
    def reequip_weapon(self, weapon):        
        if(self.character.WEAPON1 == self.character.WEAPON2):
            self.commandHandler.process("wie " + weapon)
            self.commandHandler.process("seco " + weapon)
        else:
            if(weapon == self.character.WEAPON1):
                self.commandHandler.process("wie " + weapon)
            else:
                self.commandHandler.process("seco " + weapon)
