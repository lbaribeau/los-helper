
from command.Command import Command
import comm.RegexStore as R

class Get(Command):
    command = 'get'
    success_regexes = [R.you_get]
    failure_regexes = [R.cant_carry, R.loot_blocked]
    error_regexes = [R.isnt_here, R.nothing_here]

    # This one's different because it can succeed AND fail
    # Since the fail regex (cant carry) comes last, failure takes precedence

    @property
    def cant_carry(self):
        return self.result in R.cant_carry

    # Commented: considered doing automatic ring wearing here

    def __init__(self, telnetHandler, inv):
        super().__init__(telnetHandler)
        self.inv = inv

    def notify(self, regex, match):
        if regex in R.you_get:
            # Erhm, currently Inventory adds stuff to itself on its own, which is fine
            # The we want an organized place to put automatic ring wearing... is it here??
            # For the human, sure, we may as well automate rings... it should be optional...
            # but defaulted to yes... so where do we do it... I want to take mudReaderHandler 
            # off of the bot, so the bot can be pure sequential action... smartCombat has 
            # some reaction based things - healing, ring wearing... so... it does it when 
            # a mob breaks a ring... the human should do get all, but not ring management, 
            # since it's annoying... so sure, get all could spawn a thread to do ring management.
            # It could be a mini bot.  

            # SmartCombat needs wear.
            # Get needs wear.... ???? maybe not!  What would ring bot do.  

            # Smart combat shouldn't do get all.... the bot should do that differently... like 
            # we want the human to do.  The bot should hit get all, then get should start a 
            # ring bot, and smart combat should remain
            # Smart combat does it on ring break.
            # Get does it on new ring
            pass
        super().notify(regex, match)


