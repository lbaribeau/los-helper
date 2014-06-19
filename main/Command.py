
import time

from BotReactions import BotReactionWithFlag 
from misc_functions import magentaprint

# class DanceOfTheCobra(CombatAbility):
#     def __init__(self, mudReaderHandler, telnetHandler):
#         self.command = "sing dance"  # needs target
#         self.cooldown_after_success = 570  # can hit right away i believe
#         self.cooldown_after_failure = 30  # can flee/move/attack
#         # success_regex = r"The Dance of the Snake ends\.\n\rYou complete the ritual by touching the (.+?) and the charming takes effect\.\.\."
#         self.success_regex = r"he Dance of the Snake ends"
#         # failure_regex = r"The Dance of the Snake has no effect on the (.+?)\.\r\n"  # and you can hit right away.
#         self.failure_regex = r"he Dance of the Snake has "
#         # classes = ["Brd"]
#         self.level = 1  # guessed
#         # magentaprint("Dance of the Cobra regexes before calling super: " + str(self.regexes))
#         self.regexes = []
#         super(DanceOfTheCobra, self).__init__(mudReaderHandler, telnetHandler)
#         # The mob just stops attacking, so how about turning off casting and just attacking him to death.
#         # You can attack immediately after on success or fail.
#         # But if you attacked then you have to wait to use it.

class Command(BotReactionWithFlag):
    # The main thing that I want out of this class is to provide 'blocking' calls.
    # That is, the ability to issue the command to the server and wait for the response. 
    # That may seem unnecessary, but without a class that does it well, lag can be a 
    # little frustrating.  BotReactions provides this pretty much on its own, 
    # but there is a little bit more common code to encapsulate here, especially 
    # cooldown code.

    # I think I can manage to do this without having to pass the same instance object
    # around every which place.  

    # The subclass has to set 'command', the cooldown variables and the success/failure 
    # regexes.

    # timer = 0
    please_wait = r"Please wait (\d+) more seconds?\."
    please_wait2 = r"Please wait (\d+):(\d+) more minutes" "\n\r"

    # def __init__(self, mudReaderHandler, telnetHandler, spell=None, target=None):
    def __init__(self, mudReaderHandler, telnetHandler):
        super(Command, self).__init__()
        magentaprint("Init for Command " + str(self))
        self.mudReaderHandler = mudReaderHandler
        self.telnetHandler = telnetHandler
        # Command.timer = time.time()  # gives the time when the ability is available
          # timer will have to be adjusted to be checked on login
          # The subclass will have to be in charge of timer, since it's a different timer
          # for each command, 
        self.success = False
        self.please_wait_time = -1
        self.regexes = []
        self.regexes.extend(self.success_regexes)
        self.regexes.extend(self.failure_regexes)
        # if spell:
        #     self.spell = " " + spell
        # if target:
        #     self.target = " " + target
        magentaprint(self.regexes)
        magentaprint("Registering " + str(self) + " with regexes " + str(self.regexes))
        # mudReaderHandler.register_reaction(self)

    def notify(self, regex, M_obj):
        if regex in self.success_regexes:
            self.success = True
            self.please_wait_time = -1
            self.mudReaderHandler.unregister_reaction(self)
        elif regex in self.failure_regexes:
            self.__class__.timer = self.__class__.timer - self.cooldown_after_success + self.cooldown_after_failure
            self.please_wait_time = -1
            self.mudReaderHandler.unregister_reaction(self)
        elif regex is self.please_wait:
            self.please_wait_time = int(M_obj.group(1))
            self.mudReaderHandler.unregister_reaction(self)
        elif regex is self.please_wait2:
            self.please_wait_time = 60*int(M_obj.group(1)) + int(M_obj.group(2))
            self.mudReaderHandler.unregister_reaction(self)

        magentaprint("Notify on Command was called.")

        super(Command, self).notify(regex, M_obj)

    def send(self, target=None):
        # This function will be called by command handler when the human user uses the command 
        # and will do the things that the user wants.  If the cooldown is close, it'll wait that 
        # little bit before sending.  It updates the cooldown timer.

        magentaprint("Command.send: self.__class__.timer - time.time(): %.1f" + str(round(self.__class__.timer - time.time(), 1)))

        if self.__class__.timer - time.time() < 0.75:
            time.sleep(max(0, self.__class__.timer - time.time()))
            magentaprint("Command.send: done sleeping.")
        else:
            magentaprint("Command: not ready for %.1f seconds." % str(round(self.__class__.timer - time.time(), 1)))
            return

        self.success = False
        self.please_wait_time = -1
        # magentaprint("Calling telnetHandler.write(" + self.command + " " + target + ")")

        self.mudReaderHandler.register_reaction(self)  

        if target:
            self.telnetHandler.write(self.command + " " + target)
        else:
            self.telnetHandler.write(self.command)

        self.start_timer()

        # Problem: The cooldown will be incorrectly set if the command failed.  So maybe 
        # send is an internal function, and commandHandler will only use the blocking?? 
        # No, I think that 'send' should register self.  Therefore notify() should unregister.
        # Maybe 'execute' will be a different register universe.  So execute won't call send.
        # So I think it's obvious now that __init__ won't register.

        # Alright... so why isn't 'execute' just 'send' and wait_for_flags?  Well, send right now 
        # doesn't register... send ought to register.  I think I was thinking send wouldn't register 
        # and I would have a permanently registered thing... but send may as well register.  It can 
        # check if it's registered...

    # def execute(self, target=""):
    #     time.sleep(max(0, self.timer - time.time()))
    #     self.send(target)

    def execute_and_block(self, target=None):
        # The caller should check up() unless they're okay with waiting a long time for the cooldown.
        # And, up() can even be wrong... so the caller had better make sure they check the cooldown
        # with the time() command as well.
        time.sleep(max(0, self.__class__.timer - time.time()))
        self.success = False
        self.please_wait_time = 0

        # mudReaderHandler.register_reaction(self)  # Commenting: send now registers.
        # Not registering till here means that the clock won't get corrected with send()
        # Maybe a different object can do that, since we want this one to be disposable.
        # I'd like to register the class object... but I'd have to join the dark side.
        self.send(target)
        self.wait_for_flag()

        while self.please_wait_time != -1:
            if please_wait_time <= 6:
                self.__class__.timer = 0
                if self.please_wait_time > 1:
                    time.sleep(self.please_wait_time - 1)
                self.send(target)
                self.wait_for_flag()
            else:
                break

        # self.mudReaderHandler.unregister_reaction(self)  # Commenting: send now registeres.
        # You have to wait 2 mudReaderThread loops or make a new object every time you use execute_and_block()
        # registering/unregistering is not expensive, it's just additionn/deletion of single objects in of the reaction list.

    def execute_and_block_serious(self, target=None):
        # serious: this command execute will work no matter the wait
        time.sleep(max(0, self.__class__.timer - time.time()))
        self.success = False
        self.please_wait_time = 0

        # mudReaderHandler.register_reaction(self)  # Commenting: send now registers.
        # Not registering till here means that the clock won't get corrected with send()
        # Maybe a different object can do that, since we want this one to be disposable.
        # I'd like to register the class object... but I'd have to join the dark side.
        self.send(target)
        self.start_timer()
        self.wait_for_flag()

        while self.please_wait_time != -1:
            self.unregistered = False  # "Undo" of the unregistering done by notify
                                       # We want to stay registered as we are sending the command again.
            self.clear_timer()
            if self.please_wait_time > 1:
                time.sleep(self.please_wait_time - 1)
            self.send(target)
            self.wait_for_flag()
            # notify() will set please_wait_time and we'll exit if the command was successful
            # and repeatedly send if we got please_wait

        # self.mudReaderHandler.unregister_reaction(self)  Commenting: send now registers.
        # You have to wait 2 mudReaderThread loops or make a new object every time you use execute_and_block()
        #   I think the desired use is to make a new Kill object every time you send the command, so we're good.
        #   (Kill being an example.)
        # registering/unregistering is not expensive, it's just additionn/deletion of single objects in of the reaction list.

    def clear_timer(self):
        # Like when the command is ready to be issued
        self.__class__.timer = 0

    def start_timer(self):
        # Like when command was just sent
        self.__class__.timer = self.__class__.timer + self.cooldown_after_success

    def up(self):
        return self.__class__.timer < time.time()


class Kill(Command):
    timer = 0

    def __init__(self, mudReaderHandler, telnetHandler):
        self.command = "kill"
        # self.target = " " + target
        self.cooldown_after_success = 3
        self.cooldown_after_failure = 3 
        super(Kill, self).__init__(mudReaderHandler, telnetHandler)
        # I think putting the cooldown as a class variable could work...
        # Then every instance will have the same one and I don't have to pass it around.
        # Maybe I can get away with just importing Kill

    success_regexes = [
        r"You swing with your .+?, hacking the (.+?) for \d+ damage\.",
        r"You slice the (.+?) for \d+ damage with your .+?\.",
        r"You slash at the (.+?) and hit for \d+ damage\.",

        r"You chop at the (.+?) for \d+ damage\.",
        r"You stab at the (.+?) with your .+?, causing \d+ damage"
        r"You lunge at the (.+?), striking for \d+ damage\.",

        r"You lash out and thump the (.+?) for \d+ damage\.",
        r"You punch the (.+?) for \d+ damage\.",
        r"You kick the (.+?) for \d+ damage\."
        r"You head-butt the (.+?) for \d+ damage\."
        r"You grab the (.+?) and gouge (him|her|it) for \d+ damage\.",

        r"You smash your .+? into the (.+?), causing \d+ damage\.",
        r"You heave your .+? at the (.+?), smashing (him|her|it) for \d+ damage\.",
        r"You bludgeon the (.+?) for \d+ damage\.",

        r"You lunge at the (.+?), hitting them for \d+ damage\.",
        r"You swing your .+?, striking for \d+ damage\.",
        r"You sweep the (.+?) with your .+? for \d+ damage\.",

        r"Your missile slams into the (.+?) for \d+ damage\.",
        r"You attack the (.+?) with your .+?, striking for \d+ damage\.",
        r"You use your .+? to strike the (.+?) for \d+ damage\.",
    ]

    failure_regexes = [
        r"You hack with your .+?, but your blow swings wide of the mark\.",
        r"You slice your (.+?) at the .+?, but miss\.",
        r"You slash at the (.+?), but miss\.",

        r"You chop at the (.+?) but fail to hit them\.",
        r"You try to stab the (.+?) with your .+?, but miss\.",
        r"You lunge wildly at the (.+?) but mistime the strike\.",

        r"You lash out at the (.+?), but miss\.",
        r"You swing a wild punch at the (.+?), but it misses\.",
        r"You kick at the (.+?), but fail to hurt them\.",
        r"You grab at the (.+?), but (s?he|it) escapes your grasp\.",
        r"You try to gouge the (.+?), but can't get a good grip\.",

        r"You swing your .+? at the (.+?), but miss\.",
        r"You heave your .+? in a wide arc, but fail to hit anything\.",
        r"You try to bludgeon the (.+?), but miss\.",

        r"You lunge at the (.+?), but you miss\.",
        r"Your .+? swings, but fails to connect\.",
        r"You sweep at the (.+?) with your .+?, but miss\.",

        r"Your missile arcs towards the (.+?), but fails to hit them\.",
        r"You attack the (.+?) with your .+?, but miss\.",
        r"You use your .+?, but nothing hits the (.+?)\."
    ]

# class Command(BotReactionWithFlag):
# 	# Subclasses should set self.regexes and self.command

#     def __init__(self, mudReaderHandler, telnetHandler):
#         self.mudReaderHandler = mudReaderHandler
#         self.telnetHandler = telnetHandler

#     def _execute(self):
#         self.regexes = [character_name.title() + "\s+?(\S\S\S)\s\s([MF])\s\s\[(\d\d)\](\S+)\s+(\d+)\s+(\S+)\s" ]
#         self.mudReaderHandler.register_reaction(self)
#         self.telnetHandler.write(self.command)
#         self.wait_for_flag()
#         self.mudReaderHandler.unregister_reaction(self)

#     def notify(self, regex, M_obj):
#         self.character_class = M_obj.group(1)
#         self.gender = M_obj.group(2)
#         self.level = int(M_obj.group(3))
#         self.title = M_obj.group(4)
#         self.age = M_obj.group(5)
#         self.race = M_obj.group(6)
#         super(Whois, self).notify(regex, M_obj)



# Hmmm...
# Would like
#  Kill().execute_blocking()
# for every ability...
# One issue is the cooldown.  If I construct a new object each time, then what object do I register to 
# update the cooldown?  The cooldown should persist.  Well, if I do a 'time' at the beginning, then perhaps
# the constructed objects are sufficient.  Another object is a 'ThreadStopper' like Cooldown object which 
# is always there to to update all cooldowns.  This gets unweildly with duplicate regexes unless we have only 
# single instances of each regex.  

# How about the former... cooldowns only get updated if there exists an object for the command.  I think that 
# 'time' can be an exception and initialize the cooldown class variables.