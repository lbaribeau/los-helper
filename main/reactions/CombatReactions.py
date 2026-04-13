
from misc_functions import *
from db.Database import *
from db.MudMap import *
import comm.RegexStore as R
import statistics
import datetime
import math
from plots import plots

class CombatReactions(object):
    def __init__(self, character):
        self.character = character
        self.physical_critical       = "(The|Your?).+?!!"  # TODO: more specific crit regex
        self.reset()

        self.regex_cart = [
            R.attack_hit   , 
            R.attack_miss  , 
            R.spell_damage ,
            R.cast_failure , 
            R.circle       ,
            R.circle_fail  ,
            R.mob_defeated ,
            R.mob_attacked 
        ]

    def notify(self, regex, M_obj):
        # magentaprint("Combat Reaction happened on: " + regex)
        if regex in R.attack_hit:
            gd = M_obj.groupdict()
            if 'd' in gd:
                self.damage_array.append(int(gd['d']))
            else:
                self.damage_array.append(0)
        elif regex in R.attack_miss:
            self.hits_missed+=1
        # elif regex is self.physical_critical:
        #     self.character.CRITS_LANDED += 1
        elif regex in R.spell_damage:
            # self.spells_cast += 1
            # self.spell_damage_dealt += int(M_obj.group('d'))
            # self.highest_damage = max(self.highest_damage, int(M_obj.group('d')))
            # self.lowest_damage = min(self.lowest_damage, int(M_obj.group('d')))
            self.spell_damage.append(int(M_obj.groupdict()['d']))
        elif regex in R.cast_failure:
            # self.spells_cast += 1
            self.spells_failed += 1
        elif regex in R.circle:
            self.circles+=1
        elif regex in R.circle_fail:
            self.circle_fails+=1
        elif regex in R.mob_defeated:
                # number = M_obj.group(1)
                self.mobs_killed.append(self.character.mobs.read_mob_name_from_regex_match(M_obj))
                # self.character.area_id, monster - map both into a MobLocation
                # add a rank to the MobLocation
        elif regex in R.mob_attacked:
            # if M_obj.group('d'):
            # if 'd' in M_obj.groupdict().keys(): # "in" on a dict checks the keys, and it's fast because hashing
            if 'd' in M_obj.groupdict():
                # self.hits_received += 1
                # self.damage_taken = self.damage_taken + int(M_obj.group('d'))
                self.hits_received.append(int(M_obj.group('d')))
            else:
                self.hits_received.append(0) # I think it's fair to record it like this,
                # Not sure there's a distinction between them missing and them doing zero damage like there is when we attack (could miss or hit a zero if low str)
            # else:
            #     self.hits_evaded += 1

    def report(self):
        x = self.character.EXPERIENCE # Accumulated this session (initialized to zero, matches "You gain...")
        t = get_runtime_seconds()
        gold_gained = self.character.GOLD-self.character.START_GOLD
        # exp = C.EXPERIENCE
        # expm = str(calculate_vpm(exp))
        # magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, False)
        # magentaprint("EXP this Session: " + str(calculate_vpm(C.EXPERIENCE)) + " | EXP / MIN: " + expm, False) // This calc is done elsehwere
        magentaprint("--- REPORT ---")
        # magentaprint("Start time:        " + str(startTime)[:-3])#full_time_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        #str(startTime)[:-3])#full_time_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        # magentaprint("Start time:        " + startTime.strftime("%H:%M:%S"[:-3]+" %Y-%m-%d"))
        magentaprint("Start time:        " + startTime.strftime("%H:%M:%S.%f")[:-3]+startTime.strftime(" %Y-%m-%d"))
        # magentaprint("Current time:        " + datetime.datetime.now().strftime("%H:%M:%S"[:-3]+" %Y-%m-%d"))
        magentaprint("Current time:      " + datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]+datetime.datetime.now().strftime(" %Y-%m-%d"))
        # magentaprint("Start time:        " + now.strftime("%H:%M:%S"
        magentaprint("Uptime:            " + get_runtime_string())
        magentaprint("Exp this session:  " + str(x)) # Current xp we don't really know reliably unless we zero exp this session or just note exp on login only
        magentaprint("Gold this session: {} ".format(gold_gained)) # Gold spent would be good... needs a variable for that, also a variable for gold gained
        magentaprint("Current gold:      " + str(self.character.GOLD))
        magentaprint("Exp rate:          {} /hr".format(round(x/t*3600)))
        magentaprint("Gold rate:         {} /hr".format(round(gold_gained/t*3600)))
        magentaprint("---")
        # Kills this Session: " + str(kills) + " | Kills / MIN: " + kpm, False)
        # magentaprint("Kills this Session: " + str(kills) + " | Kills / MIN: " + kpm, False)
        D=self.damage_array
        num_hits=len(D) # Damage array doesn't have zeros in it for misses, but does for "Your blow did no damage."
        # magentaprint(str(num_hits+self.hits_missed) + " attacks,")
        magentaprint(f"Attacks                  : {str(num_hits+self.hits_missed)}")
        magentaprint(f"Hits                     : {num_hits}")
        magentaprint(f"Misses                   : {self.hits_missed}")
        magentaprint(f"Zeros                    : {D.count(0)}")
        magentaprint(f"Damage array             : {D}")
        magentaprint(f"Total damage             : {sum(D)}")
        # (In Python 3, integer division will get us floats)
        if num_hits:
            magentaprint(f"Hit rate                 : {num_hits/(num_hits+self.hits_missed)*100:.2f}%")
            magentaprint(f"Mean                     : {statistics.mean(D):.2f}")

            # magentaprint(f"Attack hit average damage: {statistics.mean(self.damage_array):.2f} +/- {2*statistics.stdev(self.damage_array):.2f}") # Or do sum(self.damage_array)/len(self.damage_array)
            # No... I think that the /sqrt(n) is about statistics measurement error, which I don't care about
            # I don't need error in estimate of the mean (/sqrt(n))
            # I just need to print what we got and use 2sigma for error
            if num_hits > 1:
                stdev = statistics.stdev(D)
            else: 
                stdev = 0
            magentaprint(f"Attack stdev             : {stdev:.2f}")
            magentaprint(f"2 stdevs                 : {2*stdev:.2f}")
            # magentaprint(f"Attack hit average damage: {statistics.mean(self.damage_array):.2f}") # Or do sum(self.damage_array)/len(self.damage_array)
            magentaprint(f"Zero rate of hits        : {D.count(0)/num_hits*100:.2f}%")
            magentaprint(f"Damage expectation       : {sum(D)/(num_hits+self.hits_missed):.2f}")
            # magentaprint(f"Median: {sorted(self.damage_array)[num_hits/2-1] if num_hits % 2 else (int(self.damage_array[num_hits/2])+int(self.damage_array[num_hits/2+1]))/2}")
            _sorted=sorted(D)
            # magentaprintprint(f"Median: {_sorted[int(num_hits/2)-1] if num_hits % 2 == 0 else (int(_sorted[int(num_hits/2+.5)])+int(_sorted[int(num_hits/2)-.5]))/2}")
            median=_sorted[int(num_hits/2-.5)] if num_hits % 2 else (int(_sorted[int(num_hits/2-1)])+int(_sorted[int(num_hits/2)]))/2
            magentaprint(f"Median                   : {median:.1f}")
            if stdev > 0.1:
                magentaprint(f"Z score (distance from 0): {statistics.mean(D)/stdev*100:.2f}%")
            else:
                magentaprint(f"Z score (distance from 0): infinite")
            magentaprint(f"Variability              : {stdev/statistics.mean(D)*100:.2f}%")
            magentaprint(f"Skew                     : {statistics.mean(D)-median:.2f}")
            magentaprint(f"Range                    : {max(D)-min(D)}")
            magentaprint(f"Min (0th percentile)     : {min(D)}")
            magentaprint(f"10th percentile          : {self.get_percentile(_sorted, .1):.1f}")
            magentaprint(f"25th percentile          : {self.get_percentile(_sorted, .25):.1f}")
            magentaprint(f"Median                   : {median}")
            magentaprint(f"75th percentile          : {self.get_percentile(_sorted, .75):.1f}")
            magentaprint(f"90th percentile          : {self.get_percentile(_sorted, .90):.1f}")
            magentaprint(f"Max (100th percentile)   : {max(D)}")

        circles_attempted=self.circles+self.circle_fails
        magentaprint(f"Circles attempted        : {circles_attempted}")
        magentaprint(f"Circles hit              : {self.circles}")
        magentaprint(f"Circles missed           : {self.circle_fails}")
        if circles_attempted:
            magentaprint(f"Circle hit rate          : {self.circles/(self.circles+self.circle_fails)*100:.2f}%") 
        magentaprint("---")
        magentaprint("Spell damage:")
        magentaprint(self.spell_damage)
        LSD=len(self.spell_damage) # length spell damage
        if LSD:
            magentaprint(f"Mean assuming hit: {statistics.mean(self.spell_damage)}")
        if LSD or self.spells_failed:
            magentaprint(f"Spell hit: {LSD/(self.spells_failed+LSD)*100:.2f}%") # Might be nice to record this for lvl 2 magic
            magentaprint(f"Spell expectation mean: {sum(self.spell_damage)/(LSD+self.spells_failed)}")
        magentaprint(str(len(self.mobs_killed))+" mobs killed:")
        magentaprint("  "+", ".join(self.mobs_killed))
        magentaprint("---")
        if not self.hits_received:
            magentaprint("No mob attacks to report")
        else:
            num_hits=len(self.hits_received)
            D=self.hits_received
            magentaprint(f"Mob attacks              : {num_hits}")
            magentaprint(f"Misses/blocks            : {D.count(0)}")
            magentaprint(D)
            magentaprint(f"Total damage             : {sum(D)}")
            magentaprint(f"Block/Dodge rate         : {D.count(0)/num_hits*100:.2f}%")
            magentaprint(f"Damage expectation       : {sum(D)/num_hits:.2f}")
            magentaprint(f"(Remove zeros from mob damage array because it's like misses, unlike how we did player damage)")
            D=[_D for _D in D if _D > 0]
            _sorted=sorted(D)
            num_hits=len(D)
            if num_hits>1:
                stdev=statistics.stdev(D)
            elif num_hits == 1:
                stdev=0
            else:
                magentaprint(f"All stats are 0")
                return
            magentaprint(f"Mob attack stdev         : {stdev:.2f}")
            magentaprint(f"2 stdevs                 : {2*stdev:.2f}")
            # magentaprint(f"Attack hit average damage: {statistics.mean(self.damage_array):.2f}") # Or do sum(self.damage_array)/len(self.damage_array)
            # magentaprint(f"Damage expectation: {sum(D)/(num_hits):.2f}")
            # magentaprint(f"Median: {sorted(self.damage_array)[num_hits/2-1] if num_hits % 2 else (int(self.damage_array[num_hits/2])+int(self.damage_array[num_hits/2+1]))/2}")
            # magentaprintprint(f"Median: {_sorted[int(num_hits/2)-1] if num_hits % 2 == 0 else (int(_sorted[int(num_hits/2+.5)])+int(_sorted[int(num_hits/2)-.5]))/2}")
            median=_sorted[int(num_hits/2-.5)] if num_hits % 2 else (int(_sorted[int(num_hits/2-1)])+int(_sorted[int(num_hits/2)]))/2
            magentaprint(f"Median                   : {median:.1f}")
            if stdev > .1:
                magentaprint(f"Z score (distance from 0): {statistics.mean(D)/stdev*100:.2f}%")
            else:
                magentaprint(f"Z score (distance from 0): infinite")
            magentaprint(f"Variability              : {stdev/statistics.mean(D)*100:.2f}%")
            magentaprint(f"Skew                     : {statistics.mean(D)-median:.2f}")
            magentaprint(f"Range, without 0         : {max(D)-min([_D for _D in D if _D != 0])}")
            magentaprint(f"Min (0th percentile)     : {min(D)}")
            magentaprint(f"10th percentile          : {self.get_percentile(_sorted, .1):.1f}")
            magentaprint(f"25th percentile          : {self.get_percentile(_sorted, .25):.1f}")
            magentaprint(f"Median                   : {median:.1f}")
            magentaprint(f"75th percentile          : {self.get_percentile(_sorted, .75):.1f}")
            magentaprint(f"90th percentile          : {self.get_percentile(_sorted, .90):.1f}")
            magentaprint(f"Max (100th percentile)   : {max(D)}")
        magentaprint("---")
        # Idea: bashes (R.bash, R.bash_fail)... I don't bash lately it's not great... gives acolytes time to regen mana, mime artists land their spells anyway
        # Maybe plot histograms of player damage and mob damage, even spells
        # Maybe split by mob target (both player damage and mob damage)
        # Idea: time stats like, did we get attacks every 3 secons
        # Or what kind of lag/delays are we seeing from commands

    def reset(self):
        self.damage_array         = [] # numpy could be faster
        self.spell_damage         = []
        self.hits_received        = []
        self.mobs_killed          = []
        self.hits_missed          = 0
        self.spells_failed        = 0
        # self.hits_evaded        = 0
        self.circles              = 0
        self.circle_fails         = 0

    def plot(self):
        if not self.damage_array:
            magentaprint("No player damage samples")
            return
        pyplot = plots.get_pyplot()

        pyplot.figure(f"Player Damage Samples ({self.hits_missed} misses, not shown) ({len(self.mobs_killed)} mobs killed)")
        pyplot.plot(self.damage_array, '--*')
        pyplot.xlabel("Sample")
        pyplot.ylabel("Damage")
        plots.auto_config()

        pyplot.figure(f"Player Damage Bar Graph ({self.hits_missed} misses not shown) ({len(self.mobs_killed)} mobs killed)")
        # pyplot.bar(self.damage_array) #[self.damage_array.count(i) for i in range(0,6)]
        D=self.damage_array
        L=len(D)
        plots.do_grid()
        bars=pyplot.bar(range(0, max(D)+1), [D.count(i) for i in range(0,max(D)+1)], align='center', color='skyblue', edgecolor='black') #[self.damage_array.count(i) for i in range(0,6)]
        bars[0].set_color("dodgerblue") # https://matplotlib.org/stable/gallery/color/named_colors.html
        bars[0].set_edgecolor("black")
        pyplot.gca().set_xticks(range(0, max(D)+1))
        pyplot.gca().set_yticks(range(0, max([D.count(i) for i in range(0,max(D)+1)])+1))
        pyplot.xlabel("Damage")
        pyplot.ylabel("Count")
        pyplot.tight_layout()

        # plots.auto_config_hist()
        if not self.hits_received:
            magentaprint("No mob damage samples")
            return
        pyplot.figure("Mob Damage Samples")
        pyplot.plot(self.hits_received, '--*')
        plots.auto_config()
        pyplot.xlabel("Sample")
        pyplot.ylabel("Damage")

        pyplot.figure("Mob Damage Bar Graph")
        # heights,ranges,patches = pyplot.bar(self.damage_array)
        D=self.hits_received
        L=len(D)
        plots.do_grid()
        bars=pyplot.bar(range(0, max(D)+1), [D.count(i) for i in range(0,max(D)+1)], align='center', color='lightcoral', edgecolor='black') #[self.damage_array.count(i) for i in range(0,6)]
        bars[0].set_color("coral")
        bars[0].set_edgecolor("black")
        pyplot.gca().set_xticks(range(0, max(D)+1))
        pyplot.gca().set_yticks(range(0, max([D.count(i) for i in range(0,max(D)+1)])+1)) # maybe ymax
        pyplot.xlabel("Mob Damage")
        pyplot.ylabel("Count")
        pyplot.tight_layout()
        # plots.auto_config_hist()
        pyplot.show(block=False) # Alternative is pyplot.ion(), turns interactive mode on, but, this is better, but, make sure the interpreter doesn't think it's time to exit

    def get_percentile(self, sorted_data, p):
        # (Did I just vibe code?)
        if not sorted_data: return 0
        # _sorted = sorted(data)
        L = len(sorted_data)
        index_fractional=p*(L-1)
        lower_point=math.floor(index_fractional)
        upper_point=math.ceil(index_fractional)
        interp_weight=index_fractional-lower_point
        return (1-interp_weight)*sorted_data[lower_point]+interp_weight*sorted_data[upper_point]

    def report1(self):
        C = self.character
        exp = C.TOTAL_EXPERIENCE  # Ehrm maybe name these variables better...
        # This one comes from Info sheet, character xp, and isn't maintained
        gold = C.GOLD

        # if not hasattr(C,'aura'):
        #     magentaprint("CombatReactions.py: Please check aura first")
        #     magentaprint("Apparently I broke 'report' when I moved 'aura' off of 'character' onto cast.")
        #     magentaprint("Report could subscribe to the aura regex or have access to cast...")
        #     magentaprint("[{} H {} M]: ".format(C.HEALTH, C.MANA))
        #     return

        # aura = str(C.aura)
        # magentaprint("Current Aura: " + C.aura, False)
        # magentaprint("Character EXP: " + str(exp), False)
        magentaprint("Character Gold " + str(gold), False)
        exp = C.EXPERIENCE
        expm = str(calculate_vpm(exp))
        magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, False)
        kills = len(self.mobs_killed)
        kpm = str(calculate_vpm(kills))
        magentaprint("Kills this Session: " + str(kills) + " | Kills / MIN: " + kpm, False)
        total_phys_attacks = self.hits_dealt + self.hits_missed
        # crits_landed = C.CRITS_LANDED
        spells_hit = self.spells_cast - self.spells_failed

        try:
            average_phys_damage = round(self.total_damage_dealt / self.hits_dealt, 1)
            phys_hit_rate = round(self.hits_dealt / self.total_phys_attacks * 100, 1)
            # phys_crit_rate = round(self.crits_landed / total_phys_attacks * 100, 1)

            average_spell_damage = round(self.spell_damage_dealt / self.spells_hit)
            spell_hit_rate = round(self.spells_hit / self.spells_cast * 100, 1)
            spell_crit_rate = 0
        except Exception:
            average_phys_damage = -1
            average_spell_damage = -1
            phys_hit_rate = -1
            spell_hit_rate = -1
            phys_crit_rate = -1
            spell_crit_rate = -1

        magentaprint("Average Phys Damage: " + str(average_phys_damage) + " | Average Spell Damage: " + str(average_spell_damage), False)
        magentaprint("Phys Hit Rate: " + str(phys_hit_rate) + "% | Spell Hit Rate: " + str(spell_hit_rate) + "%", False)
        magentaprint("Phys Crit Rate: " + str(phys_crit_rate) + " | Spell Crit Rate: " + str(spell_crit_rate) + "%", False)
        runtime = round(get_runtime_in_minutes(), 2)
        magentaprint("Minutes Run: " + str(runtime), False)


    def print_experience(self):
        # Copied from command_handler... could deleted it from there...
        x = self.character.EXPERIENCE # Accumulated this session (initialized to zero, matches "You gain...")
        t = get_runtime_seconds()
        gold_gained = self.character.GOLD-self.character.START_GOLD
        magentaprint("Start time:        " + str(startTime))
        magentaprint("Uptime:            " + get_runtime_string())
        magentaprint("Exp this session:  " + str(x))
        magentaprint("Gold this session: {} ".format(gold_gained))
        # magentaprint("Start gold:        " + str(self.character.START_GOLD))
        magentaprint("Current gold:      " + str(self.character.GOLD))
        magentaprint("Exp rate:          {} /hr".format(round(x/t*3600)))
        # magentaprint("Exp rate:          {} /min".format(round(round(x/t*60))))
        # g = self.character.GOLD # Ok this is all the current gold, so it won't give us gold rate
        # magentaprint("Gold delta: ")
        # magentaprint("Gold rate: {} gold/hr; {} gold/min; {} gold/s.".format(round(x/t/3600), round(x/t/60), round(x/t)))
        # magentaprint("EXP this Session: " + str(exp) + " | EXP / MIN: " + expm, False)
        #magentaprint(str(exp), False)
        magentaprint("Gold rate:         {} /hr".format(round(gold_gained/t*3600)))
        # magentaprint("Gold rate:         {} /min".format(round(gold_gained/t*60, 1)))
        # (Deleted from __init__())...

        # I think these regexes don't use enough text so might be slow to run all of the mud text against all the time
        # self.physical_hit_type     = "You (head-butt|kick|grab|lash out( at| and thump)?) the (.+?)( and gouge him)?"
        # self.physical_damage       = "You ([A-Za-z ']+?) the ([A-Za-z0-9 ']+?) for (\d+) damage\."
        # self.physical_miss         = "You (.+?) the (.+?), but (.+?)\." #keyword "but" means ignore everything - you missed

        # self.mob_physical_hit_type = " (kicks|punches|lashes out|throws a wild punch at) you"
        # self.mob_physical_damage   = "The (.+?) ([\d]) damage\."
        # self.mob_physical_miss     = "The (.+?) you, but (.+?)\."
        # self.spell_damage_dealt    = "The spell did ([\d]*) damage\."
        # numbers = "(?:[\d]*?1st|[\d]*?2nd|[\d]*?3rd|[\d]*th)"
        # self.enemy_defeated = "Your enemy, (?:the |The )?(" + numbers + " )?(.+?) has been defeated\."
        # self.regexes = [
        #   self.physical_damage,
        #   self.physical_miss,
        #   self.physical_critical,
        #   self.mob_physical_damage,
        #   self.mob_physical_miss,
        #   self.spell_damage_dealt,
        #   self.spell_fails,
        #   self.enemy_defeated]

        # self.spell_type = "You cast a (.+?) spell on (.+?)\."
        # self.hits_dealt           = 0 # Use length of array? Sure
        # Prefer to keep the whole array... let the stats be functions
        # self.damage_dealt       = 0
        # self.highest_damage     = 0
        # self.lowest_damage      = 0
        # self.CRITS_LANDED       = 0
        # self.spells_cast          = 0 # This can be sum of fails and successes
        # self.spell_damage_dealt = 0
        # self.spells_crit        = 0
        # self.damage_taken         = 0 # Keep an array
        # self.mobs_defeated        = 0

        # if attack_hit
            # self.hits_dealt += 1
            # self.highest_damage = max(self.highest_damage, int(M_obj.group('d')))
            # self.lowest_damage = min(self.lowest_damage, int(M_obj.group('d')))