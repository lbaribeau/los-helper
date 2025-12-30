
import re


# re.match(pattern, string, flags)
# - Flags can be like re.IGNORECASE or re.MULTILINE

__numbers2025  = "(?P<nth>(?P<n>\d+)(st|nd|rd|th) )" # This one bifurcates the suffix"st/nd/rd/th" from the actual number (1/2/3/4) but we can assume that the mud is consistant that way
# __numbers_opt  = "(?:" + __numbers3 + ")?"
__numbers_opt  = "(?:" + __numbers2025 + ")?"
__Three_possible_mob_strings = r"(?P<whole_mob_name>((?P<mob1>The( [A-Z][a-z'-]+)+)|(?:The " + __numbers_opt + r"(?P<mob2>[a-z '-]+))|(?P<mob3>[A-Z][A-Za-z '-]+)))"

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

M = re.match(mob_attacked[9], "The 4th stall holder lashes out at you, but misses.")
# M should be able to get me "stall 2"
# Uh oh... that depends on other mobs....
# Since it's just one word....
# So it's coupled...
M.group('n') # Should be 4

# Ok we got 2

M = re.match(mob_attacked[9], "The stall holder lashes out at you, but misses.")
M.group('n') # Should be 1
# Ok good it matched because we do have the "option" (?) on the numbers
# And .group('n') is none


r=mob_attacked[9]
M = re.match(r, "The stall holder lashes out at you, but misses.")
if M: # MudReader checks this
	if M.group('n'):
		n=M.group('n')
	else:
		n=1
else:
	"error"

# Suppose I want the 2nd stall holder
# But there is also a stall bolder present
# So my RestLoop object needs access to mobs (mobs.list)
# Then I could say, ok get_first_reference("stall holder")
# That would handle the stall bolder
# Add 1 to get the 2nd stall holder






