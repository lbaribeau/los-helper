
import time
from misc_functions import magentaprint

class MudEvent(object):
    good_MUD_timeout = 5.0

    def __init__(self, regexes):
        self.regexes = regexes
        self.subscribers = []
        self.flag = False
        # for r in regexes:
        #     magentaprint("MudEvent regex " + str(r))

    def notify(self):
        self.flag = True

    def wait_for_flag(self):
        # The other flag code is riddled with @classmethod scope which 
        # got messier than I wanted, so I'll write the loop again
        start_time = time.time()
        run_time = 0

        # This should maybe support 'stopping'
        while not self.flag and run_time < self.good_MUD_timeout:
            time.sleep(0.05)
            run_time = time.time() - start_time

        if not self.flag:
            magentaprint("MudEvent.wait_for_flag() timed out!" + str(class_with_flag))
            return False  # Timed out
        else:
            self.flag = False
            return True 








