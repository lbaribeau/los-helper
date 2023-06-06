
# https://docs.python.org/3/library/re.html
# "r" (raw) strings mean the slash is a real slash becoming a regex escape character and not a python literal character is next.
# (?:...) means that the substring doesn't end up available as a match
# - grouping parentheses that don't save what they match

prompt            = [r"\[(\d+) H (\d+) M\]: (You feel the benefits of resting\.)?"]
__item            = r"(?P<item>[A-Za-z0-9\-'\s\(\)\+]+)"
__items           = r"(?P<items>[A-Za-z0-9\-'\s,\(\)\+]+)"
__player          = r"(?P<player>[A-Za-z]+)"
you_have          = [r"You have: " + __items + r"\."]
wont_buy          = [r'The shopkeep says, "I won\'t buy that rubbish from you\."'] # Could get the prompt with the regex, so ^ might not match
wont_buy2         = [r"The shopkeep won't buy that from you\."]
sold              = [r"The shopkeep gives you (\d+) gold for " + __item + r'\.']
you_drop          = [r"You drop " + __items + r"\."]
disintegrates     = [r"(?:A|Some) " + __item + r" disintegrates\."]
gold_from_tip     = [r"You have (\d+) gold\."]
not_a_pawn_shop   = [r"^This is not a pawn shoppe\."]
you_now_have      = [r"^You now have (\d+) gold pieces\."]
not_empty         = [r"^It isn't empty!"]
you_wear          = [r"You wear " + __items + r"\."]
nothing_to_wear   = [r"^You have nothing you can wear\."]
# you_get         = [r"(?s)[^ ]You get (.+?)\.(?:\nYou now have (.+?) gold pieces\.)?"]
# you_get         = [r"[^ ]You get " + __items + r"\."]  # We don't want this to miss because getting can happen in combat - maybe it shouldn't
you_get           = [r"^(You weren't able to carry everything\.\n?\r?)?You get " + __items + r"\."]  
# False positives on "You get the vague..." ... hard to deal with in regex
# (\n and \r didn't match at the beginning, but ^ rules out "You get" in descriptions.)
# "... more than is assuring. You get the distinct feeling (newline) that the rangers are not winning...""
# Ok, to test go timouts, go to this bog troll area, and delete the ^ in you_get, and spam that area and all the areas 
# around it 30+ times
# We could miss a "You get" this way
# Eh now we don't match if you don't get everything because of the ^... so we put that in as an optional group, since we need the ^
you_remove        = [r"You removed? " + __items + r"\."]
nothing_to_remove = [r"^You aren't wearing anything that can be removed\.", r"^You aren't using that\."]
# you_wield       = [r"You wield (.+?)( in your off hand)?\."]
you_give          = [r"^You give " + __items + r" to " + __player + r"\."]
you_put_in_bag    = [r"^You put " + __items + r" in(:?to)? " + __item + r"\."]
gave_you          = [__player + r" gave " + __items + r" to you\."]
you_hold          = [r"^You hold " + __items + r"\."]
# weapon_breaks   = [r"Your (.+?) breaks and you have to remove it\."]
# weapon_shatters = [r"Your (.+?) shatters\."]
armour_breaks     = [r"Your " + __item + r" fell apart\."]

current_equipment = [r"You see " + __player + r" (?:the [A-Za-z'\-]+)\.\n?\r?(?:(?:.+?\.\n?\r?)+)?((?:.+?:.+\n?\r?)+)"]  
# doesn't work for 'eq' command ()... also it does trigger looking at another player!
no_inventory      = [r"You currently have no carried inventory\."]
#wearing           = [r"\n?\r?(?:On )?(.+?):[\s]*(?:a |an |some )"+__item+'\n\r']  # TODO: Redundant
#wearing           = [r"(?:On )?(.+?):[\s]*(?:a |an |some )"+__item+'\n\r']  # TODO: Redundant
# Ok this one (wearing) has some serious false positives... maybe fixed it... that first hook "On" can also be Shield and what else
#wearing           = [r"(On arms|On legs|On neck|On hands|On head|On feet|On face|On finger|Shield|Holding):[\s]+(?:a |an |some )"+__item+'\n\r']
# See one_equip
# Not sure that's even necessary (but I did write it to be more strict)
you_arent_wearing_anything = [r"You aren't wearing anything\."]

__exit           = r"(?P<exit>[A-Za-z ]+)"
found_exit       = [r"You found an exit: " + __exit + r"\."]
search_fail      = [r"You didn't find anything\."]
hide             = [r"You slip into the shadows unnoticed\.", r"You are already hiding\."]
hide_fail        = [r"You attempt to hide in the shadows\.$"]  # This occurs on success as well
prepare          = [r"You prepare yourself for traps\."]
already_prepared = [r"You've already prepared\."]

please_wait    = [r"Please wait (\d+) more seconds?\."]
please_wait2   = [r"Please wait (\d+):(\d+) more minutes"]

__numbers      = "(1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th|11th|12th|13th|14th|15th|16th|17th|18th|19th)" 
__numbers2     = "(?:(\d*1st|\d*2nd|\d*3rd|\d+th) )?"
__numbers3     = "(?P<nth>\d*1st|\d*2nd|\d*3rd|\d+th) "
__numbers_opt  = "(?:" + __numbers3 + ")?"
# __The_mob    = "(?:The " + __numbers_opt + ")?(?P<mob>[a-z '-]+) "
__Numbered_mob = r"(?P<numbered_mob>[A-Z](?:he " + __numbers_opt + ")?[a-z '-]+) "
# __The_mob    = "[A-Z](?:he " + __numbers_opt + ")?(?P<mob>[a-z '-]+) "
__the_mob      = r"(?:the " + __numbers_opt + ")?(?P<mob>[a-z '-]+) "
# The_mob2 won't try to match 1st/2nd with the regex.  Turns out it gets hairy accounting for that and The mobs and named mobs.
__The_mob2     = r"(P<mob>[A-Z][\w '-]+) "
# __the_mob2 = "(P<mob>[\w '-]+) "
__mob          = r"[a-z '-]+"
__the_mob2     = r"(P<mob>(?:[A-Z][a-z '-]+)|(?:the " + __numbers_opt + __mob + ")) "
# __3_possible_mob_strings = r"(P<mob1>[A-Z][a-z '-]+)|(P<mob2>The [A-Z][a-z '-]+)|(?:[Tt]he " + __numbers_opt + r"(P<mob3>([a-z '-]+))) "
# __3_possible_mob_strings = r"((?P<mob1>The [A-Z][a-z '-]+)|(?P<mob2>[A-Z][a-z '-]+)|(?:[Tt]he " + __numbers_opt + r"(?P<mob3>([a-z '-]+)))) "
# __3_possible_mob_strings = r"((?P<mob1>The [A-Z][a-z '-]+ )|(?P<mob2>([A-Z][a-z'-]+ )+)|(?:[Tt]he " + __numbers_opt + r"(?P<mob3>([a-z '-]+ ))))"  # Alaran problem... try prioritizing named mob last
# __3_possible_mob_strings = r"((?P<mob1>The [A-Z][a-z '-]+ )|(?:[Tt]he " + __numbers_opt + r"(?P<mob3>([a-z '-]+ ))|(?P<mob2>[A-Z][a-z'-]+ ([a-z'-]+ )*)))"  # Need 2nd capital letter (The General)
# __Three_possible_mob_strings = r"((?P<mob1>The [A-Z][a-z '-]+ )|(?:The " + __numbers_opt + r"(?P<mob2>([a-z '-]+ ))|(?P<mob3>([A-Z][a-z'-]+ )+)))"  # Still no good for Hef/Alaran (mob3)
# __Three_possible_mob_strings = r"((?P<mob1>The ([A-Z][a-z '-]+ )+)|(?:The " + __numbers_opt + r"(?P<mob2>([a-z '-]+ ))|(?P<mob3>[A-Z][A-Za-z '-]+ )))"
# __Three_possible_mob_strings = r"((?P<mob1>The ([A-Z][a-z '-]+ )+)|(?:The " + __numbers_opt + r"((?P<mob2>[a-z '-]+) ))|(?P<mob3>[A-Z][A-Za-z '-]+ ))"
__Three_possible_mob_strings = r"(?P<whole_mob_name>((?P<mob1>The( [A-Z][a-z'-]+)+)|(?:The " + __numbers_opt + r"(?P<mob2>[a-z '-]+))|(?P<mob3>[A-Z][A-Za-z '-]+)))"
# __three_possible_mob_strings = r"((?P<mob1>The ([A-Z][a-z '-]+ )+)|(?:the " + __numbers_opt + r"(?P<mob2>([a-z '-]+ ))|(?P<mob3>[A-Z][A-Za-z '-]+ )))"
# __three_possible_mob_strings = r"((?P<mob1>The ([A-Z][a-z '-]+ )+)|(?:the " + __numbers_opt + r"((?P<mob2>[a-z '-]+) ))|(?P<mob3>[A-Z][A-Za-z '-]+ ))"
# __three_possible_mob_strings = r"(?:the " + __numbers_opt + r"((?P<mob1>(?P<mob3>(?P<mob2>[a-z '-]+))) ))"  # Simplefied mob2 only, you_attack not working
# __three_possible_mob_strings = "(?:the ((?P<mob1>(?P<mob3>(?P<mob2>[a-z '-]+))) ))"
# __three_possible_mob_strings = "(?:the ((?P<mob1>(?P<mob3>(?P<mob2>.+?))) ))"
# __three_possible_mob_strings = "(?:the ((?P<mob1>(?P<mob3>(?P<mob2>.+?))) ))"
__three_possible_mob_strings = r"((?P<mob1>The( [A-Z][a-z'-]+)+)|(?:the " + __numbers_opt + r"(?P<mob2>[a-z '-]+))|(?P<mob3>[A-Z][A-Za-z '-]+))"
# Separating The and the eliminates mob2 from matching 'the' in Alaran/Hef
__Numbers = r"(:?(?P<N>An?|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|Eleven|Twelve|Thirteen) )?"
# __mob_string = "(?P<mob_string>[\w ]+)"  # We don't need this unless there are commas.
#s_numbered=" ?([\d]*?1st|[\d]*?2nd|[\d]*?3rd|[\d]*th)? ?"

# Combat / Mobs
# you_attack = ["You attack " + __the_mob + "\."]
# you_attack = ["You attack the (?P<mob2>.+?)\."]
you_attack = ["You attack " + __three_possible_mob_strings + "\."]
# you_attack = ["You attack (.+?)\."]  # no space!
mob_aggro = [__Three_possible_mob_strings + " attacks you\."]  # TODO: alert here(?)
# mob_wandered = ["(?:The " + __numbers_opt + ")?(?P<mob>.+?) just wandered to the (?P<exit>.+?)\."
mob_wandered = [__Three_possible_mob_strings + r" just wandered to the (?P<exit>[a-z ]+)\."]
# mob_left = ["The (:?(?P<nth>\d*1st|\d*2nd|\d*3rd|\d+th) )?(?P<mob>.+?) just wandered away\."
mob_left = [__Three_possible_mob_strings + " just wandered away\."]
# mob_arrived = ["An? (?P<mob>.+?) just arrived\."]
# mob_arrived = [__Numbers + "(?P<mob>[\w ]+?) just arrived\."]
# mob_arrived = ["(?P<mobs>[\w -']+?) just arrived\."]
# mob_arrived = [__The_mob2 + "(?P<mobs>[a-z]+ [a-z '-]+?) just arrived\."]
mob_arrived = [r"(?P<mobs>[A-Z][a-z]* [a-z '-]+?) just arrived\."]  # no 1st/2nd numbers in arrived, but Two/Three is possible
# mob_arrived = [__3_possible_mob_strings + r" just arrived\."]
# mob_joins1 = ["the" + s_numbered + " (.+?) joins in the fight!"q

# Lower case 't' grammar error
# mob_joined1 = [__the_mob + "joins in the fight!"]  # A mob standing there joins
mob_joined1 = [__three_possible_mob_strings + " joins in the fight!"]  # A mob standing there joins
mob_joined2 = [__three_possible_mob_strings + " decides to join in on the fight!"]  # A mob wanders in and joins
mob_attacked = [  # TODO: do any mobs wield weapons? (different text)
    # "The" + s_numbered + " (.+?) punches you for (.+?) damage\.",
    __Three_possible_mob_strings + r" punches you for (?P<d>\d+) damage\.",
    __Three_possible_mob_strings + r" throws a wild punch at you, but it misses\.",
    __Three_possible_mob_strings + r" kicks you for (?P<d>\d+) damage\.",
    __Three_possible_mob_strings + r" kicks at you, but fails to hurt you\.",
    __Three_possible_mob_strings + r" grabs you and gouges you for (?P<d>\d+) damage\.",
    __Three_possible_mob_strings + r" tries to gouge you, but you shake (him|her|it) off\.",
    __Three_possible_mob_strings + r" painfully head-butts you for (?P<d>\d+) damage\.",
    __Three_possible_mob_strings + r" tries to grab you, but you break free of (his|her|its) grasp\.",
    __Three_possible_mob_strings + r" lashes out and thumps you for (?P<d>\d+) damage\.",
    __Three_possible_mob_strings + r" lashes out at you, but misses\.",
    __Three_possible_mob_strings + r" tramples you for (?P<d>\d+) damage\.",
    __Three_possible_mob_strings + r" tries to trample you\.",
    __Three_possible_mob_strings + r" bites you for (?P<d>\d+) damage\.",
    __Three_possible_mob_strings + r" tries to bite you\.",
    __Three_possible_mob_strings + r" kicks you for (?P<d>\d+) damage\.",
    __Three_possible_mob_strings + r" kicks at you, but fails to connect\.",
    __Three_possible_mob_strings + r" charges at you and butts for (?P<d>\d+) damage\.",  # TODO - missing no dmg version of this one
    __Three_possible_mob_strings + r" casts a [A-Za-z\-]+ spell on you for (?P<d>\d+) damage\."
]

# mob_says = __Three_possible_mob_strings + r" says to you, \"(.+?)\"\.?$"

# mob_died = ["Your attack overwhelms (?:the " + __numbers_opt + ")?(?P<mob>.+?) and (s?he|it) collapses!"]
# # it_fled = ["The (" + numbers + " )?(?P<mob_name>.+?) flees to the (.+?)\."]
# # mob_fled = ["(?:The ?(" + __numbers + " )?)?(?P<mob_name>.+?) flees to the (?P<exit>.+?)\."] 
# mob_fled = ["(?:The " + __numbers_opt + ")?(?P<mob>.+?) flees to the (?P<exit>.+?)\."] 
# mob_defeated = ["Your enemy, (?:the " + __numbers_opt + ")?(?P<mob>.+?) has been defeated\."]
mob_died = [r"Your attack overwhelms " + __three_possible_mob_strings + " and (?:s?he|it) collapses!"]
# it_fled = ["The (" + numbers + " )?(?P<mob_name>.+?) flees to the (.+?)\."]
# mob_fled = ["(?:The ?(" + __numbers + " )?)?(?P<mob_name>.+?) flees to the (?P<exit>.+?)\."] 
mob_fled = [__Three_possible_mob_strings + r" flees to the (?P<exit>[a-z ]+)\."] 
mob_defeated = [r"Your enemy, " + __three_possible_mob_strings + r" has been defeated\."]
you_died = [r"You are overwhelmed by " + __three_possible_mob_strings + r"'s attack and you collapse!"]
loot_blocked = [__Three_possible_mob_strings + r" won't let you take anything\."]
nothing_here = [r"There's nothing here\."]

# Go and Cartography
#           .=\n\r   EAT JUNK DATA (death,loginprompts,hptick)              Title           Description               Exit list             Players / Mobs / Signs / Items (optional)
area                  = ["(?:You run like a chicken\.\n\r\n\r)?(?s)(?:(?:.+?Stone\.\n\r|.+?healed\.\n\r|.+?\]:\s+?)\n\r)?([A-Za-z].+?)\n\r\n\r(?:(.+?)\n\r)?(Obvious exits: .+?\.)\n?\r?(?:You see (?:Cer.+?)\n?\r?)?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?(You see .+?\.)?\n?\r?"]
obvious_exits         = [r"(?s)Obvious exits: ([A-Za-z\s,]+)\.\n\r"]
go_where              = [r"Go where\?"]
cant_go               = [r"You can't go that way\."]
# blocked_path        = ["(?:The " + __numbers2 + ")?(.+?) blocks your exit\."]  # Make the The optional is hard
# blocked_path        = [r"(?:The )" + __numbers2 + r"(?P<mob_name>.+?) blocks your exit\."]
blocked_path          = [__Three_possible_mob_strings + r" blocks your exit\."]
open_first            = [r"You have to open it first\."]
no_exit               = [r"I don't see that exit\."]
class_prohibited      = [r"Your class prohibits you from entering there\."]
level_too_low         = [r"You must be at least level (\d+) to go that way\."]
level_too_high        = [r"Only players under level (\d+) may go that way\."]
not_invited           = [r"You have not been invited in\."]
not_open_during_day   = [r"That exit is not open during the day\."]
not_open_during_night = [r"That exit is closed for the night\."]
no_items_allowed      = [r"You cannot bring anything through that exit\."]
locked                = [r"It's locked\."]
no_right              = [r"You have not earned the right to pass this way!"]
in_tune               = [r"That way may only be taken by those in tune with the world!"]
not_authorized        = [r"You are not authorised to enter here\."]
cannot_force          = [r"You cannot force yourself to go through there\."]
washroom = [
    r"Sorry, only males are allowed to go there\.",
    r"Sorry, only females are allowed to go there\."]
cliff = [r"You fell and hurt yourself for (\d+) damage\."]
# __go_failure = blocked_path + open_first + no_exit + class_prohibited + level_too_low + \
#     class_prohibited + level_too_low + not_invited + not_open_during_day + \
#     not_open_during_night + no_items_allowed + locked + no_right \
#     in_tune + not_authorized + cannot_force
too_dark = [r"It's too dark to see\."]
# the = "?(?:The |the )?" #named mobs have no "The/the"
#you_see_mob = ["You see (?:[Tt]he )?" + __numbers2 + "(.+?)\.\n\r(.+?)\n\r(.+?)\n\r(.+?(?:\.|!))"]  
# Not to be confused with "You see a flock of birds take off to the north of you." ideally
you_see_mob = ["Obvious exits: (?:.+?)\.\n\rYou see (?:[Tt]he )?" + __numbers2 + "(.+?)\.\n\r(.+?)\n\r(.+?)\n\r(.+?(?:\.|!))"]  
# So that will match less, I think it's correct, it could be confused with players or items if items are alone.
# mob_aura = ["(?:The " + __numbers2 + ")?(.+?) glows with a (.+?) aura\."]
__aura = r"(?P<aura>[A-Za-z ]+)"
mob_aura = [__Three_possible_mob_strings + r" glows with a " + __aura + r" aura\."]
not_here = [r"You don't see that here\."]
# loot_blocked = [r"(?:The " + __numbers2 + ")?(.+?) won't let you take anything\."] #The spiv won't let you take anything.
loot_dropped = [__Three_possible_mob_strings + r" was carrying: "+__items+"\."]
loot_blocked = [__Three_possible_mob_strings + r"won't let you take anything\."] #The spiv won't let you take anything.
teleported = [r"### " + __player + r"'s body is teleported away to be healed\."]

backup_shutdown = [r'### Game backup shutdown in (.+?) minutes\.']

#You see a large pit ahead, but cannot stop in time!
#You fall down into the pit!
interstitial = [r"You fall down into the pit!"]


# store_list = ["You may buy:\n\r((?:.+\n?)*)"]
# store_list = ["You may buy:\s+(A |An |Some)("]
#     ((?:.+\n?)*)"]
# store_list = [r"You may buy:(\s+([A-Za-z']+ )+\s+(\([sml]\)\s+)?Cost: \d+)+"]  # Too liberal with \s+ and can't anchor to the end newlines
# store_list = [r"You may buy:(\n\r +(?P<item>[A-Za-z']+ )+\s+(\([sml]\)\s+)?Cost: \d+)+"]  # Can't get at the items like this... stopped halfway through
# store_list = [r"You may buy: *[\n\r]{2}(?P<store_list>.+?[\n\r]{2})+[\n\r]{2}"]  # Match until two newlines which indicate the end of the store list
# store_list = [r"You may buy: *[\n\r]{2}(?P<store_list>.+?[\n\r]{2})+[\n\r]{2}"]  # Wrong grouping only returns last line
store_list = [r"You may buy: *[\n\r]{2}(?P<store_list>(.+?[\n\r]{2})+)[\n\r]{2}"]  
# store_list = [r"You may buy:"]
# store_item_list = "(?:[\s]*)(?:A |An |Some )?(.+?)(?:[\s]*)(?:(\(.\))?(?:[\s]*))?Cost: ([\d]*)" #well do a re.findall on the list above to iterate through, don't add this to the array below

open_success = [r"You open the " + __exit + r"\."]
already_open = ["It's already open\."]
open_what    = [r"Open what\?"]

# Skills
hastened                = [r"You feel yourself moving faster\."]
# haste_success         = [hastened[0], already_hastened[0]]
haste_fail              = [r"Your attempt to hasten failed\."]
feel_slower             = ["You feel slower\."]
already_hastened        = ["You're already hastened\."]
prayers_answered        = [r"You feel extremely pious\."]
not_answered            = [r"Your prayers were not answered\."]
feel_less_pious         = [r"You feel less pious\."]
already_prayed          = [r"You've already prayed\."]
skin_thickening         = [r"You feel your skin thickening and hardening\."]
barkskin_failed         = [r"Your attempt to invoke barkskin failed\."]
skin_softens            = [r"Your skin softens\."]
already_hardened        = [r"Your skin is already hardened\."]
red_mist                = [r"A red mist coats your vision, your heart pounds harder \. \. \."]
berserk_fail            = [r"You fail to work yourself into a frenzy\."]
red_mist_fades          = [r"The red mist fades from your sight\."]  # Neato dark blue colored text
already_berserk         = [r"You're already berserk!"]
meditate                = [r"You feel at one with the universe\."]
not_at_peace            = [r"Your spirit is not at peace\."]
aesters_tears           = ["Your music rejuvenates everyone in the room\."]
dance_of_the_cobra      = [r"he Dance of the Snake ends"]
dance_of_the_cobra_fail = [r"he Dance of the Snake has"]
dance_whom              = [r"Sing the Dance to whom\?"]
turn                    = [r"You turned the (.+?) for (.+?) damage\."]
turn_fail               = [r"You failed to turn the (.+?)\."]
turn_living_target      = [r"You may only turn the unliving."]
turn_whom               = [r"Turn whom\?"]
slow = [r"Your touch slows down the (.+?)\."]
slow_fail = [r"You failed to slow the (.+?)\."]
slow_whom = [r"Slow whom\?"]
touch                   = [r"You touched the (.+?) for (.+?) damage\."]
touch_fail              = [r"You failed to harm the (.+?)\."]
touch_whom              = [r"Touch whom\?"]
wither                  = [r"You withered " + __three_possible_mob_strings  + r" for (?P<d>\d+) damage\."]
#You withered Farmer Woldis for 64 damage.

wither_fail             = [r"Your withering touch did not hurt " + __three_possible_mob_strings + r"\."]
wither_whom             = [r"Wither whom\?"]
bash                    = [r"You bash the (.+?), confusing them\."]
bash_fail               = [r"You failed to bash it\."]
bash_whom               = [r"Bash whom\?"]
circle                  = [r"You circle the (.+?)\."]
circle_fail             = [r"You failed to circle it\."]
circle_whom             = [r"Circle whom\?"]

backstab = [r"You backstab the (.+?)."]
backstab_fail = [r"You failed\."]
backstab_error = [r"Backstab requires sharp or thrusting weapons.", r"You don't see that here.", r"You need to be hidden or undetected to backstab!"]

no_see = [r"You don't see that here\."]
i_no_see = [r"I don't see that here\."]

# ask command
ask_success = ['(?:The)?(.+?) says to you, "(?P<statement>(?:.+?\n?\r?)+?)"']
ask_fail = ["(?:The)?(.+?) doesn't respond to you\."]

# Kill command
bad_k_target = [
    r"You don't see that here\.",
    r"Attack what\?"
]

# You knock the wind out of the mime artist!!
crit = [
    r"You knock the wind out of (?:.+?)",
    r"Your attack knocks (?:.+?) off balance",
    r"(?:.+?) is caught off guard by your attack"
]
# crit = [
#     r"You knock the wind out of " + __three_possible_mob_strings + r'!!',
#     r"Your attack knocks " + __three_possible_mob_strings + r' off balance!!',
#     __Three_possible_mob_strings + r" is caught off guard by your attack!!"
# ]

# Your wind magic buffets the usher.
# You cast a dustgust spell on usher.
# The spell did 39 damage.

spell_crit = [
    r"Your wind magic buffets " + __three_possible_mob_strings + r"\.",
    r"Your earth magic slams hard into " + __three_possible_mob_strings + r"\.",
    r"Your fire magic explodes into " + __three_possible_mob_strings + r"\."
]
__mob_overwhelmed = r"(?P<over>\n?\r?.+?\n?\r?Your attack overwhelms)?"
attack_hit = [
    "(?s)You swing with your .+?, hacking (?:the )?(" + __numbers + " )?(.+?)\s+for\s+(?P<d>\d+)\s+damage\." + __mob_overwhelmed,
    "(?s)You slice (?:the )?(" + __numbers + " )?(.+?) for (?P<d>\d+)\s+damage\s+with\s+your\s+.+?\." + __mob_overwhelmed,
    "You slash at (?:the )?(" + __numbers + " )?(.+?) and hit for (?P<d>\d+) damage\." + __mob_overwhelmed,

    "You chop at (?:the )?(" + __numbers + " )?(.+?) for (?P<d>\d+) damage\." + __mob_overwhelmed,
    "(?s)You stab (?:the )?(" + __numbers + " )?(.+?) with your .+?,\s+causing\s+(?P<d>\d+)\s+damage" + __mob_overwhelmed,
    "You lunge at (?:the )?(" + __numbers + " )?(.+?), striking for (?P<d>\d+) damage\." + __mob_overwhelmed,

    "You lash out and thump (?:the )?(" + __numbers + " )?(.+?) for (?P<d>\d+) damage\." + __mob_overwhelmed,
    "You punch (?:the )?(" + __numbers + " )?(.+?) for (?P<d>\d+) damage\." + __mob_overwhelmed,
    "You kick (?:the )?(" + __numbers + " )?(.+?) for (?P<d>\d+) damage\." + __mob_overwhelmed,
    "You head-butt (?:the )?(" + __numbers + " )?(.+?) for (?P<d>\d+) damage\." + __mob_overwhelmed,
    "You grab (?:the )?(" + __numbers + " )?(.+?) and gouge (him|her|it) for (?P<d>\d+)\s+damage\." + __mob_overwhelmed,

    "(?s)You smash your .+? into (?:the )?(" + __numbers + " )?(.+?),\s+causing\s+(?P<d>\d+)\s+damage\." + __mob_overwhelmed,
    "You heave your .+? at (?:the )?(" + __numbers + " )?(.+?),\s+smashing\s+(him|her|it)\s+for\s+(?P<d>\d+)\s+damage\." + __mob_overwhelmed,
    "You bludgeon (?:the )?(" + __numbers + " )?(.+?) for (?P<d>\d+) damage\." + __mob_overwhelmed,

    "You lunge at (?:the )?(" + __numbers + " )?(.+?), hitting them for (?P<d>\d+) damage\." + __mob_overwhelmed,
    "You swing your .+?, striking for (?P<d>\d+) damage\." + __mob_overwhelmed,
    "(?s)You sweep (?:the )?(" + __numbers + " )?(.+?) with your .+?\s+for\s+(?P<d>\d+)\s+damage\." + __mob_overwhelmed,

    "Your missile slams into (?:the )?(" + __numbers + " )?(.+?) for (?P<d>\d+) damage\." + __mob_overwhelmed,
    "(?s)You attack (?:the )?(" + __numbers + " )?(.+?) with your .+?,\s+striking\s+for\s+(?P<d>\d+)\s+damage\." + __mob_overwhelmed,
    "You use your .+? to strike (?:the )?(" + __numbers + " )?(.+?)\s+for\s+(?P<d>\d+)\s+damage\." + __mob_overwhelmed,
    r"(?P<over>Your touch completely overwhelms the (.+?)!)"
]
attack_miss = [
    "Your blow did no damage.",
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
    "(?s)You use your .+?, but nothing hits (?:the )?(" + __numbers + " )?(.+?)\.",
    "Your blow did no damage\." # Should be a hit for 0
]

aura = [r"You glow with a " + __aura + " aura\."]
mob_aura = [__Three_possible_mob_strings + r" glows with a " + __aura + " aura\."]

cast = [
    r"You cast a (.+?) spell on (.+?)\." + __mob_overwhelmed,
    r"(.+?) spell cast\." + __mob_overwhelmed,
    r"You cast a (.+?) spell\." + __mob_overwhelmed
]

bind_cast = [
    r"Bind cast on (.+?)\."
]

spell_damage = [
    r"The spell did (?P<d>\d+) damage."
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
    r"(?:\|(?P<white3>.+?)\|\s+)?"
    # r"(?:\|(?P<white3>.+?)\|\s+)?"
    r"/======================================= Miscellaneous ==================\\\s+"
    # r"(?P<misc>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    r"\|(?P<misc>.+?)\|\s+"
    r"(?:\|(?P<misc2>.+?)\|\s+)?"
    r"(?:\|(?P<misc3>.+?)\|\s+)?"
    r"/===================================================== Running Spells ===\\\s+"
    # r"(?P<buffs>(?:\|\s+.+?\s+\|\s*?\n\r)+)"
    r"\|(?P<buffs>.+?)\|\s+"
    r"(?:\|(?P<buffs2>.+?)\|\s+)?"
    r"(?:\|(?P<buffs3>.+?)\|\s+)?"
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
# you_arent_wearing_anything = [r"You aren't wearing anything\."]
on_body = [r"On (body):   (.+?)\n\r"]
on_arms = [r"On arms:   (.+?)\n\r"]
on_legs = [r"On legs:   (.+?)\n\r"]
# on_neck = [r"On neck:   (.+?)\n\r(On neck:   (?P<second_neck>.+?)\n\r)?"]
on_neck = [r"On neck:   (.+?)\n\r"]
on_face = [r"On face:   (.+?)\n\r"]
on_hands= [r"On hands:  (.+?)\n\r"]
on_head = [r"On head:   (.+?)\n\r"]
on_feet = [r"On feet:   (.+?)\n\r"]
on_finger = [r"On finger: (.+?)\n\r"]
# on_finger = [r"On finger: (.+?)\n\r(On finger: (?P<other_finger>.+?)\n\r)"]
shield  = [r"Shield:    (.+?)\n\r"]
wielded = [r"Wielded:   (.+?)\n\r"]
seconded= [r"Seconded:  (.+?)\n\r"]
holding = [r"Holding:   (.+?)\n\r"]

one_equip = [r"((?P<slot>(?:On [^:]{4,6})|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):\s+(?P<piece>.+?)\s*\n\r)"]
# See also wearing

# eq = [r"(On body:   (?P<body>.+?)\n\r)?" \
#       r"(On arms:   (?P<arms>.+?)\n\r)?" \
#       r"(On legs:   (?P<legs>.+?)\n\r)?" \
#       r"(On neck:   (?P<neck>.+?)\n\r)?" \
#       r"(On neck:   (?P<second_neck>.+?)\n\r)?" \
#       r"(On hands:   (?P<hands>.+?)\n\r)?" \
#       r"(On head:   (?P<head>.+?)\n\r)?" \
#       r"(On feet:   (?P<feet>.+?)\n\r)?" \
#       # r"(On finger: (?P<finger>.+?)){0,8}" \
#       r"(On finger: (?P<finger>.+?)\n\r)?" \
#       r"(On finger: (?P<finger2>.+?)\n\r)?" \
#       r"(On finger: (?P<finger3>.+?)\n\r)?" \
#       r"(On finger: (?P<finger4>.+?)\n\r)?" \
#       r"(On finger: (?P<finger5>.+?)\n\r)?" \
#       r"(On finger: (?P<finger6>.+?)\n\r)?" \
#       r"(On finger: (?P<finger7>.+?)\n\r)?" \
#       r"(On finger: (?P<finger8>.+?)\n\r)?" \
#       r"(Wielded:   (?P<weapon>.+?)\n\r)?" \
#       r"(Seconded:  (?P<seconded>.+?)\n\r)?" \
#       r"(Holding:   (?P<holding>.+?)\n\r)?" \
#       # r".+?\["  # Match the [ of the prompt at the end to ensure we get don't stop matching early
# ]
# eq = [r"(?P<slot>[^:]+?):(?P<piece>.+?)\n\r)" \
#       r"((?P<slot>[^:]+?):(?P<piece>.+?)\n\r)){" \
# eq = [r"((?P<slot>[^:]+?):(?P<piece>.+?)\n\r){1,20}"]  # Match the prompt bracket if this is not greedy enough
# eq = [r"((?P<slot>(On [^:]+?)|(Shield)):(?P<piece>.+?)\n\r){1,20}"]
    # This isn't greedy enough - we get notify before all equipment has been printed.
    # Match the prompt bracket?  Try it.  Hmph, the buffer gets flushed and we miss matches.  read_very_eager() solved it.
# eq = [r"(((?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?:.+?)\n\r){1,20}"]
# eq = [r"((?P<slot1>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece1>.+?)\n\r)"
#       r"((?P<slot2>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece2>.+?)\n\r)?"
#       r"((?P<slot3>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece3>.+?)\n\r)?"
#       r"((?P<slot4>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece4>.+?)\n\r)?"
#       r"((?P<slot5>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece5>.+?)\n\r)?"
#       r"((?P<slot6>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece6>.+?)\n\r)?"
#       r"((?P<slot7>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece7>.+?)\n\r)?"
#       r"((?P<slot8>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece8>.+?)\n\r)?"
#       r"((?P<slot9>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece9>.+?)\n\r)?"
#       r"((?P<slot10>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece10>.+?)\n\r)?"
#       r"((?P<slot11>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece11>.+?)\n\r)?"
#       r"((?P<slot12>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece12>.+?)\n\r)?"
#       r"((?P<slot13>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece13>.+?)\n\r)?"
#       r"((?P<slot14>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece14>.+?)\n\r)?"
#       r"((?P<slot15>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece15>.+?)\n\r)?"
#       r"((?P<slot16>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece16>.+?)\n\r)?"
#       r"((?P<slot17>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece17>.+?)\n\r)?"
#       r"((?P<slot18>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece18>.+?)\n\r)?"
#       r"((?P<slot19>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece19>.+?)\n\r)?"
#       r"((?P<slot20>(?:On [^:]+?)|(?:Shield)|(?:Wielded)|(?:Seconded)|(?:Holding)):(?P<piece20>.+?)\n\r)?"
#       # r"\[(\d+) H (\d+) M\]: "
# ]

# m.group('holding') returns None with no error if the holding group didn't occur.
# Erhm maybe it's \r\n

# "The extreme nature of this place wracks your aura!""  (Bandit Hill)

# you_feel_better = [r"You feel better\.\n\r"]
# you_feel_no_different = [r"You feel no different\."]
potion_drank = [r"Potion drank\."]
# use_what = [r"Use what\?\n\r"]  # didn't match
use_what = [r"Use what\?"]
cant_use = [
    r"How does one use that\?",
    r"You can only use a potion on yourself\."
]
you_drink=[r"You drink the philtre of health's broth\."]
eat_success=[r"You eat the (.+?)\."]
eat_fail=[r"The (.+?) has not been mixed properly\."]
cant_do=[r"You can't do that\."]

mix_success = [r"You finish preparing a (.+?)\."]
mix_fail = [r"Your preparation of a (.+?) fails\."]
not_mixed_properly=[r"The (.+?) has not been mixed properly.\."]
# eat

you_wield         = [r"You wield (an?|some) (?P<weapon>[A-Za-z ']+)\."]  # Gets a positive of the off-hand message
off_hand          = [r"You wield (an?|some) (?P<weapon>[A-Za-z ']+) in your off hand\."]
weapon_broken     = [r"You can't\. Its broken\."]  # grammatical error
not_weapon        = [r"You can't wield that\."]
dont_have         = [r"You don't have that\."]
weapon_break      = [r"Your (?P<weapon>[A-Za-z' ]+?) breaks and you have to remove it\."]
weapon_shatters   = [r"Your (?P<weapon>[A-Za-z' ]+?) shatters\."]
already_wielding  = [r"You're already wielding something\."]
no_primary        = [r"You're must be using a primary weapon first\."]
remove_shield     = [r"You must remove your shield first\."]
cannot_second     = [r"You cannot use this weapon at the same time as another"]
primary_excludes  = [r"Your primary weapon excludes the use of this one\."]
heavier_second    = [r"Your second weapon cannot be heavier than your primary one\."]
already_seconding = [r"You already have something in your off hand\."]
not_skilled       = [r'You are not yet skilled enough to use this!']
not_ranger        = [r'The skill is currently beyond you\.']

bought       = [r"^Bought\."]
# bought       = [r"Bought\."]
buy_what     = [r"Buy what\?"]
not_a_shop   = [r"This is not a shoppe\."]
not_for_sale = [r"That item is not for sale\."]  # TODO: this is made up and needs to be checked
cant_carry = [
    r"You can't carry anymore\.",
    r"You weren't able to carry everything\."
]
isnt_here = [r"That isn't here\."]

repair = [r"The smithy hands (?:an?|some) (?P<weapon>[A-Za-z' ]+?) back to you, almost good as new\."]
# TODO: The smithy takes \d+ gold pieces from you.
darnitall = [r'"Darnitall!" shouts the smithy, "I broke another\. Sorry la(d|ss)\.']
not_a_repair_shop = [r"This is not a repair shop\."]

# pristine_condition = [r"It is in pristine condition\."]
# excellent_condition = [r"It is in excellent condition\."]
# good_condition      = [r"It is in good condition\."]
# fair_condition      = [r"It is in fair condition\."]
# fine_condition      = [r"It is in fine condition\."]
# poor_condition      = [r"It is in poor condition\."]
# bad_condition       = [r"It is in bad condition\."]
# terrible_condition  = [r"It is in terrible condition\."]
condition = [r"It is in ([a-z]+) condition\."]
broken = [r"It is broken\."] # I think this is for broken armour
unusable = [r"It is unusable\."] # weapons

# Armour
repair_what    = [r"Repair what\?"]
cant_repair    = [r"The smithy cannot repair that\.", r"You can only repair weapons and armor\."]
not_broken     = [r"It's not broken yet\."]
drop_what      = [r"Drop what\?"]
sell_what      = [r"Sell what\?"]
# fled         = [r"You run like a chicken\."]
wear_what      = [r"Wear what\?"]
no_room        = [r"There is no room to wear that\!"]
already_holding= [r"You're already holding something\."]
in_combat      = [r"You are fighting\! you can't do that now\!"]
doesnt_fit     = [__item + r" doesn't fit you\."]
class_prevents = [r'Your class prevents you from using '+__items+r'\.']
no_gold        = [r"You don't have enough gold\."]
# get_ring     = [r"(?s)You get .+? an? .+? ring((,.+?\.)|(\.))"]  # problem here.
get_ring       = [r"(?s)You get " + __items + r"?an? [a-z]+ ring(([a-zA-Z0-1-',\s]+\.)|(\.))"]

occupied_area         = [r"Someone is blocking the way\."]
rest = [r"You lean back to take some rest\."] # blue text
you_feel_the_benefits = [r"You feel the benefits of resting\."]
may_not_use           = [r'You may not use that\.'] # Haven't needed this one (double print with class_prevents)

