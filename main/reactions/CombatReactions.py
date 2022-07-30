
from db.MudMob import *
from misc_functions import *
from command.Inventory import parse_item_list
from db.Database import *
from db.MudMap import *
from db.MudItem import *
from db.MobLoot import *
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

        self.mobs_killed = {}
        self.hits_dealt = 0
        self.hits_missed = 0
        self.damage_dealt = 0
        self.highest_damage = 0
        self.lowest_damage = 0
        self.physical_crit = 0
        self.spells_cast = 0
        self.spells_failed = 0
        self.spell_damage_dealt = 0
        self.spells_crit = 0
        self.hits_received = 0
        self.hits_evaded = 0
        self.damage_taken = 0
        self.in_combat = False

        self.regex_cart = [RegexStore.attack_hit, RegexStore.attack_miss, RegexStore.mob_attacked, RegexStore.cast_failure, RegexStore.mob_defeated,
        RegexStore.spell_damage, RegexStore.loot_dropped]

    def notify(self, regex, M_obj):
        combat_state = self.in_combat

        # magentaprint("Combat Reaction happened on: " + regex)
        if regex in RegexStore.attack_hit:
            self.in_combat = True
            self.hits_dealt += 1
            dmg = 0
            try:
                dmg = int(M_obj.group('d'))
                self.damage_dealt += dmg
                self.highest_damage = max(self.highest_damage, dmg)
                self.lowest_damage = min(self.lowest_damage, dmg)
            except Exception as e:
                magentaprint("Couldn't convert attack regex to dmg / int")
        elif regex in RegexStore.loot_dropped:
            mob_name = self.character.mobs.read_match(M_obj)
            mob = Mob(name=str(mob_name).strip())
            new_mob = mob.map()
            if new_mob:
                magentaprint(str(mob) + " new mob found on loot drop - this shouldn't be happening", False)
            items = parse_item_list(M_obj.group('items'))
            for mud_item in items:
                mob_loot = MobLoot(mob=mob, item=mud_item.obj)
                mob_loot.map()

        elif regex in RegexStore.mob_defeated:
            # number = M_obj.group(1)
            mob = self.character.mobs.read_match(M_obj).lower()

            count = 1
            if mob in self.mobs_killed:
                count = self.mobs_killed[mob] + 1
                del self.mobs_killed[mob]

            self.mobs_killed[mob] = count
            
            # self.character.area_id, monster - map both into a MobLocation
            # add a rank to the MobLocation
            self.in_combat = False
        elif regex in RegexStore.attack_miss:
            self.hits_missed += 1
        elif regex is RegexStore.magic_crit:
            self.character.CRITS_LANDED += 1
        elif regex in RegexStore.mob_attacked:
            self.in_combat = True
            # if M_obj.group('d'):
            if 'd' in M_obj.groupdict().keys():
                self.hits_received += 1
                self.damage_taken = self.damage_taken + int(M_obj.group('d'))
            else:
                self.hits_evaded += 1
        elif regex in RegexStore.spell_damage:
            self.in_combat = True
            self.spells_cast += 1
            self.spell_damage_dealt += int(M_obj.group('d'))
            self.highest_damage = max(self.highest_damage, int(M_obj.group('d')))
            self.lowest_damage = min(self.lowest_damage, int(M_obj.group('d')))
        elif regex in RegexStore.cast_failure:
            self.in_combat = True
            self.spells_cast += 1
            self.spells_failed += 1

        if self.character.is_headless and combat_state != self.in_combat:
            magentaprint("Reporting", False)
            output_api_feed('report', self.report())

    def report(self, no_print=True):
        exp = self.character.TOTAL_EXPERIENCE
        gold = self.character.TOTAL_GOLD
        aura = self.character.AURA
        magentaprint("Current Aura: " + str(aura), no_print)
        magentaprint("Total EXP: " + str(exp) + " | Total Gold: " + str(gold), no_print)
        exp = self.character.EXPERIENCE
        expm = str(calculate_vpm(exp))
        magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, no_print)
        kills = len(self.mobs_killed)
        kpm = str(calculate_vpm(kills))
        magentaprint("Kills this Session: " + str(kills) + " | Kills / MIN: " + kpm, no_print)
        total_phys_attacks = self.hits_dealt + self.hits_missed
        spells_hit = self.spells_cast - self.spells_failed

        try:
            average_phys_damage = (round(self.damage_dealt / self.hits_dealt, 1) if self.hits_dealt > 0 else 0)
            phys_hit_rate = (round((self.hits_dealt / total_phys_attacks) * 100, 1) if total_phys_attacks > 0 else 0)
            phys_crit_rate = -1#round(self.crits_landed / total_phys_attacks * 100, 1)
            
            average_spell_damage = (round(self.spell_damage_dealt / spells_hit) if spells_hit > 0 else 0)
            spell_hit_rate = (round((spells_hit / self.spells_cast) * 100, 1) if self.spells_cast > 0 else 0)
            spell_crit_rate = -1
        except Exception as e:
            magentaprint(e, no_print)
            average_phys_damage = -2
            average_spell_damage = -2
            phys_hit_rate = -2
            spell_hit_rate = -2
            phys_crit_rate = -2
            spell_crit_rate = -2

        magentaprint(str(self.hits_dealt) + ",  " + str(total_phys_attacks) + ",  " + str(spells_hit) + ",  " + str(self.spells_cast))
        magentaprint("Average Phys Damage: " + str(average_phys_damage) + " | Average Spell Damage: " + str(average_spell_damage), no_print)
        magentaprint("Phys Hit Rate: " + str(phys_hit_rate) + "% | Spell Hit Rate: " + str(spell_hit_rate) + "%", no_print)
        magentaprint("Phys Crit Rate: " + str(phys_crit_rate) + " | Spell Crit Rate: " + str(spell_crit_rate) + "%", no_print)
        runtime = round(get_runtime_in_minutes(), 2)
        total_time = self.character.TRACK_TIME + self.character.REST_TIME + self.character.COMBAT_TIME
        percent_track = round(safe_divide(self.character.TRACK_TIME, total_time) * 100, 2)
        percent_rest = round(safe_divide(self.character.REST_TIME, total_time) * 100, 2)
        percent_combat = round(safe_divide(self.character.COMBAT_TIME, total_time) * 100, 2)
        magentaprint("Track Time: " + str(round(self.character.TRACK_TIME/60, 2)) + ", " + str(percent_track) + "%", no_print)
        magentaprint("Rest time: " + str(round(self.character.REST_TIME/60, 2)) + ", " + str(percent_rest) + "%", no_print)
        magentaprint("Combat Time: " + str(round(self.character.COMBAT_TIME/60, 2)) + ", " + str(percent_combat) + "%", no_print)
        magentaprint("Minutes Run: " + str(runtime), no_print)

        output = {
                'hp': self.character.hp,
                'mp': self.character.mp,
                'deaths': self.character.DEATHS,
                'area': str(self.character.MUD_AREA),
                'mobs': str(self.character.mobs.attacking),
                'track': str(self.character.current_track),
                'last_direction': self.character.LAST_DIRECTION,
                'successful_go': self.character.SUCCESSFUL_GO,
                'blocking_mob': self.character.GO_BLOCKING_MOB,
                'go_please_wait': self.character.GO_PLEASE_WAIT,
                'go_no_exit': self.character.GO_NO_EXIT,
                'go_timeout': self.character.GO_TIMEOUT,
                'confused': self.character.CONFUSED,
                'can_see': self.character.CAN_SEE,
                'aura':str(aura),
                'exp': exp,
                'expm': expm,
                'kills': kills,
                'kpm': kpm,
                'inventory': self.character.inventory.to_dict(),
                'mobs_killed': self.mobs_killed,
                'timestamp': get_timestamp(),
                'runtime': str(runtime),
                'total_phys_attacks': total_phys_attacks,
                'spells_hit': spells_hit,
                'average_phys_damage': average_phys_damage,
                'phys_hit_rate': phys_hit_rate,
                'phys_crit_rate': phys_crit_rate,
                'average_spell_damage': average_spell_damage,
                'spell_hit_rate': spell_hit_rate,
                'spell_crit_rate': spell_crit_rate,
                'rest_time': self.character.REST_TIME,
                'track_time': self.character.TRACK_TIME,
                'combat_time': self.character.COMBAT_TIME,
                'percent_track': percent_track,
                'percent_rest': percent_rest,
                'percent_combat': percent_combat
                }

        return output
