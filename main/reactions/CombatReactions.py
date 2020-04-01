
from misc_functions import *
from db.Database import *
from db.MudMap import *
import comm.RegexStore as RegexStore

class CombatReactions(object):
    def __init__(self, character):
        # I think these regexes don't use enough text so might be slow to run all of the mud text against all the time
        #self.physical_hit_type = "You (head-butt|kick|grab|lash out( at| and thump)?) the (.+?)( and gouge him)?"
        # self.physical_damage = "You ([A-Za-z ']+?) the ([A-Za-z0-9 ']+?) for (\d+) damage\."
        # self.physical_miss = "You (.+?) the (.+?), but (.+?)\." #keyword "but" means ignore everything - you missed
        self.physical_critical = "(The|Your?).+?!!"  # Todo: more specific crit regex

        #self.mob_physical_hit_type = " (kicks|punches|lashes out|throws a wild punch at) you"
        # self.mob_physical_damage = "The (.+?) ([\d]) damage\."
        # self.mob_physical_miss = "The (.+?) you, but (.+?)\."
        # self.spell_damage_dealt = "The spell did ([\d]*) damage\."
        # self.regexes = [self.physical_damage,
        #                 self.physical_miss,
        #                 self.physical_critical,
        #                 self.mob_physical_damage,
        #                 self.mob_physical_miss,
        #                 self.spell_damage_dealt,
        #                 self.spell_fails,
        #                 self.enemy_defeated]

        self.spell_type = "You cast a (.+?) spell on (.+?)\."

        numbers = "(?:[\d]*?1st|[\d]*?2nd|[\d]*?3rd|[\d]*th)"
        # self.enemy_defeated = "Your enemy, (?:the |The )?(" + numbers + " )?(.+?) has been defeated\."

        self.character = character

        # self.good_MUD_timeout = 1.5
        # self.__waiter_flag = False
        # self.__stopping = False

        self.mobs_killed = []
        self.hits_dealt = 0
        self.hits_missed = 0
        self.damage_dealt = 0
        self.highest_damage = 0
        self.lowest_damage = 0
        # self.CRITS_LANDED = 0
        self.spells_cast = 0
        self.spells_failed = 0
        self.spell_damage_dealt = 0
        self.spells_crit = 0
        self.hits_received = 0
        self.hits_evaded = 0
        self.damage_taken = 0

        self.regex_cart = [RegexStore.attack_hit, RegexStore.attack_miss, RegexStore.mob_attacked, RegexStore.cast_failure, RegexStore.mob_defeated]

    def notify(self, regex, M_obj):
        # magentaprint("Combat Reaction happened on: " + regex)
        if regex in RegexStore.attack_hit:
            self.hits_dealt += 1
            dmg = 0
            try:
                dmg = int(M_obj.group('d'))
            except Exception as e:
                magentaprint("Couldn't convert attack regex to dmg / int")

            self.highest_damage = max(self.highest_damage, dmg)
            self.lowest_damage = min(self.lowest_damage, dmg)
        elif regex in RegexStore.mob_defeated:
                # number = M_obj.group(1)
                self.mobs_killed.append(self.character.mobs.read_match(M_obj))
                # self.character.area_id, monster - map both into a MobLocation
                # add a rank to the MobLocation
        elif regex in RegexStore.attack_miss:
            self.hits_missed += 1
        # elif regex is self.physical_critical:
        #     self.character.CRITS_LANDED += 1
        elif regex in RegexStore.mob_attacked:
            # if M_obj.group('d'):
            if 'd' in M_obj.groupdict().keys():
                self.hits_received += 1
                self.damage_taken = self.damage_taken + int(M_obj.group('d'))
            else:
                self.hits_evaded += 1
        elif regex in RegexStore.spell_damage:
            self.spells_cast += 1
            self.spell_damage_dealt += int(M_obj.group('d'))
            self.highest_damage = max(self.highest_damage, int(M_obj.group('d')))
            self.lowest_damage = min(self.lowest_damage, int(M_obj.group('d')))
        elif regex in RegexStore.cast_failure:
            self.spells_cast += 1
            self.spells_failed += 1

    def report(self):
        exp = self.character.TOTAL_EXPERIENCE
        gold = self.character.TOTAL_GOLD
        aura = str(self.character.AURA_STATUS)
        magentaprint("Current Aura: " + aura, False)
        magentaprint("Total EXP: " + str(exp) + " | Total Gold: " + str(gold), False)
        exp = self.character.EXPERIENCE
        expm = str(calculate_vpm(exp))
        magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, False)
        kills = len(self.mobs_killed)
        kpm = str(calculate_vpm(kills))
        magentaprint("Kills this Session: " + str(kills) + " | Kills / MIN: " + kpm, False)
        total_phys_attacks = self.hits_dealt + self.hits_missed
        # crits_landed = self.character.CRITS_LANDED
        spells_hit = self.spells_cast - self.spells_failed

        try:
            average_phys_damage = (round(self.damage_dealt / self.hits_dealt, 1) if self.hits_dealt > 0 else 0)
            phys_hit_rate = (round((self.hits_dealt / total_phys_attacks) * 100, 1) if total_phys_attacks > 0 else 0)
            phys_crit_rate = 0#round(self.crits_landed / total_phys_attacks * 100, 1)
            
            average_spell_damage = (round(self.spell_damage_dealt / spells_hit) if spells_hit > 0 else 0)
            spell_hit_rate = (round((self.spells_hit / self.spells_cast) * 100, 1) if self.spells_cast > 0 else 0)
            spell_crit_rate = 0
        except Exception as e:
            magentaprint(e, False)
            average_phys_damage = -1
            average_spell_damage = -1
            phys_hit_rate = -1
            spell_hit_rate = -1
            phys_crit_rate = -1
            spell_crit_rate = -1

        magentaprint(str(self.hits_dealt) + ",  " + str(total_phys_attacks) + ",  " + str(spells_hit) + ",  " + str(self.spells_cast))
        magentaprint("Average Phys Damage: " + str(average_phys_damage) + " | Average Spell Damage: " + str(average_spell_damage), False)
        magentaprint("Phys Hit Rate: " + str(phys_hit_rate) + "% | Spell Hit Rate: " + str(spell_hit_rate) + "%", False)
        magentaprint("Phys Crit Rate: " + str(phys_crit_rate) + " | Spell Crit Rate: " + str(spell_crit_rate) + "%", False)
        runtime = round(get_runtime_in_minutes(), 2)
        magentaprint("Minutes Run: " + str(runtime), False)
