
# Level 1
burn         = 'burn'
hurt         = 'hu'
rumble       = 'rum'
blister      = 'blis'

# Level 2
fireball     = 'fireb'
dustgust     = 'dust'
crush        = 'crush'
waterbolt    = 'water'

# Level 3
shockbolt    = 'shock'
burstflame   = 'burstflame'
shatterstone = 'shatt'

vigor        = 'v'
mendwounds   = 'm'
light        = 'l'
showaura     = 'show'
protection   = 'prot'

# Parallel arrays used to downrank
_lvl1 = [
	burn, 
	hurt,
	rumble, 
	blister
]
_lvl2 = [
	fireball, 
	dustgust,
	crush, 
	waterbolt
]
_lvl3 = [
	burstflame,
	shockbolt,
	shatterstone
]

def _get_level_3(level1_spell):
	index = _lvl1.index(level1_spell)
	if index < len(_lvl3):
		return _lvl3[index]
	else:
		return _lvl2[index]

def _get_level_2(level1_spell):
	return _lvl2[_lvl1.index(level1_spell)]
