
prompt = ["\[(\d+) H (\d+) M\]"]

you_have = ["You have (.+?)\."]

hastened = ["You feel yourself moving faster\."]
already_hastened = ["You're already hastened\."]
# haste_success = [hastened[0], already_hastened[0]]
haste_fail = ["Your attempt to hasten failed\."]
feel_slower = ["You feel slower\."]
aesters_tears = ["Your music rejuvenates everyone in the room\."]
dance_of_the_cobra = [r"he Dance of the Snake ends"]
dance_of_the_cobra_fail = [r"he Dance of the Snake has"]

please_wait = [r"Please wait (\d+) more seconds?\."]
please_wait2 = [r"Please wait (\d+):(\d+) more minutes"]

__numbers = "(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th|16th|17th|18th|19th)" 
__numbers2 = "(?:(\d*1st|\d*2nd|\d*3rd|\d+th) )?"

obvious_exits = [r"(?s)Obvious exits: (.+?)\.\n\r"]
go_where = [r"Go where\?"]
cant_go = [r"You can't go that way\."]
# blocked_path = ["(?:The " + __numbers2 + ")?(.+?) blocks your exit\."]  # Make the The optional is hard
blocked_path = ["(?:The )" + __numbers2 + "(?P<mob_name>.+?) blocks your exit\."]
open_first = ["You have to open it first\."]
no_exit = ["I don't see that exit\."]
class_prohibited = ["Your class prohibits you from entering there\."]
level_too_low = ["You must be at least level \d+ to go that way\."]
not_invited = ["You have not been invited in\."]
not_open_during_day = ["That exit is not open during the day\."]
not_open_during_night = ["That exit is closed for the night\."]
no_items_allowed = ["You cannot bring anything through that exit\."]
locked = ["It's locked\."]
no_right = ["You have not earned the right to pass this way!"]
in_tune = ["That way may only be taken by those in tune with the world!"]
not_authorized = ["You are not authorised to enter here\."]
cannot_force = ["You cannot force yourself to go through there\."]
# __go_failure = blocked_path + open_first + no_exit + class_prohibited + level_too_low + \
#     class_prohibited + level_too_low + not_invited + not_open_during_day + \
#     not_open_during_night + no_items_allowed + locked + no_right \
#     in_tune + not_authorized + cannot_force

open_success = ["You open the (.+?)\."]
already_open = ["It's already open\."]
open_what = ["Open what\?"]


goodbye = ["Goodbye! Come back soon\."]

mob_died = ["Your attack overwhelms (?:the (" + __numbers + " )?)?(.+?) and (s?he|it) collapses!"]
mob_fled = ["(:?The ?(" + __numbers + " )?)?(.+?) flees to the (.+?)\."] 

attack_error = [
        r"You don't see that here\.",
        r"Attack what\?"
]
attack_hit = [
        "(?s)You swing with your .+?, hacking (:the )?(" + __numbers + " )?(.+?)\s+for\s+\d+\s+damage\.",
        "(?s)You slice (:the )?(" + __numbers + " )?(.+?) for \d+\s+damage\s+with\s+your\s+.+?\.",
        "You slash at (:the )?(" + __numbers + " )?(.+?) and hit for \d+ damage\.",

        "You chop at (:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "(?s)You stab (:the )?(" + __numbers + " )?(.+?) with your .+?,\s+causing\s+\d+\s+damage",
        "You lunge at (:the )?(" + __numbers + " )?(.+?), striking for \d+ damage\.",

        "You lash out and thump (:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "You punch (:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "You kick (:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "You head-butt (:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "You grab (:the )?(" + __numbers + " )?(.+?) and gouge (him|her|it) for \d+\s+damage\.",

        "(?s)You smash your .+? into (:the )?(" + __numbers + " )?(.+?),\s+causing\s+\d+\s+damage\.",
        "You heave your .+? at (:the )?(" + __numbers + " )?(.+?),\s+smashing\s+(him|her|it)\s+for\s+\d+\s+damage\.",
        "You bludgeon (:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",

        "You lunge at (:the )?(" + __numbers + " )?(.+?), hitting them for \d+ damage\.",
        "You swing your .+?, striking for \d+ damage\.",
        "(?s)You sweep (:the )?(" + __numbers + " )?(.+?) with your .+?\s+for\s+\d+\s+damage\.",

        "Your missile slams into (:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "(?s)You attack (:the )?(" + __numbers + " )?(.+?) with your .+?,\s+striking\s+for\s+\d+\s+damage\.",
        "You use your .+? to strike (:the )?(" + __numbers + " )?(.+?)\s+for\s+\d+\s+damage\."
]
attack_miss = [
        "You hack with your .+?, but your blow swings wide of the mark\.",
        "You slice your .+? at (:the )?(" + __numbers + " )?(.+?),\s+but\s+miss\.",
        "You slash at (:the )?(" + __numbers + " )?(.+?), but miss\.",

        "You chop at (:the )?(" + __numbers + " )?(.+?) but fail to hit them\.",
        "(?s)You try to stab (:the )?(" + __numbers + " )?(.+?) with your .+?,\s+but\s+miss\.",
        "You lunge wildly at (:the )?(" + __numbers + " )?(.+?) but mistime\s+the\s+strike\.",

        "You lash out at (:the )?(" + __numbers + " )?(.+?), but miss\.",
        "You swing a wild punch at (:the )?(" + __numbers + " )?(.+?), but it misses\.",
        "You kick at (:the )?(" + __numbers + " )?(.+?), but fail to hurt them\.",
        "You grab at (:the )?(" + __numbers + " )?(.+?), but (s?he|it) escapes your grasp\.",
        "You try to gouge (:the )?(" + __numbers + " )?(.+?), but can't get a good grip\.",

        "(?s)You swing your .+? at (:the )?(" + __numbers + " )?(.+?),\s+but\s+miss\.",
        "You heave your .+? in a wide arc, but fail to\s+hit\s+anything\.",
        "You try to bludgeon (:the )?(" + __numbers + " )?(.+?), but miss\.",

        "You lunge at (:the )?(" + __numbers + " )?(.+?), but you miss\.",
        "Your .+? swings, but fails to connect\.",
        "(?s)You sweep at (:the )?(" + __numbers + " )?(.+?) with your .+?,\s+but\s+miss\.",

        "Your missile arcs towards (:the )?(" + __numbers + " )?(.+?), but fails\s+to\s+hit\s+them\.",
        "(?s)You attack (:the )?(" + __numbers + " )?(.+?) with your .+?,\s+but\s+miss\.",
        "(?s)You use your .+?, but nothing hits (:the )?(" + __numbers + " )?(.+?)\."
]

aura = [r"You glow with a (.+?) aura\.", r"The (.+?) glows with a (.+?) aura\."]

cast = [
    r"You cast a (.+?) spell on (.+?)\.",
    r"(.+?) spell cast\.",
    r"You cast a (.+?) spell\."
]
cast_failure = [
    r"Your spell fails\.",
]
no_mana = [
    r"You cannot meet the casting cost!"
]
cast_error = [
    r"That spell does not exist\.",
    r"You don't know that spell\.",
    r"Spell name is not unique\.",
    r"Cast what\?",
    r"They are not here\.",
    r"Cast at whom\?" 
]

# "The extreme nature of this place wracks your aura!""  (Bandit Hill)