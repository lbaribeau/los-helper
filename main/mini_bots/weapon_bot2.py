
import time
import re
# import threading
from misc_functions import *
from Exceptions import *
from comm import RegexStore as R
from combat.mob_target_determinator import MobTargetDeterminator
# from mini_bots.smithy_bot import SmithyBot
from mini_bots.travel_bot   import TravelBot
from mini_bots.shopping_bot import ShoppingBot
from mini_bots.mini_bot     import MiniBot
from mini_bots.shopping_bot import ShoppingBot
from db.Database            import AreaStoreItem

# Ok we want....
# If no weapons, buy TWO WEAPONS
# If one weapon, buy one weapon
# What offhand do we want... do we want to use up something available...
# Don't even bother - keep it simple - sell that one and only manage one weapon
# (Sell the throwing stars)
# Say user wielded something - then use that one... could use that one as offhand too, right?
# Yes...
# We could try fully populating the DB
# We don't want to go too expensive though
# Can we untie the shield part and make that armour? No we do want dual wield, right?
# Let ruorg use a crossbow...
# So he'll carry two crossbows and 4 throwing stars
# No two crossbows and just the plussed throwing stars
# How do we decide whether to use a shield? 
# Just always use a shield and a one-hand (keep it simple)
# Have a list of acceptable weapons... do we use the DB to decide?
# Just hardcode it?
# Write some logic like, if we can buy level 2, don't use level 1
# If we are wielding something, assume it's fine.
# Save it to repair it.
# Choose a weapon when the smithy breaks it.
# We are just avoiding unarmed combat here.
# Could we repair something in terrible condition?
# How do we make sure one weapon is good
# So first we need to be able to check the inventory for the weapon.
# Ok so on init... 
# Make sure we have our one-hand and our shield on
# And we have an offhand in the bag
# Not init but check_weapons

# So, we just need, wielding something, and something available in the bag
# Ideally in good condition
# Shattering can always happen
# But having something available in the bag will be way less scary than just having one wepon
# So, who uses who here...
# It would be nice to have the wield command tell us what's going on
# But maybe we don't need it
# Nevermind logic for temp weapon

# I want to simplify this... I want to guarantee we have a replacement weapon in the bag

# class MainhandWeaponBot(MiniBot, threading.Event):
class MainhandWeaponBot(MiniBot):
    def __init__(self, character, command_handler):
        super().__init__()
        self.character = character
        self.inventory = character.inventory
        self.command_handler = command_handler
        self.weapon_check_cooldown = 10
        self.last_weapon_check_time = None
        # self.simple_weapon_bot = simple_weapon_bot

        self.actions = {
            # R.you_wield: (lambda self, match : self.weapon = match.group('weapon')),
            # R.off_hand: (lambda self, match : self.second = match.group('weapon')),
            # R.weapon_break: lambda match : if
            R.you_wield[0]:       self.react_to_wield,
            R.weapon_break[0]:    self.react_to_weapon_break, # Can be repaired
            R.weapon_shatters[0]: self.react_to_weapon_break, # Is destroyed
            # R.shield[0]:          self.set_shield_or_offhand
            # R.off_hand[0]:        self.react_to_off_hand,
        }
        # self.regex_cart = self.actions.keys()
        self.regex_cart = [
            R.you_wield, 
            R.weapon_break, 
            R.weapon_shatters, 
            # R.off_hand, 
            # R.shield
        ]
        self.possible_weapons = []

    # Inventory keeps track of if a weapon is broken in the inventory

    def add_in_map(self, mud_map):
        # Methods which require navigation or knowing possible weapons to wield require this to be called
        # self.smithy_bot   = SmithyBot(self.character, self.command_handler, mud_map)
        self.travel_bot   = TravelBot(self.character, self.command_handler, mud_map)
        self.shopping_bot = ShoppingBot(self.character, self.command_handler, mud_map)

    def notify(self, regex, match):
        self.actions[regex](match)
        # super().notify() # Event

    def react_to_wield(self, match):
        if match.group('weapon').endswith('in your off hand'):
            pass
        else:
            self.weapon = match.group('weapon')

    def react_to_weapon_break(self, match):
        # if hasattr(self, 'weapon') and self.weapon == match.group('weapon'):
        if hasattr(self, 'weapon'):
            # Assume main hand (this bot is not supporting dual wield)
            del self.weapon

    def weapon_removed(self):
        if hasattr(self, 'weapon'):
            del self.weapon

    def run(self):
        self.stopping = False
        self.check_weapons()

    def has_weapon_wielded(self):
        return hasattr(self, 'weapon')
    # def needs_weapon(self):
    #     #return not self.has_weapon()
    #     return not (self.has_weapon() and self.has_weapon_in_inventory())
    def needs_to_shop(self):
        if self.has_weapon_wielded():
            return self.count_weapons_in_inventory()==0
        else:
            return self.count_weapons_in_inventory()<2
    # def has_weapon_in_inventory(self):
    #     # return self.command_handler.inventory.
    #     # Maybe keep it in a sack if not the keep_list
    #     # We have to rewield in combat
    #     # if any([p in self.command_handler.inventory.list for p in self.get_possible_weapons()]):
    #     return self.count_weapons_in_inventory() > 0
    def count_weapons_in_inventory(self):
        return sum([self.command_handler.inventory.list.count(p.item.name) for p in self.get_possible_weapons()])
    def has_broken_weapon_in_inventory(self):
        return any([self.command_handler.inventory.has_broken(p.item.name) for p in self.get_possible_weapons()])
    def has_usable_weapon_in_inventory(self):
        # Ehrm can we start doing "looks" here in case we can't maintain is_usable
        return any([self.command_handler.inventory.has_unbroken(p.item.name) for p in self.get_possible_weapons()])
    def look_at_each_possible_weapon(self):
        for w in self.get_possible_weapons():
            for r in self.command_handler.inventory.get_all_references(w.item.name):
                self.command_handler.look.execute_and_wait(r)
    def get_usable_weapon_ref(self):
        if not self.has_usable_weapon_in_inventory():
            return None
        p_list = self.get_possible_weapons()
        weapon = p_list[[self.command_handler.inventory.has_unbroken(p.item.name) for p in p_list].index(True)].item.name
        return self.inventory.get_unbroken(weapon)
    def get_broken_weapon_ref(self):
        if not self.has_broken_weapon_in_inventory():
            return None
        p_list = self.get_possible_weapons()
        weapon = p_list[[self.command_handler.inventory.has_broken(p.item.name) for p in p_list].index(True)].item.name
        return self.inventory.get_broken(weapon)
    def needs_smithy(self):
        return self.has_broken_weapon_in_inventory() and not self.has_unbroken_weapon_in_inventory()

    def should_check_weapons(self):
        now = get_timeint()
        should_do_thing = False

        if not self.last_weapon_check_time:
            self.last_weapon_check_time = now
            should_do_thing = True
        else:
            seconds_since_last_check = (now - self.last_weapon_check_time).total_seconds()
            if seconds_since_last_check > self.weapon_check_cooldown:
                self.last_weapon_check_time = now
                should_do_thing = True
        return should_do_thing

    def check_weapons(self):
        if not self.should_check_weapons():
            # magentaprint("Already checked weapons recently in the last " + str(self.weapon_check_cooldown) + " seconds.", False)
            return 0
        
        self.get_possible_weapons()
        self.look_at_each_possible_weapon()
        if self.possible_weapons[0].item.name not in self.inventory.keep_list:
            self.inventory.keep_list.append(self.possible_weapons[0].item.name)
            magentaprint("Weapon bot added {0} to inventory keep list, {1}".format(self.possible_weapons[0].item.name, self.possible_weapons[0].item.name in self.inventory.keep_list))
        if not hasattr(self, 'weapon'):
            if self.has_usable_weapon_in_inventory():
                wield = self.command_handler.wield
                usable_ref = self.get_usable_weapon_ref()
                # self.clear()
                wield.execute_and_wait(usable_ref)
                # self.wait(timeout=5) # We don't have notify on every possible wield result
                if wield.success:
                    self.weapon = wield.M_obj.group('weapon')
                    self.check_weapons()
                elif wield.result in R.already_wielding:
                    magentaprint("Error case checking weapons, not sure what is wielded.")
                    if not hasattr(self, 'weapon'):
                        self.weapon='notsure'
                elif wield.result in R.weapon_broken:
                    magentaprint("check_weapons spotted broken weapon.")
                    self.inventory.get(usable_ref).usable = False
                    self.check_weapons() # Mark it as broken 
                elif wield.result in R.dont_have:
                    magentaprint("Error case checking weapons, expected {0}, removing.".format(usable_ref))
                    self.inventory.remove_by_ref(usable_ref)
                    self.check_weapons() # Square one (check for usable in inventory)
                else:
                    magentaprint("Check weapons unexpected else, wield result is {0}".format(wield.result))
                    # Maybe easier to just spam wield on our entire inventory
            elif self.has_broken_weapon_in_inventory():
                repair = self.command_handler.repair
                self.travel_bot.go_to_nearest_smithy(grinding=False)
                weapon = self.get_broken_weapon_ref()
                repair.execute_and_wait(weapon)
                if repair.success or repair.failure:
                    # Repair is in charge of updating inventory, so we know that's done
                    self.check_weapons() # This will wield it 
                elif repair.result in R.dont_have:
                    magentaprint("Error case checking weapons, expected {0}, removing.".format(usable_ref))
                    self.inventory.remove_by_ref(usable_ref)
                    self.check_weapons() # Error: remove it and go back to square one
                elif repair.result in R.no_gold:
                    magentaprint("Check weapons saw no gold to repair.")
                    return
                else:
                    magentaprint("Check weapons repairing problem")
                    raise
            else:
                self.go_buy_default_weapon()
                self.check_weapons() # Wield, buy secondary
        else:
            if self.has_usable_weapon_in_inventory():
                return 0
            elif self.has_broken_weapon_in_inventory():
                repair = self.command_handler.repair
                self.travel_bot.go_to_nearest_smithy(grinding=False)
                weapon = self.get_broken_weapon_ref()
                repair.execute_and_wait(weapon)
                if repair.success:
                    return 0
                elif repair.failure:
                    self.check_weapons() # Maybe there's another to try repairing
                elif repair.result is R.dont_have:
                    magentaprint("Error case checking weapons, expected {0}, removing.".format(usable_ref))
                    self.inventory.remove_by_ref(usable_ref)
                    self.check_weapons()
                elif repair.result is R.no_gold:
                    magentaprint("Check weapons saw no gold to repair.")
                    return
                else:
                    magentaprint("Check weapons repairing problem")
                    raise
                    # This could be a db error
            else:
                return self.go_buy_default_weapon()

        # if self.needs_weapon():
        #     if self.has_weapon_in_inventory():

        # elif self.broken_weapon:
        #     self.repair_or_replace_weapon()
        # elif hasattr(self, 'weapon') and self.shield_or_offhand:  # ArmourBot or eq should be called first...
        #     return
        # else:
        #     self.repair_or_replace_weapon()

    def go_buy_default_weapon(self):
        # magentaprint("WeaponBot.go_buy_default_weapon()")
        # magentaprint("WeaponBot.go_buy_replacement() calling shopping_bot.go_buy " + str(self.get_possible_weapons()[0]))
        # if self.possible_weapons[0] not in self.shopping_bot.keep_list:
        #     self.shopping_bot.keep_list.add(self.possible_weapons[0])
        # I think we want to alleviate inventory of the keep list

        if self.shopping_bot.go_buy(self.possible_weapons[0]):
            return True
        else:
            if hasattr(self, 'weapon'):
                magentaprint("Warning: WeaponBot could not buy another weapon")
            else:
                # raise Exception("WeaponBot couldn't buy main weapon.")
                magentaprint("WeaponBot couldn't buy main weapon.")  # We won't exit here - maybe the bot will sell/drop then return
            return False

    def combat_rewield(self):
        # Should have a weapon ready
        # self.command_handler
        # self.try_exact_replacement_from_inventory() # Is this more robust? Maybe
        # Well we should pick out one that is usable
        # (We don't want to have to worry about which one will be rewieled)
        if self.has_usable_weapon_in_inventory():
            # We'd better have something
            self.command_handler.wield.execute(self.get_usable_weapon_ref())
            # Assume that worked
            # NO WHAT IF THE FIRST ONE IS BROKEN
            # It can happen apparently
            # So... let's try blocking calls here? Is this called in a notify?
            # So get_usable was WRONG somehow
            # This happens IN SmartCombat.notify
            # So we can't do any waiting calls
            # Because MudReaderThread is calling this
            # So we can't hang and expect another notify
            # What if we passed the baton to the smartCombat run
            # Since it'd be nice to get feedback on this rewield
            # Not sure what happened to is_usable

        else:
            # Try weapon bot 1?
            # Try one of the functions below from weapon bot 1?
            if not self.try_exact_replacement_from_inventory():
                self.try_other_possible_weapons_in_inventory()

    ###--- I don't think I use anything below (from weapon bot 1) ---###

    def repair_or_replace_weapon(self):
        self.command_handler.equipment.execute_and_wait()
        if hasattr(self, 'weapon') and self.shield_or_offhand:
            magentaprint("WeaponBot.repair_or_replace_weapon() has weapon and shield/offhand so return.")
            return
        elif not self.shield_or_offhand:
            magentaprint("WeaponBot needs to figure out whether to buy an offhand - assume shield.")
            return

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

    def try_default_replacement_from_inventory(self):
        magentaprint('try_default_replacement_from_inventory')
        return self.try_weapons_from_inventory(self.get_possible_weapons()[0].item.name)

    def try_weapon_list_from_inventory(self, l):
        magentaprint('try_weapon_list_from_inventory')
        for w in l:
            if self.try_weapons_from_inventory(w):
                return w

    def try_rewielding_each_in_inventory(self, command_object, weapon_name):
        ref = self.character.inventory.get_reference(weapon_name, 2)

        while self.character.inventory.get(ref) and self.character.inventory.get(ref).obj.name == weapon_name:
            if self.character.inventory.get(ref).usable:
                command_object.execute_and_wait(ref)

                if command_object.success:
                    return True
                else:
                    self.character.inventory.set_broken(ref)

            ref = MobTargetDeterminator().increment_ref(ref)

        return False

        # If offhand breaks, we need to try one wield and then correct our variables once we learn which broke of mainhand/offhand

    # def go_replace_weapon(self, w):
    #     self.go_buy_and_wield(self.shattered_weapon)
    #     del self.shattered_weapon

    #     bw = self.broken_weapon
    #     del self.broken_weapon
    #     self.go_buy_and_wield(bw)

    def rewield(self, weapon_ref):
        weapon_name = self.character.inventory.name_from_reference(weapon_ref)
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
            raise Exception("WeaponBot.rewield() wield error!")

    def try_weapons_from_inventory(self, weapon_name):
        magentaprint('try_weapons_from_inventory')
        if hasattr(self, 'weapon'):  # We know that the offhand broke
            magentaprint("WeaponBot.try_weapons_from_inventory() but weapon is already set to " + self.weapon + '!')
            if self.try_reequipping_offhand(weapon_name):
                # self.second = w  # let the reaction do it
                return True
        else:
            ref = self.character.inventory.get_first_reference(weapon_name)
            magentaprint("WeaponBot.try_weapons_from_inventory() weapon name/ref: " + str(weapon_name) + "/" + str(ref))

            # while ref and self.character.inventory.get(ref).obj.name == weapon_name:  # ??? Should work, but had get return None after broken weapon.
            while ref and self.character.inventory.get(ref) and self.character.inventory.get(ref).obj.name == weapon_name:
                if self.character.inventory.get(ref).usable:
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
                        self.character.inventory.unset_usable(ref)
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


    # def try_exact_replacement_from_inventory(self):
    #     self.simple_weapon_bot.try_exact_replacement_from_inventory()

    # def try_weapon_list_from_inventory(self, l):
    #     self.simple_weapon_bot.try_weapon_list_from_inventory(self, l)

    @property
    def should_go_to_smithy(self):
        return (not hasattr(self, 'weapon') or self.temporary_weapon) and \
            (self.character.inventory.has_any_broken(self.broken_weapon) or \
                self.character.inventory.has_broken(self.get_possible_weapons[0].item.name))

    def try_exact_replacement_from_inventory_with_possible_smithy_trip(self):
        magentaprint("WeaponBot.try_exact_replacement_from_inventory()")
        if self.character.inventory.has_any(self.broken_weapon) and not self.stopping:
            # self.smithy_bot.go_to_nearest_smithy()
            self.travel_bot.go_to_nearest_smithy()
            wielded_weapon = self.try_weapon_list_from_inventory_in_smithy(self.broken_weapon)
            if wielded_weapon:
                self.broken_weapon.remove(wielded_weapon)
                return wielded_weapon

    def try_default_replacement_from_inventory_with_possible_smithy_trip(self):
        magentaprint("WeaponBot.try_default_replacement_from_inventory_with_possible_smithy_trip()")
        if self.character.inventory.has(self.get_possible_weapons()[0].item.name) and not self.stopping:
            # self.smithy_bot.go_to_nearest_smithy()
            self.travel_bot.go_to_nearest_smithy()
            # return self.try_weapons_from_inventory(self.possible_weapons[0].item.name)
            return self.try_weapon_list_from_inventory_in_smithy([self.possible_weapons[0].item.name])
        else:
            magentaprint("has(%s) returned False" % str(self.get_possible_weapons()[0].item.name))

    def try_weapon_list_from_inventory_in_smithy(self, l):
        for w in l:
            while self.character.inventory.has(w) and not self.stopping:
                magentaprint("WeaponBot in smithy " + str(w))

                if self.repair_one(w):
                    self.rewield(self.character.inventory.get_last_reference(w))
                    return w

    def repair_one(self, name):
        ref = self.character.inventory.get_last_reference(name)
        self.command_handler.repair.execute_and_wait(ref)
        if self.command_handler.repair.success:
            self.character.inventory.set_usable(ref)
            return True
        else:
            self.character.inventory.remove_by_ref(ref)
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
            return self.weapon == self.get_possible_weapons()[0].item.name
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
            while self.character.inventory.has(w.item.name) and not self.stopping:
                if self.try_weapons_from_inventory(w.item.name):
                    return True

                # self.smithy_bot.go_to_nearest_smithy()
                self.travel_bot.go_to_nearest_smithy()

                if self.repair_one(w.item.name):
                    self.rewield(self.character.inventory.get_last_reference(w.item.name))
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

    def get_store_path(self):
        return self.map.get_path(self.character.AREA_ID, self.get_possible_weapons()[0].area.id)

    def wield_default_weapon(self):
        self.rewield(self.character.inventory.get_last_reference(self.possible_weapons[0].item.name))

    @property
    def possible_weapons_in_inventory(self):
        return self.character.inventory.get_all_by_name_list([asi.item.name for asi in self.get_possible_weapons()])

    def correct_temp_weapon(self):
        magentaprint("WeaponBot.correct_temp_weapon")
        # We wielded a weapon in combat, so we should now wield a default weapon and ensure we have a backup
        if self.default:
            magentaprint('default')
            magentaprint("self.character.inventory.has_any([w.item.name for w in self.get_possible_weapons()]: " + str(self.character.inventory.has_any([w.item.name for w in self.get_possible_weapons()])))

            # if self.get_possible_weapons()
            # usable_possible_weapons_in_inv = any(x.usable for x in possible_weapons_in_inventory)
            # if self.character.inventory.get_all_by_name_list([asi.item.name for asi in self.get_possible_weapons()]) and \
            #    any([x.usable for x in self.character.inventory.get_all_by_name_list([asi.item.name for asi in self.get_possible_weapons()])]):
# [asi.item.name for asi in self.get_possible_weapons()])):

            # if possible_weapons_in_inventory and any(x.usable for x in possible_weapons_in_inventory):
            #     pass
            # elif self.character.inventory.has_any([w.item.name for w in self.get_possible_weapons()]):
            # possible_weapons_in_inventory = self.character.inventory.get_all_by_name_list([asi.item.name for asi in self.get_possible_weapons()])
            if self.possible_weapons_in_inventory:
                if any(x.usable for x in possible_weapons_in_inventory):
                    pass
                else:
                    magentaprint('Ensure that one is usable to serve as the backup')
                    for w in self.get_possible_weapons():
                        while self.character.inventory.has(w.item.name) and not self.stopping:
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
            while self.character.inventory.has(self.get_possible_weapons()[0].item.name) and not self.stopping:
                # magentaprint('Not wielding default (?): ' + str(self.weapon) + '/' + str(self.possible_weapons()[0]))
                # Preferred case (backup weapon was different)
                magentaprint("self.character.inventory.has(?): " + str(self.get_possible_weapons()[0].item.name))
                magentaprint(str(self.character.inventory))
                # while self.character.inventory.has(self.get_possible_weapons()[0].item.name):  # Done in repair
                self.go_to_nearest_smithy()
                # if self.repair(self.character.inventory.get_last_reference(self.get_possible_weapons()[0].item.name)):
                if self.repair_one(self.get_possible_weapons()[0].item.name):
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
        # if hasattr(self, 'smithy_bot'):
        if hasattr(self, 'travel_bot'):
            # self.smithy_bot.stop()
            self.travel_bot.stop()
            self.shopping_bot.stop()

    # def go_repair(self):
    #     if hasattr(self, 'broken_weapon'):
    #         if self.try_weapons_from_inventory(self.broken_weapon):
    #             del self.broken_weapon
    #             return

    #         if self.character.inventory.has(self.broken_weapon):
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
    #     weapon_ref = self.character.inventory.get_first_reference(full_weapon_name)
    #     while self.character.inventory.get(weapon_ref).obj.name == full_weapon_name:
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

    def get_possible_weapons(self):
        if self.possible_weapons:
            magentaprint("WeaponBot possible weapons: " + str([w.item.name for w in self.possible_weapons]))
            return self.possible_weapons
        elif not hasattr(self, 'travel_bot'):
            magentaprint("WeaponBot: Warning: get_possible_weapons() was called before init_with_map.")
            return None
        else:
            # self.possible_weapons = AreaStoreItem.get_by_item_type_and_level_max('weapon', self.character.weapon_type, self.character.weapon_level)
            # self.possible_weapons = sorted(self.possible_weapons, key = lambda i: i.item.level, reverse=True)
            # Strict about level
            self.possible_weapons = AreaStoreItem.get_by_item_type_and_level('weapon', self.character.weapon_type, self.character.weapon_level)
            magentaprint("WeaponBot possible weapons: " + str(self.possible_weapons))
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
    #         paths = self.db_handler.get_smithy_paths(self.character.AREA_ID)
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

    #         if self.character.inventory.has(self.broken_weapon):
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

    #         if self.character.inventory.has(self.shattered_weapon):
    #             self.go_to_nearest_smithy()

    #             if self.repair_and_wield_broken_weapons(self.shattered_weapon):
    #                 del self.shattered_weapon
    #                 return

    #         self.go_buy_and_wield(self.shattered_weapon)
    #         del self.shattered_weapon
    #     # if hasattr(self, 'broken_weapon') or hasattr(self, 'shattered_weapon'):

