
import time
import re

from misc_functions import *
from Exceptions import *
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
# from mini_bots.travel_bot import TravelBot
from mini_bots.smithy_bot   import SmithyBot
from mini_bots.mini_bot     import MiniBot
from mini_bots.shopping_bot import ShoppingBot
from db.Database            import AreaStoreItem

class WeaponBot(MiniBot):
    # This one handles a lot of cases (dual wielding)
    # It works well if a pile of weapons are available in the bag already
    # But I want to guarantee a weapon available in the bag
    # So I wrote weapon bot 2 to make that extra purchase

    # def __init__(self, char, command_handler, simple_weapon_bot):
    def __init__(self, char, command_handler):
        super().__init__()
        self.char = char
        self.command_handler = command_handler
        # self.simple_weapon_bot = simple_weapon_bot

        self.actions = {
            # R.you_wield: (lambda self, match : self.weapon = match.group('weapon')),
            # R.off_hand: (lambda self, match : self.second = match.group('weapon')),
            # R.weapon_break: lambda match : if
            R.you_wield[0]       : self.react_to_wield,
            R.off_hand[0]        : self.react_to_off_hand,
            R.weapon_break[0]    : self.react_to_weapon_break,
            R.weapon_shatters[0] : self.react_to_weapon_break,
            R.shield[0]          : self.set_shield_or_offhand
        }
        # self.regex_cart = self.actions.keys()
        self.regex_cart = [R.you_wield, R.off_hand, R.weapon_break, R.weapon_shatters, R.shield]
        self.broken_weapon     = []
        self.possible_weapons  = []
        self.shield_or_offhand = False
        self.temporary_weapon  = False

    def add_in_map(self, mud_map):
        # Methods which require navigation or knowing possible weapons to wield require this to be called
        self.smithy_bot   = SmithyBot(self.char, self.command_handler, mud_map)
        self.shopping_bot = ShoppingBot(self.char, self.command_handler, mud_map)

    def notify(self, regex, match):
        self.actions[regex](match)

    def react_to_wield(self, match):
        magentaprint("WeaponBot.react_to_wield() set self.weapon to " + match.group('weapon'))
        self.weapon = match.group('weapon')

    def react_to_off_hand(self, match):
        magentaprint("WeaponBot matched off_hand regex.")
        self.shield_or_offhand = True
        self.second = match.group('weapon')

    def react_to_weapon_break(self, match):
        self.broken_weapon.append(match.group('weapon'))

        if hasattr(self, 'weapon') and self.weapon == match.group('weapon'):
            magentaprint("WeaponBot deleted self.weapon.")
            del self.weapon  # self.weapon can be incorrectly deleted if the offhand is the same
        elif hasattr(self, 'second') and self.second == match.group('weapon'):
            self.shield_or_offhand = False
            del self.second

    def set_shield_or_offhand(self, match=None):
        magentaprint("WeaponBot set shield_or_offhand.")
        self.shield_or_offhand = True

    def run(self):
        if self.char.level <= 2:
            self.stopping = True
            self.stop()
        else:
            self.check_weapons()

    def has_broken_weapon():
        return self.broken_weapon

    def check_weapons(self):
        if self.char.level <= 2:
            return

        if self.temporary_weapon:
            self.correct_temp_weapon()
        elif self.broken_weapon:
            self.repair_or_replace_weapon()
        elif hasattr(self, 'weapon'): #and self.shield_or_offhand:  # ArmourBot or eq should be called first...
            return
        else:
            magentaprint("Repair / replace weapon", False)
            self.repair_or_replace_weapon()

    def repair_or_replace_weapon(self):
        self.command_handler.equipment.execute_and_wait()
        self.stopping = False
        if hasattr(self, 'weapon'): #and self.shield_or_offhand:
            magentaprint("WeaponBot.repair_or_replace_weapon() has weapon and shield/offhand so return.")
            return
        # elif not self.shield_or_offhand:
        #     magentaprint("WeaponBot needs to figure out whether to buy an offhand - assume shield.")
        #     return

        # if hasattr(self, 'broken_weapon'):
        magentaprint('repair_or_replace_weapon calling try_exact_replacement_from_inventory')
        if self.try_exact_replacement_from_inventory():
            # self.temporary_weapon = True  # Ensure that we have a backup
            return
        magentaprint('repair_or_replace_weapon calling try_exact_replacement_from_inventory_with_possible_smithy_trip')
        if self.try_exact_replacement_from_inventory_with_possible_smithy_trip():
            # self.temporary_weapon = True  # Ensure that we have a backup
            return

        # if self.try_other_possible_weapons_in_inventory():  # This will be used in combat,
            # but out of combat, we want to go to the smithy and try other possible weapons in order
        # if self.try_other_possible_weapons_in_inventory_with_possible_smithy_trip():
        #     return
        # Actually - forget other possible weapons - we want the default at this point
        # (We now plan to hold onto a backup weapon.)
        if self.broken_weapon:
            self.broken_weapon = []

        magentaprint('repair_or_replace_weapon calling try_default_replacement_from_inventory')
        if self.try_default_replacement_from_inventory():
            # self.temporary_weapon = True  # Ensure that we have a backup
            return
        magentaprint('repair_or_replace_weapon calling try_default_replacement_from_inventory_with_possible_smithy_trip')
        if self.try_default_replacement_from_inventory_with_possible_smithy_trip():
            # self.temporary_weapon = True  # Ensure that we have a backup
            return

        # Forget broken_weapon here since we are going to the default weapon at this point
        self.go_buy_replacement()
        # self.temporary_weapon = True  # Ensure that we have a backup

    def try_exact_replacement_from_inventory(self):
        wielded_weapon = self.try_weapon_list_from_inventory(self.broken_weapon)
        if wielded_weapon:
            self.broken_weapon.remove(wielded_weapon)
            return wielded_weapon

    def first_possible_weapon(self):
        weapons = self.get_possible_weapons()

        if len(weapons) > 0:
            return weapons[0].item.name

        return None


    def try_default_replacement_from_inventory(self):
        magentaprint('try_default_replacement_from_inventory')
        return self.try_weapons_from_inventory(self.first_possible_weapon())

    def try_weapon_list_from_inventory(self, l):
        magentaprint('try_weapon_list_from_inventory')
        for w in l:
            if self.try_weapons_from_inventory(w):
                return w

    def try_rewielding_each_in_inventory(self, command_object, weapon_name):
        ref = self.char.inventory.get_reference(weapon_name, 2)

        while self.char.inventory.get(ref) and self.char.inventory.get(ref).obj.name == weapon_name:
            if self.char.inventory.get(ref).usable:
                command_object.execute_and_wait(ref)

                if command_object.success:
                    return True
                else:
                    self.char.inventory.set_broken(ref)

            ref = MobTargetDeterminator().increment_ref(ref)

        return False

        # If offhand breaks, we need to try one wield and then correct our variables once we learn which broke of mainhand/offhand

    # def go_replace_weapon(self, w):
    #     self.go_buy_and_wield(self.shattered_weapon)
    #     del self.shattered_weapon

    #     bw = self.broken_weapon
    #     del self.broken_weapon
    #     self.go_buy_and_wield(bw)

    def rewield(self, weapon_ref, failover=False):
        weapon_name = self.char.inventory.name_from_reference(weapon_ref)
        self.command_handler.smartCombat.wield.persistent_execute(weapon_ref)
        self.command_handler.smartCombat.wield.wait_for_flag()
        if self.command_handler.smartCombat.wield.success:
            return True
        elif self.command_handler.smartCombat.wield.result in R.already_wielding:
            self.command_handler.smartCombat.wield.second.persistent_execute(weapon_ref)
            self.command_handler.smartCombat.wield.second.wait_for_flag(weapon_ref)
            if not self.command_handler.smartCombat.wield.second.success:
                raise Exception("Couldn't rewield!")
            else:
                self.second = weapon_name  # ??? This should get set by the notify
        else:
            self.rewield(weapon_ref + " 2", True)
            if failover:
                raise Exception("WeaponBot.rewield() wield error!")

    def try_weapons_from_inventory(self, weapon_name):
        if weapon_name is None:
            return False

        magentaprint('try_weapons_from_inventory')
        if hasattr(self, 'weapon'):  # We know that the offhand broke
            magentaprint("WeaponBot.try_weapons_from_inventory() but weapon is already set to " + self.weapon + '!')
            if self.try_reequipping_offhand(weapon_name):
                # self.second = w  # let the reaction do it
                return True
        else:
            ref = self.char.inventory.get_first_reference(weapon_name)
            magentaprint("WeaponBot.try_weapons_from_inventory() weapon name/ref: " + str(weapon_name) + "/" + str(ref))

            # while ref and self.char.inventory.get(ref).obj.name == weapon_name:  # ??? Should work, but had get return None after broken weapon.
            while ref and self.char.inventory.get(ref) and self.char.inventory.get(ref).obj.name == weapon_name:
                if self.char.inventory.get(ref).usable:
                    self.command_handler.smartCombat.wield.execute_and_wait(ref)

                    if self.command_handler.smartCombat.wield.result in R.already_wielding:
                        magentaprint("WeaponBot got already_wielding, assume offhand broke!")
                        if self.second:
                            self.weapon = self.second
                            del self.second
                            self.shield_or_offhand = False
                            self.try_weapons_from_inventory(weapon_name)
                        else:
                            raise Exception("WeaponBot.try_weapons_from_inventory confusion.")
                    elif self.command_handler.smartCombat.wield.result in R.weapon_broken:
                        self.char.inventory.unset_usable(ref)
                    elif self.command_handler.smartCombat.wield.success:
                        return True
                    else:
                        pass
                        # magentaprint("WeaponBot.try_weapons_from_inventory() tried " + str(w))
                        # if self.try_reequipping_mainhand(w):
                        #     self.weapon = w
                        #     return True

                ref = MobTargetDeterminator().increment_ref(ref)

            return False

    def combat_rewield(self):
        # Wield anything viable in inventory.  Ideally the bot carries/keeps/maintains a light backup weapon
        # with which to finish any fights.  Are we writing that or a stopgap?  Brocolli could carry a small mace,
        # Ruorg could carry a long bow.  It's a bit tough to decide that with the DB right now.  I suppose it could
        # check the inventory for a viable backup, hmph.  The stop gap will be that I don't set up a choice of backup weapon -
        # I'll just use the keep list, and weapon_bot will not go buy a backup, but it will satisfy the checks for combat_rewield,
        # and also I should right code here to replace and rewield the primary weapon after the fight.  So I should set a variable
        # when I rewield an odd weapon.  This means that I will stick hard to the default weapon that I can buy instead of using up
        # other weapons, which is okay I suppose.

        # Wield anything in inventory.  Set flag if it's not the primary choice weapon.
        if self.temporary_weapon:
            return
        else:
            if not self.try_exact_replacement_from_inventory():
                self.try_other_possible_weapons_in_inventory()
            self.temporary_weapon = True

    # def try_exact_replacement_from_inventory(self):
    #     self.simple_weapon_bot.try_exact_replacement_from_inventory()

    # def try_weapon_list_from_inventory(self, l):
    #     self.simple_weapon_bot.try_weapon_list_from_inventory(self, l)

    @property
    def should_go_to_smithy(self):
        return (not hasattr(self, 'weapon') or self.temporary_weapon) and \
            (self.char.inventory.has_any_broken(self.broken_weapon) or \
                self.char.inventory.has_broken(self.get_possible_weapons[0].item.name))

    def try_exact_replacement_from_inventory_with_possible_smithy_trip(self):
        magentaprint("WeaponBot.try_exact_replacement_from_inventory()")
        if self.char.inventory.has_any(self.broken_weapon) and not self.stopping:
            self.smithy_bot.go_to_nearest_smithy()
            wielded_weapon = self.try_weapon_list_from_inventory_in_smithy(self.broken_weapon)
            if wielded_weapon:
                self.broken_weapon.remove(wielded_weapon)
                return wielded_weapon

    def try_default_replacement_from_inventory_with_possible_smithy_trip(self):
        magentaprint("WeaponBot.try_default_replacement_from_inventory_with_possible_smithy_trip()")
        if self.char.inventory.has(self.first_possible_weapon()) and not self.stopping:
            self.smithy_bot.go_to_nearest_smithy()
            # return self.try_weapons_from_inventory(self.possible_weapons[0].item.name)
            return self.try_weapon_list_from_inventory_in_smithy([self.possible_weapons[0].item.name])
        else:
            magentaprint("has(%s) returned False" % str(self.first_possible_weapon()))

    def try_weapon_list_from_inventory_in_smithy(self, l):
        for w in l:
            while self.char.inventory.has(w) and not self.stopping:
                magentaprint("WeaponBot in smithy " + str(w))

                if self.repair_one(w):
                    self.rewield(self.char.inventory.get_last_reference(w))
                    return w

    def repair_one(self, name):
        ref = self.char.inventory.get_last_reference(name)
        self.command_handler.repair.execute_and_wait(ref)
        if self.command_handler.repair.success:
            self.char.inventory.set_usable(ref)
            return True
        else:
            self.char.inventory.remove_by_ref(ref)
            return False

    def try_other_possible_weapons_in_inventory(self):
        magentaprint("WeaponBot.try_other_possible_weapons_in_inventory() " + str(self.get_possible_weapons()))
        # for w in self.get_possible_weapons():
        #     if self.try_weapon_from_inventory(w.item.name):
        #         return True

        if self.try_weapon_list_from_inventory([w.item.name for w in self.get_possible_weapons()]):
            self.temporary_weapon = True
            return True
        # return self.try_weapon_list_from_inventory([w.item.name for w in self.get_possible_weapons()]):

    @property
    def default(self):
        if hasattr(self, 'weapon'):
            magentaprint("WeaponBot.default weapon: " + str(self.weapon))
            return self.weapon == self.first_possible_weapon()
        else:
            magentaprint("WeaponBot.weapon was deleted.")
            return False
        # We aren't tackling dual wielding here yet - ie. default offhand (assume shield)

    def try_other_possible_weapons_in_inventory_with_smithy_trip(self):
        # We won't break this down because we want to go through each weapon in order of priority, repairing the
        # first on the list if we have it before processing lower level weapons
        # We won't assume try_other_possible_weapons_in_inventory() has been called
        # We might try a weapon twice before repairing, since that's easier to write at the moment.  The fix for that
        # would be to set and check unusable.  We could implement that in try_weapon_list_from_inventory_in_smithy and save code.
        for w in self.get_possible_weapons():
            while self.char.inventory.has(w.item.name) and not self.stopping:
                if self.try_weapons_from_inventory(w.item.name):
                    return True

                self.smithy_bot.go_to_nearest_smithy()

                if self.repair_one(w.item.name):
                    self.rewield(self.char.inventory.get_last_reference(w.item.name))
                    return True

    def go_buy_replacement(self):
        if self.go_buy_default_weapon():
            self.wield_default_weapon()
        # if self.go_purchase_item(possible_weapons[0]):
        # magentaprint("GrindThread.go_purchase_item() got location id: " + str(item.get_purchase_location_id()))
        # if item.get_purchase_location_id():
        #     self.direction_list = ["areaid%s" % item.get_purchase_location_id(), "dobuy%s" % item.to_string(), "areaid2"]
        #     return True
        # else:
        #     return False

        #     magentaprint("check_weapons stacked shop path and dobuy onto purchase path, returning.")
        #     return True
        #     # if self.smartCombat.try_weapon(possible_weapons[0].name):  # I can't wield because I don't have the weapon yet.
        #     #     return True
        #     # else:
        #     #     magentaprint("Check weapons had trouble wielding bought weapon.")
        #     #     self.pause()
        # else:
        #     magentaprint("No weapon error - couldn't find anything in inventory or repair or shop...")
        #     self.pause()

        # return False

    def go_buy_default_weapon(self):
        magentaprint("WeaponBot.go_buy_default_weapon()")
        magentaprint("WeaponBot.go_buy_replacement() calling shopping_bot.go_buy " + str(self.get_possible_weapons()[0]), False)

        if self.shopping_bot.go_buy(self.possible_weapons[0]):
            return True
        else:
            if hasattr(self, 'weapon'):
                magentaprint("Warning: WeaponBot could not buy another weapon")
            else:
                # raise Exception("WeaponBot couldn't buy main weapon.")
                magentaprint("WeaponBot couldn't buy main weapon.")  # We won't exit here - maybe the bot will sell/drop then return
            return False

    def get_store_path(self):
        return self.map.get_path(self.char.AREA_ID, self.get_possible_weapons()[0].area.id, False)

    def wield_default_weapon(self):
        self.rewield(self.char.inventory.get_last_reference(self.possible_weapons[0].item.name))

    @property
    def possible_weapons_in_inventory(self):
        return self.char.inventory.get_all_by_name_list([asi.item.name for asi in self.get_possible_weapons()])

    def correct_temp_weapon(self):
        magentaprint("WeaponBot.correct_temp_weapon")
        self.stopping = False
        # We wielded a weapon in combat, so we should now wield a default weapon and ensure we have a backup
        if self.default:
            magentaprint('default')
            magentaprint("self.char.inventory.has_any([w.item.name for w in self.get_possible_weapons()]: " + str(self.char.inventory.has_any([w.item.name for w in self.get_possible_weapons()])))

            # if self.get_possible_weapons()
            # usable_possible_weapons_in_inv = any(x.usable for x in self.possible_weapons_in_inventory)
            # if self.char.inventory.get_all_by_name_list([asi.item.name for asi in self.get_possible_weapons()]) and \
            #    any([x.usable for x in self.char.inventory.get_all_by_name_list([asi.item.name for asi in self.get_possible_weapons()])]):
# [asi.item.name for asi in self.get_possible_weapons()])):

            # if self.possible_weapons_in_inventory and any(x.usable for x in self.possible_weapons_in_inventory):
            #     pass
            # elif self.char.inventory.has_any([w.item.name for w in self.get_possible_weapons()]):
            # self.possible_weapons_in_inventory = self.char.inventory.get_all_by_name_list([asi.item.name for asi in self.get_possible_weapons()])
            if self.possible_weapons_in_inventory:
                if any(x.usable for x in self.possible_weapons_in_inventory):
                    pass
                else:
                    magentaprint('Ensure that one is usable to serve as the backup')
                    for w in self.get_possible_weapons():
                        while self.char.inventory.has(w.item.name) and not self.stopping:
                            self.go_to_nearest_smithy()
                            if self.repair_one(w.item.name):
                                # break  # This break won't work since there are two loops
                                self.correct_temp_weapon()  # This will fall into the first 'pass' and then exit out
                    magentaprint('All repairs failed')
                    self.correct_temp_weapon()  # Execution will proceed into the other else, where we may decide to go shopping
                    # if we require a backup
            else:
                magentaprint("WeaponBot.correct_temp_weapon() has no backup weapon.")
                # self.go_buy_default_weapon() # too heavy to carry
            self.temporary_weapon = False
            self.broken_weapon = []
        else:
            while self.char.inventory.has(self.first_possible_weapon()) and not self.stopping:
                # magentaprint('Not wielding default (?): ' + str(self.weapon) + '/' + str(self.possible_weapons()[0]))
                # Preferred case (backup weapon was different)
                magentaprint("self.char.inventory.has(?): " + str(self.first_possible_weapon()))
                magentaprint(str(self.char.inventory))
                # while self.char.inventory.has(self.first_possible_weapon()):  # Done in repair
                self.go_to_nearest_smithy()
                # if self.repair(self.char.inventory.get_last_reference(self.first_possible_weapon())):
                if self.repair_one(self.first_possible_weapon()):
                    self.swap_to_default_weapon()
                    return

            if self.go_buy_default_weapon():
                self.swap_to_default_weapon()

    def swap_to_default_weapon(self):
        self.remove_mainhand()
        self.wield_default_weapon()
        self.temporary_weapon = False
        self.broken_weapon = []

    def remove_mainhand(self):
        if hasattr(self, 'weapon'):  # temporary_weapon does get set when unarmed from no good backup
            weapon_word = self.weapon.split()[1] if len(self.weapon.split()) > 1 else self.weapon
            self.command_handler.telnetHandler.write('rm ' + weapon_word)  # If some equipped armour has the same word as a weapon, this will be a bug

    def stop(self):
        self.stopping = True
        if hasattr(self, 'smithy_bot'):
            self.smithy_bot.stop()
            self.shopping_bot.stop()

    # def go_repair(self):
    #     if hasattr(self, 'broken_weapon'):
    #         if self.try_weapons_from_inventory(self.broken_weapon):
    #             del self.broken_weapon
    #             return

    #         if self.char.inventory.has(self.broken_weapon):
    #             self.go_to_nearest_smithy()

    #             if self.repair_and_wield_broken_weapons(self.broken_weapon):
    #                 del self.broken_weapon
    #                 return

    #         # self.go_buy_and_wield(self.broken_weapon)  # Nevermind trying to buy the same, just go to the DB
    #         # del self.broken_weapon
    #     else:
    #         if not hasattr(self, 'weapon'):
    #             raise Exception("TopDownGrind needs to choose a weapon from db.")

    # def try_weapons_from_inventory(self, w):
    #     for w in self.broken_weapon:
    #         if self.try_weapon_from_inventory(w):
    #             self.broken_weapon.pop()
    # def try_weapons_from_inventory(self, full_weapon_name):
    #     weapon_ref = self.char.inventory.get_first_reference(full_weapon_name)
    #     while self.char.inventory.get(weapon_ref).obj.name == full_weapon_name:
    #         if self.try_weapon_from_inventory(weapon_ref):
    #             return True
    #         else:
    #             weapon_ref = MobTargetDeterminator().increment_ref(weapon_ref)
    #     return False

    # def try_weapon_from_inventory(self, w):
    #     self.simple_weapon_bot.try_weapon_from_inventory(w)

    def try_reequipping_mainhand(self, weapon_name):
        return self.try_rewielding_each_in_inventory(self.command_handler.smartCombat.wield, weapon_name)

    def try_reequipping_offhand(self, weapon_name):
        return self.try_rewielding_each_in_inventory(self.command_handler.smartCombat.wield.second, weapon_name)

    def go_to_nearest_smithy(self, grinding=False):
        # magentaprint("TopDownGrind.go_to_nearest_smithy()")
        # smithy_path = self.get_smithy_path()
        # magentaprint("TopDownGrind.get_smithy_path(): " + str(smithy_path))
        # self.travel_bot = TravelBot(self.char, self.command_handler, self.mrh, self.db_handler)
        # self.travel_bot.follow_path(smithy_path)
        # self.smithy_bot = SmithyBot(self.char, self.command_handler, self.mrh)
        if hasattr(self, 'smithy_bot'):
            self.smithy_bot.go_to_nearest_smithy()
        else:
            raise Exception("WeaponBot: init_with_map() must be called before navigating to the smithy.")

    def get_possible_weapons(self):
        if self.possible_weapons:
            magentaprint("WeaponBot possible weapons: " + str(self.possible_weapons))
            return self.possible_weapons
        elif not hasattr(self, 'smithy_bot'):
            magentaprint("WeaponBot: Warning: get_possible_weapons() was called before init_with_map.")
            return None
        else:
            self.possible_weapons = AreaStoreItem.get_by_item_type_and_level_max('weapon', self.char.weapon_type, self.char.weapon_level)
            self.possible_weapons = sorted(self.possible_weapons, key = lambda i: i.item.level, reverse=True)
            magentaprint("WeaponBot possible weapons: " + str(self.possible_weapons), False)
            return self.possible_weapons

            # level = self.character.weapon_level
            # while not self.possible_weapons and level > 0:

            #     areastoreitems = AreaStoreItem.get_by_item_type_and_level(model_name, data_name, level)
            #     self.possible_weapons = list(MudItem.get_suitable_item_of_type('weapon', self.character.weapon_type, level).values())
            #     areastoreitems = AreaStoreItem.get_by_item_type_and_level(model_name, data_name, level)

            # while not self.possible_weapons and level > 0:
            #     magentaprint("check_weapons() trying lower level weapons.")
            #     self.possible_weapons = list(MudItem.get_suitable_item_of_type('weapon', self.character.weapon_type, level).values())
            #     level = level - 1

            # if not self.possible_weapons:
            #     magentaprint("WeaponBot didn't come up with a default weapon!")

            # return self.possible_weapons

    # def get_smithy_path(self):
    #     try:
    #         paths = self.db_handler.get_smithy_paths(self.char.AREA_ID)
    #     except Exception as e:
    #         #not a good situation - we can't find a way to the chapel from wherever we are
    #         #therefore we should just sit and wait here until we can go on the warpath again
    #         magentaprint("Exception getting smithy path.")
    #         magentaprint(e, False)
    #         raise e

    #     if paths:
    #         return get_shortest_array(paths)
    #     else:
    #         magentaprint("SmartGrindThread.get_smithy_path() error... no exception but no path returned... make sure the DB is accessible.")
    #         self.rest_and_check_aura()
    #         return []

    # Commented - algorithm change - we can do the same thing on shattered or broken
    # (try items in inventory, repair items in inventory, then go shopping)

    # def react_to_weapon_shatter(self, match):
    #     if hasattr(self, 'weapon') and hasattr(self, 'second') and self.weapon == self.second:
    #         # self.unknown_broken_weapon = True  # Unneeded because we will try both wield and second
    #         self.shattered_weapon = self.weapon
    #     elif hasattr(self, 'weapon') and self.weapon == match.group('weapon'):
    #         self.shattered_weapon = self.weapon
    #         del self.weapon
    #     elif hasattr(self, 'second') and self.second == match.group('weapon'):
    #         self.shattered_weapon = self.second
    #         del self.second
    #     else:
    #         magentaprint("TopDownGrind.react_to_weapon_shatter error case.")

    # def go_repair_or_replace_weapon(self):
    #     if hasattr(self, 'broken_weapon'):
    #         if self.try_weapons_from_inventory(self.broken_weapon):
    #             del self.broken_weapon
    #             return

    #         if self.char.inventory.has(self.broken_weapon):
    #             self.go_to_nearest_smithy()

    #             if self.repair_and_wield_broken_weapons(self.broken_weapon):
    #                 del self.broken_weapon
    #                 return

    #         self.go_buy_and_wield(self.broken_weapon)
    #         del self.broken_weapon

    #     elif hasattr(self, 'shattered_weapon'):
    #         if self.try_weapons_from_inventory(self.shattered_weapon):
    #             del self.shattered_weapon
    #             return

    #         if self.char.inventory.has(self.shattered_weapon):
    #             self.go_to_nearest_smithy()

    #             if self.repair_and_wield_broken_weapons(self.shattered_weapon):
    #                 del self.shattered_weapon
    #                 return

    #         self.go_buy_and_wield(self.shattered_weapon)
    #         del self.shattered_weapon
    #     # if hasattr(self, 'broken_weapon') or hasattr(self, 'shattered_weapon'):

