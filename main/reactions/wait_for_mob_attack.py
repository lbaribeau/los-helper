
import threading
from comm import RegexStore as R
from misc_functions import magentaprint
from datetime import datetime

class MobAttackWaiter(threading.Event):
    # The idea is we enter a new node, and we believe we may have an attacker here,
    # but we don't want to target the wrong thing
    # So we wait for a mob to hit us 
    # (ie. we chase a drunken minor, but a second before we do, another drunken miner enters that zone
    # so we can't assume we should hit the last drunken miner
    # and we don't necessary know with certainty which miner it is, the 2nd last,
    # so we plan to wait a second to take a hit so we know)

    def __init__(self):
        # Thread 1, setup
        super().__init__()
        self.regex_cart = [
            R.mob_joined1,
            R.mob_joined2,
            R.mob_attacked,
            R.mob_aggro,
            # R.is_attacking_you,
            R.blocked_path
        ]
        # mob_attackedis the main one
        # (selected regexes with __three_possible_mob_strings)

    def notify(self, regex, match):
        #(Thread 2, MudReaderThread)
        self.last_regex = regex
        self.last_match = match
        self.set() # This notifies other objects if they were waiting for this Event that they can go
        # (.clear() resets the flag, preparing it to be used again)

    def wait_for_mob_attack(self):
        # (Thread 1, bot thread or user thread)
        self.clear() # sets up flag
        magentaprint("MobAttackWater.wait() called.")
        self.last_regex = None
        self.last_match = None
        super().wait(5) # Should set last_regex and last_match to something if a mob attacked
        # If a mob didn't attack, we could use 
        # (Presumes an attacker will attack in 5 seconds)
        return self.last_match
        # Please reset me when you use me with .clear()

