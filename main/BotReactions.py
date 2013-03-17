
class BotReaction(object):
    """ This type of object has a regex and defines notify.  
    It gets registered with the MudReader and the notify 
    gets executed when the Mud sends text matching the regex.
    los-helper creates these objects and registers them with 
    MudReaderHandler at the same time it starts BotThread.
    If you're wondering about the "(object)" read about 
    new-style classes.
    http://stackoverflow.com/questions/1713038/super-fails-with-error-typeerror-argument-1-must-be-type-not-classobj
    """
    def abstract():
        import inspect
        caller = inspect.getouterframes(inspect.currentframe())[1][3]
        raise NotImplementedError(caller + ' must be implemented in subclass')
    
    def __init__(self, regex):
        self.regex = regex
    
    def notify(self, M_obj):
        """ This function is called by MudReader when regex was 
        matched.  MudReader gives the match object so that 
        the telnet command can use the text from it.  
        telnet_command gets sent. """
        abstract()

class GenericBotReaction(BotReaction):
    """ BotReaction which takes telnet_commands as an additional argument, 
    and uses it to define notify """
    
    def __init__(self, regex, commandHandler, telnet_commands):         
        super(GenericBotReaction, self).__init__(regex)
        self.commandHandler = commandHandler
        self.telnet_commands = telnet_commands
        
    def notify(self, M_obj):
        for cmd in telnet_commands:
            commandHandler.process(cmd)
            
# add init with character and commandHandler
# make a reaction type so that the kill thread can inherit it and define notify
class WieldReaction(BotReaction):
    """ notify will execute wield commands."""
    
    def __init__(self, regex, character, commandHandler):
        super(WieldReaction, self).__init__(regex)
        self.character = character
        self.commandHandler = commandHandler
    
    def notify(self, M_obj):
        reequip_weapon(M_obj.group(1))
        
    def reequip_weapon(self, weapon_str):
        if(self.character.WEAPON1 == self.character.WEAPON2):
            # If weap 1 and weap 2 are the same, not sure how to know 
            # which broke... so just put in both commands :)
            self.commandHandler.process("wie " + weapon_str)
            self.commandHandler.process("seco " + weapon_str)
        else:
            if(weapon_str == self.character_inst.WEAPON1):
                self.commandHandler.process("wie " + weapon_str)
            else:
                self.commandHandler.process("seco " + weapon_str)
        #magentaprint("Reequip weapon needs to be reimplemented.")
    
    