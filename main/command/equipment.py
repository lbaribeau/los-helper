
from command.Command import Command
from comm import RegexStore as R
from misc_functions import magentaprint
from command.Inventory import parse_item_names

class Equipment(Command):
    def __init__(self, telnetHandler):
        # self.regex_cart = [R.you_arent_wearing_anything,
        #     R.on_body, R.on_arms, R.on_legs, R.on_neck, R.on_face, R.on_hands, R.on_head,
        #     R.on_feet, R.on_finger, R.shield, R.wielded, R.seconded, R.holding
        # ]
        # success/fail/error doesn't work so well in this case... do not inherit Command?
        # Add prompt [ bracket to end of regex to ensure full capture?
        # Can I assume that all the text comes in one clump?
        self.success_regexes = [R.you_arent_wearing_anything, R.eq]
        super().__init__(telnetHandler)
        self.slot_names = [
            'body','arms','legs','neck','neck2','face','hands','feet','finger','finger2','finger3',
            'finger4','finger5','finger6','finger7','finger8','shield','wielded','seconded','holding']
        self.reset()

    def reset(self):
        self.equipment = dict.fromkeys(self.slot_names)
        self.neck_count = 0
        self.finger_count = 0

    def notify(self, r, match):
        # magentaprint("Equipment notify, match 0 is " + match.group(0))

        # if r in R.eq:
        #     for slot_name in self.equipment.keys():
        #         magentaprint("Equipment command matched " + slot_name + " to " + match(slot_name))
        #         self.equipment[slot_name] = match(slot_name)
        if r in R.eq:
            for i in range(1,21):
                if match.group('slot'+str(i)):
                    self.equipment[self.determine_slot_name(match.group('slot'+str(i)))] = self.determine_gear_name(match.group('piece'+str(i)))
                else:
                    break
        else:
            self.equipment = dict.fromkeys(self.slot_names)

        magentaprint("Equipment dict set to " + str(self.equipment))
        super().notify(r, match)

    def execute(self, target=None):
        self.reset()
        super().execute(self, target)

    # def notify(self, regex, M_obj):
    #     self.M_obj = M_obj

    @property
    def body(self):
        if self.M_obj:
            return self.M_obj.group('body')
        else:
            return None

    def determine_slot_name(self, text_before_colon):
        if text_before_colon.startswith('On '):
            if text_before_colon[3:] == 'neck':
                self.neck_count = self.neck_count + 1
                if self.neck_count > 1:
                    return text_before_colon[3:] + str(self.neck_count)
            elif text_before_colon[3:] == 'finger':
                self.finger_count = self.finger_count + 1
                if self.finger_count > 1:
                    return text_before_colon[3:] + str(self.finger_count)
            return text_before_colon[3:]
        else:
            return text_before_colon.lower()
        return slot_name

    def determine_gear_name(self, text_after_colon):
        return parse_item_names(text_after_colon)[0]

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


# if r in R.on_body:
        #     self.body = match.group(1)
        # elif r in R.on_arms:
        #     self.arms = match.group(1)
        # elif r in R.on_legs:
        #     self.legs = match.group(1)
        # elif r in R.on_neck:
        #     self.neck = match.group(1)
        #     self.neck2 = match.group('second_neck')
        # elif r in R.on_face:
        #     self.face = match.group(1)
        # elif r in R.on_hands:
        #     self.hands = match.group(1)
        # elif r in R.on_head:
        #     self.head = match.group(1)
        # elif r in R.on_feet:
        #     self.feet = match.group(1)
        # elif r in R.on_finger:
        #     self.finger = match.group(1)
        # elif r in R.shield:
        #     self.shield = match.group(1)
        # elif r in R.wielded:
        #     self.wielded = match.group(1)
        # elif r in R.seconded:
        #     self.seconded = match.group(1)
        # elif r in R.holding:
        #     self.holding = match.group(1)


        # self.body = ''
        # self.arms = ''
        # self.legs = ''
        # self.neck = ''
        # self.face = ''
        # self.hands = ''
        # self.head = ''
        # self.feet = ''
        # self.finger = ''
        # self.shield = ''
        # self.wielded = ''
        # self.seconded = ''
        # self.holding = ''

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

