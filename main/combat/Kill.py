
from combat.CombatObject import SimpleCombatObject
from comm import RegexStore

class Kill(SimpleCombatObject):
    command = 'k'
    cooldown_after_success = 3
    cooldown_after_failure = 3 
    regexes = [] 

    good_MUD_timeout = 4  # You don't want to fail too badly during combat.

    success_regexes = [RegexStore.attack_hit]
    failure_regexes = [RegexStore.attack_miss]
    error_regexes = [RegexStore.bad_k_target]

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)
        # self.regex_cart.extend([RegexStore.hastened, RegexStore.already_hastened, RegexStore.feel_slower, RegexStore.circle_fail])
        self.regex_cart.extend([RegexStore.hastened, RegexStore.already_hastened, RegexStore.feel_slower])

    def notify(self, regex, M_obj):
        if regex in RegexStore.hastened or regex in RegexStore.already_hastened:
            Kill.cooldown_after_success = 2  
            Kill.cooldown_after_failure = 2  
        elif regex in RegexStore.feel_slower:
            Kill.cooldown_after_success = 3
            Kill.cooldown_after_failure = 3  
            # Erhm... do we want to start a thread to get the timing exact... (todo)
        # elif regex in RegexStore.circle_fail:
        #     Kill.timer = Kill.timer - 
        super().notify(regex, M_obj)
