
from combat.Cast import Cast
from command.Ability import *
from misc_functions import magentaprint

# def get_class(character):
#     class_string = character.class_string
#     level = character.level
#     if class_string == "Ass":
#         return Assassin(telnetHandler)
#     elif class_string == "Bar":
#         return Barbarian(telnetHandler)
# class Assassin(CharacterClass):
#     def __init__(self, telnetHandler, level):
#         self.lvl1_maxHP = 19
#         self.lvl1_maxMP = 2
#         self.abilities = [Backstab(telnetHandler)]

class CharacterClass(object):
    def __init__(self, telnetHandler, class_string, level):
        self.id = class_string
        # self.slow_combat_skills = []
        # self.heal_skills = []
        # self.buff_skills = []
        # class_string = character.class_string

        self.ARMOR_SLOTS = [ "Body", "Arms", "Legs", "Neck", "Hands", "Head",
                             "Feet", "Finger", "Shield"
        ]

        self.weapon_slots = ["Wielded"]
        self.needs_weapon = True

        self.mana_tick = 2
        abilities = []

        if class_string == "Ass":
            self.lvl1_maxHP = 19
            self.lvl1_maxMP = 2
            abilities = [ Hide, Backstab ]
            Cast.cooldown_after_success = 5
        elif class_string == "Bar":
            self.lvl1_maxHP = 24
            self.lvl1_maxMP = 0
            self.mana_tick = 0
            # self.mana_tick_chapel = 0
            abilities = [ Bash, Circle, Berserk ]
        elif class_string == "Cle":
            self.lvl1_maxHP = 16
            self.lvl1_maxMP = 4
            self.mana_tick = 2
            abilities = [ Pray, Turn ]
            Cast.cooldown_after_success = 4
        elif class_string == "Fig":
            self.lvl1_maxHP = 22
            self.lvl1_maxMP = 2
            self.mana_tick = 2
            abilities = [ Bash, Circle ]
            Cast.cooldown_after_success = 5
        elif class_string == "Brd":
            self.lvl1_maxHP = 15
            self.lvl1_maxMP = 3
            self.mana_tick = 2
            abilities = [ AestersTears, DanceOfTheCobra ]
            Cast.cooldown_after_success = 4
        elif class_string == "Mag":
            self.lvl1_maxHP = 14
            self.lvl1_maxMP = 5
            self.needs_weapon = False
            self.mana_tick = 4  # unsure
            self.levelPath = [ ["out", "s", "w", "w", "w", "s", "e", "shop", "backroom", "portal"],
                          ["door", "out", "out", "w", "n", "e", "e", "e", "n", "cha"]]
            abilities = []
            Cast.cooldown_after_success = 3
        elif class_string == "Pal":
            self.lvl1_maxHP = 19
            self.lvl1_maxMP = 3
            abilities = [ Pray, Turn ]
            Cast.cooldown_after_success = 5
        elif class_string == "Ran":
            self.lvl1_maxHP = 18
            self.lvl1_maxMP = 3
            self.HP_gained_per_level = 6
            self.MP_gained_per_level = 3
            self.mana_tick = 2
            # self.mana_tick_chapel = 4  # Assume chapel gives +2 mana tick
            abilities = [ Haste ]
            Cast.cooldown_after_success = 5
            self.weapon_slots.append("Second")
            # cooldown is faster after lvl 10
            Search.cooldown_after_success = 6
            Search.cooldown_after_failure = 6
        elif class_string == "Thi":
            self.lvl1_maxHP = 18
            self.lvl1_maxMP = 3
            abilities = [ Hide, Backstab ]
            Cast.cooldown_after_success = 5
        elif class_string == "Mon":
            self.lvl1_maxHP = 17
            self.lvl1_maxMP = 3
            self.HP_gained_per_level = 6
            self.MP_gained_per_level = 3
            self.needs_weapon = False
            abilities = [ Meditate, Touch ]
            Cast.cooldown_after_success = 5
            # self.heal_skills.extend([ClassSkillReaction(mudReaderHandler, "Meditate",
            #                         SkillTimer("You feel at one with the universe\.", 110),
            #                         SkillTimer("Your spirit is not at peace.", 10))])

            # I actually remove abilities that are too high in level at the bottom.
            # if self.level > 9:
            #     self.slow_combat_skills.extend([ClassSkillReaction(mudReaderHandler, "Touch",
            #                             SkillTimer("Your? touch(?:ed)? .+?\.", 240),
            #                             SkillTimer("You failed to harm the .+?\.", 240))])
            self.weapon_slots = []
            self.ARMOR_SLOTS = []
        elif class_string == "Dru":
            self.lvl1_maxHP = 15
            self.lvl1_maxMP = 4
            abilities = [ Barkskin ]
            Cast.cooldown_after_success = 4
        elif class_string == "Alc":
            self.lvl1_maxHP = 15
            self.needs_weapon = False
            lvl1_maxMP = 4
            abilities = [ Slow ]
            Cast.cooldown_after_success = 3
        elif class_string == "Dar":
            self.lvl1_maxHP = 19
            self.lvl1_maxMP = 4
            abilities = [ Berserk, Wither ] # Wither causes death :(
            Cast.cooldown_after_success = 5
        else:
            magentaprint("CharacterClass error: could not recognize class string.")

        self.abilities = {}

        for a in abilities + [Search, Prepare]:
            if level >= a.level:
                self.abilities[a.command] = a(telnetHandler)  # Construct all abilities

        self.pre_combat_skills = [a for a in self.abilities.values() if isinstance(a, PreCombatAbility)]
        self.heal_skills = [a for a in self.abilities.values() if isinstance(a, HealAbility)]
        self.buff_skills = [a for a in self.abilities.values() if isinstance(a, BuffAbility)]
        self.slow_combat_skills = [a for a in self.abilities.values() if isinstance(a, SlowCombatAbility)]
        self.fast_combat_skills = [a for a in self.abilities.values() if isinstance(a, FastCombatAbility)]

        for h in self.heal_skills:
            h.set_level(level)

        # self.abilities.append(Search(telnetHandler))
        # self.abilities = [a for a in self.abilities if level >= a.level]
        # self.abilities = [c, a for c, a in self.abilities.items() if level >= a.level]
        # self.abilities = {c: a for c, a in self.abilities.items() if level >= a.level}
        # for c, a in self.abilities.items:
        #     if level >= a.level:
        # magentaprint("CharacterClass abilities before dict comprehension: " + str(self.abilities))
        # self.abilities = {a.command: a for a in self.abilities if level >= a.level}
        magentaprint("CharacterClass final abilities: " + str(self.abilities))

    # characters that primarily rely on magic for their damage
    def is_caster(self):
        return self.id in ["Mag", "Alc"]

    def is_healer(self):
        return self.id in ["Cle", "Pal"] # maybe druid too?

    # characters that primarily rely on physical attacks for their damage and have innate weapon skill
    # while dark knigth and paladin don't have innate weapon skill they get aura damage buffs
    def is_phys(self):
        return self.id in ["Mon", "Bar", "Dar", "Ran", "Fig", "Pal"]

    def __str__(self):
        return self.id


# OLD IDEAS

# CombatAbility class?
#class CombatAbility:
#    ''' CombatAbilities are things that will affect how a character fights,
#    like circle, bash, steal, backstab, '''
#    def getCommand(self):
#        abstract()
#    def getCombatAlgorithm
# CombatAbility would be kind of like CoolAbility, but I can't imagine how
# that approach would work for BotThread.  Instead use this CharacterClass
# structure (canCircle, canBash, canSteal, etc.)


    # @property
    # def lvl1_maxHP(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def lvl1_maxMP(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def HP_gained_per_level(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def MP_gained_per_level(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def mana_tick_amount(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def abilities(self): raise NotImplementedError("Subclasses should implement this!")
    # @property
    # def level_path(self): raise NotImplementedError("Subclasses should implement this!")
