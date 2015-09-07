
from command.Command import Command
from comm import RegexStore as R

class Eq(Command):
    def __init__(self):
        # self.regex_cart = [R.you_arent_wearing_anything, 
        #     R.on_body, R.on_arms, R.on_legs, R.on_neck, R.on_hands, R.on_head, 
        #     R.on_feet, R.on_finger, R.shield, R.wielded, R.seconded, R.holding
        # ]
        self.regex_cart = [R.you_arent_wearing_anything, R.eq]

    def notify(self, regex, M_obj):
        self.M_obj = M_obj

    @property
    def body(self):
        if self.M_obj:
            return self.M_obj.group('body')
        else:
            return Non
        # if regex in R.you_arent_wearing_anything:
        #     self.body = None
        #     self.arms = None
        #     self.legs = None
        #     self.neck = None
        #     self.neck2 = None
        #     self.body = None
        #     self.body = None
        #     self.body = None
        #     self.body = None
        #     self.body = None
        #     self.body = None
        #     self.body = None
        #     self.body = None




you_arent_wearing_anything = [r"You aren't wearing anything\."]
on_body = [r"On body:   (.+?)\n\r"]
on_arms = [r"On arms:   (.+?)\n\r"]
on_legs = [r"On legs:   (.+?)\n\r"]
on_neck = [r"On neck:   (.+?)\n\r(On neck:   (:P<second_neck>.+?)\n\r)?"]
on_hands= [r"On hands:  (.+?)\n\r"]
on_head = [r"On head:   (.+?)\n\r"]
on_feet = [r"On feet:   (.+?)\n\r"]
on_finger = [r"On finger: (.+?)\n\r"]
shield  = [r"Shield:    (.+?)\n\r"]
wielded = [r"Wielded:   (.+?)\n\r"]
seconded= [r"Seconded:  (.+?)\n\r"]
holding = [r"Holding:   (.+?)\n\r"]