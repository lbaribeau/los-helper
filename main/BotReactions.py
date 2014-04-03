from misc_functions import magentaprint 

class BotReaction(object):
    """ This type of object has a regex and defines notify.  
    It gets registered with the MudReader and the notify 
    gets executed when the Mud sends text matching the regex.
    los-helper creates these objects and registers them with 
    MudReaderHandler at the same time it starts BotThread.
    """
    def abstract():
        import inspect
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        raise NotImplementedError(caller + ' must be implemented in subclass')
    
    def __init__(self, regex):
        self.regex = regex
        self.unregistered = False
    
    def notify(self, M_obj):
        """ This function is called by MudReader when regex was 
        matched.  MudReader gives the match object so that 
        the telnet command can use the text from it.  
        telnet_command gets sent. """
        abstract()


class GenericBotReaction(BotReaction):
    """ BotReaction which takes telnet_commands as an additional argument, 
    and uses it to define notify.  This type of BotReaction can't make 
    use of M_obj (the command can't use matched text.) """
    
    def __init__(self, regex, commandHandler, telnet_commands):
        assert not isinstance(telnet_commands, str) # telnet_commands MUST be a list, not a string
        super(GenericBotReaction, self).__init__(regex)
        self.commandHandler = commandHandler
        self.telnet_commands = telnet_commands
        
    def notify(self, M_obj):
        for cmd in self.telnet_commands:
            self.commandHandler.process(cmd) 
            
# add init with character and commandHandler
# make a reaction type so that the kill thread can inherit it and define notify
class WieldReaction(BotReaction):
    """ notify will execute wield commands."""
    
    def __init__(self, regex, character, commandHandler):
        # Note: regex should specify the weapon string in a group.
        super(WieldReaction, self).__init__(regex)
        self.character = character
        self.commandHandler = commandHandler
    
    def notify(self, M_obj):
        magentaprint("Reequiping weapon..." + M_obj.group(1))
        self.reequip_weapon(M_obj.group(1))
        
    def reequip_weapon(self, weapon_str):        
        if(self.character.WEAPON1 == self.character.WEAPON2):
            self.commandHandler.process("wie " + weapon_str)
            self.commandHandler.process("seco " + weapon_str)
        else:
            if(weapon_str == self.character.WEAPON1):
                self.commandHandler.process("wie " + weapon_str)
            else:
                self.commandHandler.process("seco " + weapon_str)