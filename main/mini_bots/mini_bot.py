
from threading import Thread
from misc_functions import magentaprint

# class MiniBot(Thread):
class MiniBot(object):
    # Probably no regexes/reactions
    # No wait loops - let the other objects do all that
    # Pure sequential action
    # Ehrm, I think the no regexes idea may have been axed
    #  - It was a scoping thing on bot wield logic.  The "no regexes" plan involved using only variables on sub objects,
    #    ie. Cast has aura variables, wield has 1st weapon variable and Second has off hand weapon variable.  The bot needed
    #    logic involving both weapon variables with write access, and the wield/second commands didn't know enough to keep those
    #    variables accurate (regex info wasn't complete,) so I axed the no regexes thing.  Maybe, however, it will only need a few.
    # We are going to support stopping here, which means inheriting Thread, because to be human usable, a new thread must be spawned,
    # and stopping/starting these processes ties logically with making/ending a thread.
    # Correction: MiniBot should HAVE a thread.  Being a thread makes arguments difficult (ie. TravelBot's go location)
    # This sets up a 1:1 between minibots and threads.  A complex minibot should HAVE other minibots.  ie. WeaponBot can have a
    # smithybot and call its method directly.  Right now WeaponBot inherits SmithyBot, which is not as good (more complexity on the
    # single object).

    def __init__(self):
        self.stopping = False
        self.thread = None

    def stop(self):
        magentaprint("MiniBot.stop()")
        # if self.thread and self.thread.is_alive():  # We also want to stop on calls where a new thread was not made
        # (SmithyBot calls TravelBot directly, so TravelBot.thread is still None, but another thread can call TravelBot.stop
        # which should stop SmithyBot)
        self.stopping = True

    def is_alive(self):
        if self.thread:
            return self.thread.is_alive()
        else:
            return False

    # def run(self):
    #      raise NotImplementedError("MiniBot children should implement run() or overwrite start_thread().")
    # run() does not need to be implemented since Thread is not inherited and threads are made from functions.

    def start_thread(self):
        # This is an example and can be overwritten if run() is not desired or needs arguments.
        # Implementing run() here is a bit confusing since we are NOT inherting Thread and we don't have to use run() at all
        self.thread = Thread(target=self.run)
        self.thread.start()

