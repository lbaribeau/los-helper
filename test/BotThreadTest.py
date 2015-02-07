import unittest, time
from main.bots.BotThread import *
from CommandHandler import CommandHandler
from MudReaderHandler import MudReaderHandler 
        
#tests for static functions in BotThread
class BotThreadTest(unittest.TestCase):

    lowest_value = 0
    low_value = 6
    high_value = 10
    low_timeout = 300
    high_timeout = 600

    def test_NotHasIdealMana(self):
        current_mana = self.low_value
        ideal_mana = self.high_value

        result = BotThread.has_ideal_mana(current_mana, ideal_mana)

        self.assertEquals(result, False)

    def test_HasIdealMana(self):
        current_mana = self.high_value
        ideal_mana = self.low_value

        result = BotThread.has_ideal_mana(current_mana, ideal_mana)

        self.assertEquals(result, True)

    def test_NotHasIdealHealth(self):
        current_health = self.low_value
        ideal_health = self.high_value

        result = BotThread.has_ideal_health(current_health, ideal_health)

        self.assertEquals(result, False)

    def test_HasIdealHealth(self):
        current_health = self.high_value
        ideal_health = self.low_value

        result = BotThread.has_ideal_health(current_health, ideal_health)

        self.assertEquals(result, True)

    def test_TrueCanUseTimedAbility(self):
        last_use = time.time() - self.high_timeout 
        timeout = self.low_timeout

        result = BotThread.can_use_timed_ability(last_use, timeout)
        self.assertEquals(result, True)

    def test_FalseCanUseTimedAbility(self):
        last_use = time.time() - self.low_timeout
        timeout = self.high_timeout

        # magentaprint("Times : " + str(last_use) + " " + str(timeout), False)

        result = BotThread.can_use_timed_ability(last_use, timeout)
        self.assertEquals(result, False)

    def test_TrueCanCastSpell_HasSurplusManaAndSpell(self):
        current_mana = self.high_value
        spell_cost = self.low_value
        knows_spell = True

        result = BotThread.can_cast_spell(current_mana, spell_cost, knows_spell)
        self.assertEquals(result, True)

    def test_TrueCanCastSpell_HasExactManaAndSpell(self):
        current_mana = self.low_value
        spell_cost = self.low_value
        knows_spell = True

        result = BotThread.can_cast_spell(current_mana, spell_cost, knows_spell)

        self.assertEquals(result, True)

    def test_FalseCanCastSpell_NotEnoughMana(self):
        current_mana = self.lowest_value
        spell_cost = self.low_value
        knows_spell = True

        result = BotThread.can_cast_spell(current_mana, spell_cost, knows_spell)
        self.assertEquals(result, False)

    def test_FalseCanCastSpell_DoesntKnowSpell(self):
        current_mana = self.high_value
        spell_cost = self.low_value
        knows_spell = False

        result = BotThread.can_cast_spell(current_mana, spell_cost, knows_spell)
        self.assertEquals(result, False)

    def test_TrueShouldHealUp_HealthAndManaLow(self):
        current_health = self.low_value
        ideal_health = self.high_value

        current_mana = self.high_value        
        heal_cost = self.low_value

        knows_spell = True
        has_healing_items = True

        result = BotThread.should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items)

        self.assertEquals(result, True)

    def test_TrueShouldHealUp_HealthAndManaLowSpellsOnly(self):
        current_health = self.low_value
        ideal_health = self.high_value
        current_mana = self.low_value
        ideal_mana = self.high_value
        heal_cost = self.lowest_value
        knows_spell = True
        has_healing_items = False

        result = BotThread.should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items)
        self.assertEquals(result, True)

    def test_TrueShouldHealUp_HealthAndManaLowItemsOnly(self):
        current_health = self.low_value
        ideal_health = self.high_value
        current_mana = self.low_value
        ideal_mana = self.high_value
        heal_cost = self.lowest_value
        knows_spell = False
        has_healing_items = True

        result = BotThread.should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items)
        self.assertEquals(result, True)

    def test_TrueShouldHealUp_HealthLow(self):
        current_health = self.low_value
        ideal_health = self.high_value
        current_mana = self.high_value
        ideal_mana = self.low_value
        heal_cost = self.lowest_value
        knows_spell = True
        has_healing_items = True

        result = BotThread.should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items)
        self.assertEquals(result, True)

    def test_TrueShouldHealUp_HealthLowManaLowButHasItems(self):
        current_health = self.low_value
        ideal_health = self.high_value
        current_mana = self.low_value
        ideal_mana = self.high_value
        heal_cost = self.high_value
        knows_spell = True
        has_healing_items = True

        result = BotThread.should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items)
        self.assertEquals(result, True)

    def test_FalseShouldHealUp_HealthAndManaHigh(self):
        current_health = self.high_value
        ideal_health = self.low_value
        current_mana = self.high_value
        ideal_mana = self.low_value
        heal_cost = self.low_value
        
        knows_spell = True
        has_healing_items = True

        result = BotThread.should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items)
        self.assertEquals(result, False)

    def test_FalseShouldHealUp_NoSpellsOrItems(self):
        current_health = self.low_value
        ideal_health = self.high_value
        current_mana = self.low_value
        ideal_mana = self.high_value
        heal_cost = self.lowest_value
        knows_spell = False
        has_healing_items = False

        result = BotThread.should_heal_up(current_health, ideal_health, current_mana, heal_cost, knows_spell,
                        has_healing_items)
        self.assertEquals(result, False)










