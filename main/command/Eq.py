
from command.Command import Command
from comm import RegexStore as R

class Eq(Command):
    def __init__(self):
        self.regex_cart = [R.you_arent_wearing_anything, 
            R.on_body, R.on_arms, R.on_legs, R.on_neck, R.on_face, R.on_hands, R.on_head, 
            R.on_feet, R.on_finger, R.shield, R.wielded, R.seconded, R.holding
        ]
        # self.regex_cart = [R.you_arent_wearing_anything, R.eq]

    def notify(self, r, match):
        if r in R.on_body:
            self.body = match.group(1)
        elif r in R.on_arms:
            self.arms = match.group(1)
        elif r in R.on_legs:
            self.legs = match.group(1)
        elif r in R.on_neck:
            self.neck = match.group(1)
            self.neck2 = match.group('second_neck')
        elif r in R.on_face:
            self.face = match.group(1)
        elif r in R.on_hands:
            self.hands = match.group(1)
        elif r in R.on_head:
            self.head = match.group(1)
        elif r in R.on_feet:
            self.feet = match.group(1)
        elif r in R.on_finger:
            self.finger = match.group(1)
        elif r in R.shield:
            self.shield = match.group(1)
        elif r in R.wielded:
            self.wielded = match.group(1)
        elif r in R.seconded:
            self.seconded = match.group(1)
        elif r in R.holding:
            self.holding = match.group(1)

    def execute(self, target=None):
        self.body = ''
        self.arms = ''
        self.legs = ''
        self.neck = ''
        self.face = ''
        self.hands = ''
        self.head = ''
        self.feet = ''
        self.finger = ''
        self.shield = ''
        self.wielded = ''
        self.seconded = ''
        self.holding = ''
        super().execute(self, target)

    def notify(self, regex, M_obj):
        self.M_obj = M_obj

    @property
    def body(self):
        if self.M_obj:
            return self.M_obj.group('body')
        else:
            return None
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




# you_arent_wearing_anything = [r"You aren't wearing anything\."]
# on_body = [r"On body:   (.+?)\n\r"]
# on_arms = [r"On arms:   (.+?)\n\r"]
# on_legs = [r"On legs:   (.+?)\n\r"]
# on_neck = [r"On neck:   (.+?)\n\r(On neck:   (:P<second_neck>.+?)\n\r)?"]
# on_hands= [r"On hands:  (.+?)\n\r"]
# on_head = [r"On head:   (.+?)\n\r"]
# on_feet = [r"On feet:   (.+?)\n\r"]
# on_finger = [r"On finger: (.+?)\n\r"]
# shield  = [r"Shield:    (.+?)\n\r"]
# wielded = [r"Wielded:   (.+?)\n\r"]
# seconded= [r"Seconded:  (.+?)\n\r"]
# holding = [r"Holding:   (.+?)\n\r"]