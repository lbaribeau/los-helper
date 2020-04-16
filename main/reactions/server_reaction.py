
from comm import RegexStore
from misc_functions import magentaprint

class ServerReaction(object):
    def __init__(self):
        self.regex_cart = [RegexStore.backup_shutdown]
        self.is_rebooting = False
        
    def notify(self, regex, M_obj):
        magentaprint("notified {}".format(M_obj), False)
        self.reboot()
        #set a flag on the character that indicates they should be dormant
        #this should tell the bot to go back to the chapel
        #then the bot should call the command handler call the quit command
        #then los_helper should shutdown the remaining threads and sleep for 20-30 minutes
        #los_helper should then try logging back in if it fails give it another 5-10 minutes

    def reboot(self):
        self.is_rebooting = True

    def reset(self):
        self.is_rebooting = False