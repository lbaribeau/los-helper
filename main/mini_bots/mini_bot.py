
class MiniBot(object):
    # Probably no regexes/reactions
    # No wait loops - let the other objects do all that
    # Pure sequential action
    # Ehrm, I think the no regexes idea may have been axed
    #  - It was a scoping thing on bot wield logic.  The "no regexes" plan involved using only variables on sub objects,
    #    ie. Cast has aura variables, wield has 1st weapon variable and Second has off hand weapon variable.  The bot needed
    #    logic involving both weapon variables with write access, and the wield/second commands didn't know enough to keep those
    #    variables accurate (regex info wasn't complete,) so I axed the no regexes thing.  Maybe, however, it will only need a few.

    def __init__(self):
        self.stopping = False

    def stop(self):
        self.stopping = True

