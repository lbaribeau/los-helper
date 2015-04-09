you_have = ["You have (.+?)\."]

hastened = ["You feel yourself moving faster\."]
feel_slower = ["You feel slower\."]

please_wait = [r"Please wait (\d+) more seconds?\."]
please_wait2 = [r"Please wait (\d+):(\d+) more minutes"]

__numbers = "(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th|16th|17th|18th|19th)" 

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

aura = [r"You glow with a (.+?) aura\."]

cast = [
    r"You cast a (.+?) spell on (.+?)\.",
    r"(.+?) spell cast\.",
    r"You cast a (.+?) spell\.",
    aura[0]
]

cast_failure = [
    r"Your spell fails\.",
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