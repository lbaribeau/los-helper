
from combat.CombatObject import SimpleCombatObject
from comm import RegexStore as R
from misc_functions import magentaprint

class Kill(SimpleCombatObject):
    command = 'k'
    cooldown_after_success = 3
    cooldown_after_failure = 3
    regexes = []

    good_MUD_timeout = 4  # You don't want to fail too badly during combat.

    success_regexes = [R.attack_hit]
    failure_regexes = [R.attack_miss]
    error_regexes   = [R.bad_k_target] 
    # SmartCombat also has to stop on bad target

    def __init__(self, telnetHandler):
        super().__init__(telnetHandler)

        # self.regex_cart.extend([R.hastened, R.already_hastened, R.feel_slower, R.circle_fail])
        self.regex_cart.extend([R.hastened, R.already_hastened, R.feel_slower])

    def notify(self, regex, M_obj):
        if regex in R.attack_hit:
            # magentaprint("kill notified: " + str(M_obj.group(0)), False)
            if "over" in M_obj.groupdict() and M_obj.group('over') is not None:
                # magentaprint("Mob killed - stopping kill thread", False)
                self.target_dead = True
                self.stop()
            else:
                target_dead = False
        elif regex in R.hastened or regex in R.already_hastened:
            Kill.cooldown_after_success = 2
            Kill.cooldown_after_failure = 2
        elif regex in R.feel_slower:
            Kill.cooldown_after_success = 3
            Kill.cooldown_after_failure = 3
            # Erhm... do we want to start a thread to get the timing exact... (todo)
        # elif regex in R.circle_fail:
        #     Kill.timer = Kill.timer -
        super().notify(regex, M_obj)

    # TODO: This should have a mob_target_determinator since it still gets used
