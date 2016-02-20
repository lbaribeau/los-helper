
# Unused
from combat.CombatObjects import Cast

class ShowAura(Cast):
	aura = None

	def cast(self):
		super().cast('show')

		
