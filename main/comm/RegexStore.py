
prompt = ["\[(\d+) H (\d+) M\]: (You feel the benefits)?"]

you_have = ["You have (.+?)\."]

found_exit = [r"You found an exit: (.+?)\."]
search_fail = [r"You didn't find anything\."]

please_wait = [r"Please wait (\d+) more seconds?\."]
please_wait2 = [r"Please wait (\d+):(\d+) more minutes"]

__numbers = "(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th|16th|17th|18th|19th)" 
__numbers2 = "(?:(\d*1st|\d*2nd|\d*3rd|\d+th) )?"
__numbers3 = "(?P<nth>\d*1st|\d*2nd|\d*3rd|\d+th) "
__numbers_opt = "(?:" + __numbers3 + ")?"
__The_mob = "(?:The " + __numbers_opt + ")?(?P<mob>[\w ]+) "
__the_mob = "(?:the " + __numbers_opt + ")?(?P<mob>[\w ]+) "
__Numbers = "(:?(?P<N>An?|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen) )?"
# __mob_string = "(?P<mob_string>[\w ]+)"  # We don't need this unless there are commas.
#s_numbered=" ?([\d]*?1st|[\d]*?2nd|[\d]*?3rd|[\d]*th)? ?"

# Combat / Mobs
# mob_died = ["Your attack overwhelms (?:the " + __numbers_opt + ")?(?P<mob>.+?) and (s?he|it) collapses!"]
# # it_fled = ["The (" + numbers + " )?(?P<mob_name>.+?) flees to the (.+?)\."]
# # mob_fled = ["(?:The ?(" + __numbers + " )?)?(?P<mob_name>.+?) flees to the (?P<exit>.+?)\."] 
# mob_fled = ["(?:The " + __numbers_opt + ")?(?P<mob>.+?) flees to the (?P<exit>.+?)\."] 
# mob_defeated = ["Your enemy, (?:the " + __numbers_opt + ")?(?P<mob>.+?) has been defeated\."]
# mob_wandered = ["(?:The " + __numbers_opt + ")?(?P<mob>.+?) just wandered to the (?P<exit>.+?)\."
mob_died = ["Your attack overwhelms " + __the_mob + "and (?:s?he|it) collapses!"]
# it_fled = ["The (" + numbers + " )?(?P<mob_name>.+?) flees to the (.+?)\."]
# mob_fled = ["(?:The ?(" + __numbers + " )?)?(?P<mob_name>.+?) flees to the (?P<exit>.+?)\."] 
mob_fled = [__The_mob + "flees to the (?P<exit>[\w ]+)\."] 
mob_defeated = ["Your enemy, " + __the_mob + "has been defeated\."]
mob_wandered = [__The_mob + "just wandered to the (?P<exit>[\w ]+)\."]
# mob_left = ["The (:?(?P<nth>\d*1st|\d*2nd|\d*3rd|\d+th) )?(?P<mob>.+?) just wandered away\."
mob_left = [__The_mob + " just wandered away\."]
# mob_arrived = ["An? (?P<mob>.+?) just arrived\."]
# mob_arrived = [__Numbers + "(?P<mob>[\w ]+?) just arrived\."]
mob_arrived = ["(?P<mobs>[\w ]+?) just arrived\."]
# mob_joins1 = ["the" + s_numbered + " (.+?) joins in the fight!"]
# Lower case 't' grammar error
mob_joined1 = [__the_mob + "joins in the fight!"]  # A mob standing there joins
mob_joined2 = [__the_mob + "decides to join in on the fight!"]  # A mob wanders in and joins
mob_attacked = [
    # "The" + s_numbered + " (.+?) punches you for (.+?) damage\.",
    __The_mob + "punches you for (.+?) damage\.",
    __The_mob + "throws a wild punch at you, but it misses\.",
    __The_mob + "kicks you for (\d+) damage\.",
    __The_mob + "kicks at you, but fails to hurt you\.",
    __The_mob + "grabs you and gouges you for (\d+) damage\.",
    __The_mob + "tries to grab you, but you break free of (his|her|its) grasp\.",
    __The_mob + "tries to gouge you, but you shake (him|her|it) off\.",
    __The_mob + "lashes out and thumps you for (\d+) damage\.",
    __The_mob + "lashes out at you, but misses\.",               
    __The_mob + "painfully head-butts you for (\d+) damage\.",
    __The_mob + "casts a (.+?) on you for (\d+) damage\."
    # __The_mob + "casts a (.+?) at you for (\d+) damage\."  # I don't think 'at' ever occurs
] 

# Go and Cartography
#           .=\n\r   EAT JUNK DATA (death,loginprompts,hptick)              Title           Description               Exit list             Players / Mobs / Signs / Items (optional)
area = ["(?s)(?:(?:.+?Stone\.\n\r|.+?healed\.\n\r|.+?\]:\s+?)\n\r)?([A-Za-z].+?)\n\r\n\r(?:(.+?)\n\r)?(Obvious exits: .+?\.)\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?"]
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
too_dark = ["It's too dark to see\."]
# the = "?(?:The |the )?" #named mobs have no "The/the"
you_see_mob = ["You see (?:[Tt]he )?" + __numbers2 + "(.+?)\.\n\r(.+?)\n\r(.+?)\n\r(.+?(?:\.|!))"]
mob_aura = ["(?:The " + __numbers2 + ")?(.+?) glows with a (.+?) aura\."]
not_here = ["You don't see that here\."]
loot_blocked = ["(?:The " + __numbers2 + ")?(.+?) won't let you take anything\."] #The spiv won't let you take anything.
teleported = ["### (.+?)'s body is teleported away to be healed\."]
store_list = ["You may buy:\n((?:.+\n?)*)"]
# store_item_list = "(?:[\s]*)(?:A |An |Some )?(.+?)(?:[\s]*)(?:(\(.\))?(?:[\s]*))?Cost: ([\d]*)" #well do a re.findall on the list above to iterate through, don't add this to the array below

open_success = ["You open the (.+?)\."]
already_open = ["It's already open\."]
open_what = ["Open what\?"]

# Skills
hastened = ["You feel yourself moving faster\."]
# haste_success = [hastened[0], already_hastened[0]]
haste_fail = ["Your attempt to hasten failed\."]
feel_slower = ["You feel slower\."]
already_hastened = ["You're already hastened\."]

prayers_answered = [r"You feel extremely pious\."]
not_answered = [r"Your prayers were not answered\."]
feel_less_pious = [r"You feel less pious\."]
already_prayed = [r"You've already prayed\."]

skin_thickening = [r"You feel your skin thickening and hardening\."]
barkskin_failed = [r"Your attempt to invoke barkskin failed\."]
skin_softens = [r"Your skin softens\."]
already_hardened = [r"Your skin is already hardened\."]

red_mist = [r"A red mist coats your vision, your heart pounds harder \. \. \."]
berserk_fail = [r"You fail to work yourself into a frenzy\."]
red_mist_fades = [r"The red mist fades from your sight\."]  # Neato dark blue colored text
already_berserk = [r"You're already berserk!"]

meditate = [r"You feel at one with universe\."]
not_at_peace = [r"Your spirit is not at peace\."]

aesters_tears = ["Your music rejuvenates everyone in the room\."]
dance_of_the_cobra = [r"he Dance of the Snake ends"]
dance_of_the_cobra_fail = [r"he Dance of the Snake has"]
dance_whom = [r"Sing the Dance to whom\?"]
turn = [r"You turned the (.+?) for (.+?) damage\."]
turn_fail = [r"You failed to turn the (.+?)\."]
turn_living_target = [r"You may only turn the unliving."]
turn_whom = [r"Turn whom\?"]
touch = [r"You touched the (.+?) for (.+?) damage\."]
touch_fail = [r"You failed to harm the (.+?)\."]
touch_whom = [r"Touch whom\?"]
wither = [r" the (.+?) for (.+?) damage\."]  # TODO: Obviously needs work
wither_fail = [r"Your withering touch did not hurt the ([\w ]+)\."]
wither_whom = [r"Wither whom\?"]
bash = [r"You bash the (.+?), confusing them\."]
bash_fail = [r"You failed to bash it\."]
bash_whom = [r"Bash whom\?"]
circle = [r"You circle the (.+?)\."]
circle_fail = [r"You failed to circle it\."]
circle_whom = [r"Circle whom\?"]

# Kill / Cast
bad_k_target = [
        r"You don't see that here\.",
        r"Attack what\?"
]
attack_hit = [
        "(?s)You swing with your .+?, hacking (?:the )?(" + __numbers + " )?(.+?)\s+for\s+\d+\s+damage\.",
        "(?s)You slice (?:the )?(" + __numbers + " )?(.+?) for \d+\s+damage\s+with\s+your\s+.+?\.",
        "You slash at (?:the )?(" + __numbers + " )?(.+?) and hit for \d+ damage\.",

        "You chop at (?:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "(?s)You stab (?:the )?(" + __numbers + " )?(.+?) with your .+?,\s+causing\s+\d+\s+damage",
        "You lunge at (?:the )?(" + __numbers + " )?(.+?), striking for \d+ damage\.",

        "You lash out and thump (?:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "You punch (?:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "You kick (?:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "You head-butt (?:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "You grab (?:the )?(" + __numbers + " )?(.+?) and gouge (him|her|it) for \d+\s+damage\.",

        "(?s)You smash your .+? into (?:the )?(" + __numbers + " )?(.+?),\s+causing\s+\d+\s+damage\.",
        "You heave your .+? at (?:the )?(" + __numbers + " )?(.+?),\s+smashing\s+(him|her|it)\s+for\s+\d+\s+damage\.",
        "You bludgeon (?:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",

        "You lunge at (?:the )?(" + __numbers + " )?(.+?), hitting them for \d+ damage\.",
        "You swing your .+?, striking for \d+ damage\.",
        "(?s)You sweep (?:the )?(" + __numbers + " )?(.+?) with your .+?\s+for\s+\d+\s+damage\.",

        "Your missile slams into (?:the )?(" + __numbers + " )?(.+?) for \d+ damage\.",
        "(?s)You attack (?:the )?(" + __numbers + " )?(.+?) with your .+?,\s+striking\s+for\s+\d+\s+damage\.",
        "You use your .+? to strike (?:the )?(" + __numbers + " )?(.+?)\s+for\s+\d+\s+damage\."
]
attack_miss = [
        "You hack with your .+?, but your blow swings wide of the mark\.",
        "You slice your .+? at (?:the )?(" + __numbers + " )?(.+?),\s+but\s+miss\.",
        "You slash at (?:the )?(" + __numbers + " )?(.+?), but miss\.",

        "You chop at (?:the )?(" + __numbers + " )?(.+?) but fail to hit them\.",
        "(?s)You try to stab (?:the )?(" + __numbers + " )?(.+?) with your .+?,\s+but\s+miss\.",
        "You lunge wildly at (?:the )?(" + __numbers + " )?(.+?) but mistime\s+the\s+strike\.",

        "You lash out at (?:the )?(" + __numbers + " )?(.+?), but miss\.",
        "You swing a wild punch at (?:the )?(" + __numbers + " )?(.+?), but it misses\.",
        "You kick at (?:the )?(" + __numbers + " )?(.+?), but fail to hurt them\.",
        "You grab at (?:the )?(" + __numbers + " )?(.+?), but (s?he|it) escapes your grasp\.",
        "You try to gouge (?:the )?(" + __numbers + " )?(.+?), but can't get a good grip\.",

        "(?s)You swing your .+? at (?:the )?(" + __numbers + " )?(.+?),\s+but\s+miss\.",
        "You heave your .+? in a wide arc, but fail to\s+hit\s+anything\.",
        "You try to bludgeon (?:the )?(" + __numbers + " )?(.+?), but miss\.",

        "You lunge at (?:the )?(" + __numbers + " )?(.+?), but you miss\.",
        "Your .+? swings, but fails to connect\.",
        "(?s)You sweep at (?:the )?(" + __numbers + " )?(.+?) with your .+?,\s+but\s+miss\.",

        "Your missile arcs towards (?:the )?(" + __numbers + " )?(.+?), but fails\s+to\s+hit\s+them\.",
        "(?s)You attack (?:the )?(" + __numbers + " )?(.+?) with your .+?,\s+but\s+miss\.",
        "(?s)You use your .+?, but nothing hits (?:the )?(" + __numbers + " )?(.+?)\."
]

aura = [
    r"You glow with a (.+?) aura\.", 
    r"The (.+?) glows with a (.+?) aura\."
]

cast = [
    r"You cast a (.+?) spell on (.+?)\.",
    r"(.+?) spell cast\.",
    r"You cast a (.+?) spell\."
]
cast_failure = [
    r"Your spell fails\."
]
no_mana = [
    r"You cannot meet the casting cost!"
]
bad_target_or_spell = [
    r"That spell does not exist\.",
    r"You don't know that spell\.",
    r"Spell name is not unique\.",
    r"Cast what\?",
    r"Cast at whom\?" 
]
not_here = [
    "They are not here\."
]
spells = [(
    r"\n\r"
    r"/=== Combat Spells ======================================================\\\s+"

    # r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    # r"\|(?P<none>\s+none\s+\|)\s*?\n\r"
    r"\|\s(?:\s+none\s+\|)|(?:Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
    # r"\|\s(Level Earth        Wind         Fire         Water        Astral       \|\s+\|   1(?P<black1>.+?)\|\s+\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
    # r"\|\s(  1(?P<black1>.+?)\|\s+\|\s+\|   2(?P<black2>.+?)\|\s+\|   3(?P<black3>.+?)\|\s+\|   4(?P<black4>.+?)\|\s+\|   5(?P<black5>.+?)\|)\s+"
    r"/================== Healing and Protection ==============================\\\s+"
    # r"\|   1(?P<black1>.+?)\|\s+"  # . can match spaces, and \s can match newlines
    # r"\|   2(?P<black2>.+?)\|\s+"
    # r"\|   3(?P<black3>.+?)\|\s+"
    # r"\|   4(?P<black4>.+?)\|\s+"
    # r"\|   5(?P<black5>.+?)\|\s+"
    # A regex without 1-5 specified and done with a quantifier could work if we don't put 
    # .+ and \s+ next to eachother, like this (maybe) (same with \s and \n/\r):
    # r"(?P<black>(?:\|.+?\|\s*?)+)"  erhm except I think, we can't use | as the anchor now, 
    # and same with newline, we'd have to use the Astral    | and the /===== as the anchors 
    # and match everything in between.  Spells.py would need to deal with the grouped '|'s.
    # r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    r"\|(?P<white>.+?)\|\s+"
    r"(?:\|(?P<white2>.+?)\|\s+)?"
    # r"(?:\|(?P<white3>.+?)\|\s+)?"
    r"/======================================= Miscellaneous ==================\\\s+"
    # r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    r"\|(?P<misc>.+?)\|\s+"
    r"(?:\|(?P<misc2>.+?)\|\s+)?"
    # r"(?:\|(?P<misc3>.+?)\|\s+)?"
    r"/===================================================== Running Spells ===\\\s+"
    # r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    r"\|(?P<buffs>.+?)\|\s+"
    r"(?:\|(?P<buffs2>.+?)\|\s+)?"
    # r"(?:\|(?P<buffs3>.+?)\|\s+)?"
    # r"\\========================================================================/\s*\n\r"
    r"\\="
)]
# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s*\n\r"
#     r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/================== Healing and Protection ==============================\\\s*\n\r"
#     r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/======================================= Miscellaneous ==================\\\s*\n\r"
#     r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/===================================================== Running Spells ===\\\s*\n\r"
#     r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\\========================================================================/\s*\n\r"
# )]
# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     # r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<none>\s+none\s+\|)\s*?\n\r"
#     r"\|\s+none\s+\|\s+"
#     r"/================== Healing"
# ),(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s+"
#     r"\| Level Earth        Wind         Fire         Water        Astral       \|\s+"
#     # r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\|   1(?P<black1>.+?)\|\s+"  # . can match spaces, and \s can match newlines
#     r"\|   2(?P<black2>.+?)\|\s+"
#     r"\|   3(?P<black3>.+?)\|\s+"
#     r"\|   4(?P<black4>.+?)\|\s+"
#     r"\|   5(?P<black5>.+?)\|\s+"
#     r"/================== Healing"
#     # A regex without 1-5 specified and done with a quantifier could work if we don't put 
#     # .+ and \s+ next to eachother, like this (maybe) (same with \s and \n/\r):
#     # r"(?P<black>(?:\|.+?\|\s*?)+)"  erhm except I think, we can't use | as the anchor now, 
#     # and same with newline, we'd have to use the Astral    | and the /===== as the anchors 
#     # and match everything in between.  Spells.py would need to deal with the grouped '|'s.
# ),(
#     # r"/================== Healing and Protection ==============================\\\s*\n\r"
#     r"/================== Healing and Protection ==============================\\\s+"
#     r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<white>.+?)\|\s+"
#     # r"(\|(?P<white2>.+?)\|\s+)?"
#     # r"(\|(?P<white3>.+?)\|\s+)?"
#     r"/======================================= Misc"
# ),(
#     r"/======================================= Miscellaneous ==================\\\s*\n\r"
#     r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<misc>.+?)\|\s+"
#     # r"(\|(?P<misc2>.+?)\|\s+)?"
#     # r"(\|(?P<misc3>.+?)\|\s+)?"
#     r"/===================================================== Running"
# ),(
#     r"= Running Spells ===\\\s*\n\r"
#     r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     # r"\|(?P<buffs>.+?)\|\s+"
#     # r"(\|(?P<buffs2>.+?)\|\s+)?"
#     # r"(\|(?P<buffs3>.+?)\|\s+)?"
#     r"\\========================================================================/\s*\n\r"
# )]
# spells = [(
#     r"\n\r"
#     r"/=== Combat Spells ======================================================\\\s*\n\r"
#     r"(?P<black>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/================== Healing and Protection ==============================\\\s*\n\r"
# )]
# spells2 = [(
#     r"/================== Healing and Protection ==============================\\\s*\n\r"
#     r"(?P<white>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/======================================= Miscellaneous ==================\\\s*\n\r"
# )]
# spells3 = [(
#     r"/======================================= Miscellaneous ==================\\\s*\n\r"
#     r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"/===================================================== Running Spells ===\\\s*\n\r"
# )]
# spells4 = [(
#     r"/===================================================== Running Spells ===\\\s*\n\r"
#     r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
#     r"\\========================================================================/\s*\n\r"
# )]
    # r"\|\s+(?P<black>.+?)+\s+\|\s*?\n\r"
    # r"\|\s+(?P<white>.+?)+\s+\|\s*?\n\r"
    # r"\|\s+(?P<misc>.+?)+\s+\|\s*?\n\r"
    # r"\|\s+(?P<buffs>.+?)+\s+\|\s*?\n\r"
    # r"/=== Combat Spells ======================================================\\\s*\n\r"
    # r"\|\s+(?P<black>.+?)\s+\|\s*?\n\r"
    # r"/================== Healing and Protection ==============================\\\s*\n\r"
    # r"\|\s+(?P<white>.+?)\s+\|\s*?\n\r"
    # r"/======================================= Miscellaneous ==================\\\s*\n\r"
    # r"\|\s+(?P<misc>.+?)\s+\|\s*?\n\r"
    # r"/===================================================== Running Spells ===\\\s*\n\r"
    # r"\|\s+(?P<buffs>.+?)\s+\|\s*?\n\r"
    # r"\\========================================================================/\s*\n\r"

goodbye = ["Goodbye! Come back soon\."]
# game_shutdown = ['### Game shutdown in (\d+) seconds\.']
# game_shutdown2 = ["### Game backup shutdown in \d:\d\d minutes\."]
# game_shutdown3 = ["### Shutting down now\."]
# Equipment
you_arent_wearing_anything = [r"You aren't wearing anything\."]

# on_body = [r"On body:   (.+?)\n\r"]
# on_arms = [r"On arms:   (.+?)\n\r"]
# on_legs = [r"On legs:   (.+?)\n\r"]
# on_neck = [r"On neck:   (.+?)\n\r(On neck:   (?P<second_neck>.+?)\n\r)?"]
# on_hands= [r"On hands:  (.+?)\n\r"]
# on_head = [r"On head:   (.+?)\n\r"]
# on_feet = [r"On feet:   (.+?)\n\r"]
# on_finger = [r"On finger: (.+?)\n\r"]
# shield  = [r"Shield:    (.+?)\n\r"]
# wielded = [r"Wielded:   (.+?)\n\r"]
# seconded= [r"Seconded:  (.+?)\n\r"]
# holding = [r"Holding:   (.+?)\n\r"]
eq = [r"(On body:   (?P<body>.+?)\n\r)?" \
      r"(On arms:   (?P<arms>.+?)\n\r)?" \
      r"(On legs:   (?P<legs>.+?)\n\r)?" \
      r"(On neck:   (?P<neck>.+?)\n\r)?" \
      r"(On neck:   (?P<second_neck>.+?)\n\r)?" \
      r"(On hands:   (?P<hands>.+?)\n\r)?" \
      r"(On head:   (?P<head>.+?)\n\r)?" \
      r"(On feet:   (?P<feet>.+?)\n\r)?" \
      r"(On finger: (?P<finger>.+?)){0,8}" \
      r"(Wielded:   (?P<weapon>.+?))?" \
      r"(Seconded:  (?P<seconded>.+?))?" \
      r"(Holding:   (?P<holding>.+?))"
]  # m.group('holding') returns None with no error if the holding group didn't occur.

# "The extreme nature of this place wracks your aura!""  (Bandit Hill)