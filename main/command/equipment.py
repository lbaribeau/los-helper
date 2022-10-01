
from itertools import chain
import json
from command.Command import Command
from comm import RegexStore as R
from misc_functions import magentaprint, output_api_feed
from command.Inventory import parse_item_names

class Equipment(Command):
    command = 'eq'
    def __init__(self, telnetHandler, is_headless=False):
        # self.regex_cart = [R.you_arent_wearing_anything,
        #     R.on_body, R.on_arms, R.on_legs, R.on_neck, R.on_face, R.on_hands, R.on_head,
        #     R.on_feet, R.on_finger, R.shield, R.wielded, R.seconded, R.holding
        # ]
        self.success_regexes = [
            R.you_arent_wearing_anything,
            R.one_equip, 
            R.prompt
        ]
        self.is_headless = is_headless
        # success/fail/error doesn't work so well in this case... do not inherit Command?
        # Add prompt [ bracket to end of regex to ensure full capture?
        # Can I assume that all the text comes in one clump?
        # self.success_regexes = [R.you_arent_wearing_anything, R.eq]
        super().__init__(telnetHandler)
        # self.regexes.extend(R.prompt)  # We will wait for the prompt to set the flag to avoid an early return
                                       # that doesn't catch all of the equipment
        # self.regex_cart.append(R.prompt)
        self.slot_names = [
            'body','arms','legs','neck','neck2','hands','head','feet','face','finger','finger2','finger3',
            'finger4','finger5','finger6','finger7','finger8','shield','wielded','seconded','holding']
        self.reset()

    def reset(self):
        self.dict = dict.fromkeys(self.slot_names)
        self.neck_count = 0
        self.finger_count = 0
        self.prompt_flag = 0
        self.eq_flag = 0

    def notify(self, r, match):
        # magentaprint("Equipment notify, match 0 is " + match.group(0))

        # if r in R.eq:
        #     for slot_name in self.equipment.keys():
        #         magentaprint("Equipment command matched " + slot_name + " to " + match(slot_name))
        #         self.equipment[slot_name] = match(slot_name)
        # if r in R.eq:
        #     for i in range(1,21):
        #         if match.group('slot'+str(i)):
        #             self.dict[self.determine_slot_name(match.group('slot'+str(i)))] = self.determine_gear_name(match.group('piece'+str(i)))
        #         else:
        #             break
        #     self.eq_flag = True
        # if r in chain.from_iterable(self.success_regexes)
        if r in R.one_equip:
            slot_name = self.determine_slot_name(match.group('slot'))
            if slot_name in self.dict.keys():
                self.dict[slot_name] = self.determine_gear_name(match.group('piece'))
                self.eq_flag = True  # We need to concoct a flag that determines whether all equipment was matched...
                # The prompt hack isn't doing it job in that regard
                if self.is_headless:
                    output_api_feed('equipment', (self.dict))
            else:
                magentaprint("match.group('slot').lower() is " + match.group('slot').lower() + " and is not in " + str(self.dict.keys()))
        elif r in R.you_arent_wearing_anything:
            self.reset()
        elif r in R.prompt:
            self.prompt_flag = True
        else:
            magentaprint("Equipment: What regex was that: " + str(r))

        super().notify_success_fail_or_error(r, match)

    def notify_of_buffer_completion(self):
        # MudReaderHandler says it's done with the buffer
        if self.eq_flag and self.prompt_flag:
        # if self.eq_flag:
            #magentaprint("Equipment dict is " + str(self.dict))
            #magentaprint("Equipment dict is {\n" + '\n\t'.join([('{0}'.ljust(10)+': {1}').format(k, v) for k, v in self.dict.items()]))
            magentaprint("Equipment dict is {\n" + ''.join(['{0: <10}: {1}\n'.format(k, v) if v is not None else '' for k, v in self.dict.items()])+'}')
                #+ str(self.dict))
            # magentaprint("Equipment completed.")
            self.eq_flag = False
            self.prompt_flag = False
            # super().set_completion_flag()  # We are returning when we get the prompt since returning on R.eq is buggy.
            super().notify(None,None) # Sets completion flag
            # This is also why we separated Command.notify() into two methods (we don't want to set the completion flag on R.eq
            # like most other commands that don't have a similar bug.)
            # It's finicky - there's another issue when the prompt is sent with the eq text and gets registered before it,
            # so we need to wait for both flags.
            self.telnetHandler.write('')

    def execute(self, target=None):
        self.reset()
        super().execute(target)

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


# So when I first wrote this I had inventory calling get_equipment on you_hold
# Now we have this equipment object
# So let's subscribe to you hold
# No, we need a HOLD COMMAND
# Well, maybe
# Or maybe we get enough info from the string that came in
# We should have a hold command though... in general
# So let's have it be able to tell equipment that something happened


