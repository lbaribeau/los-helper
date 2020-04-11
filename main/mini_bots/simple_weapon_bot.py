class SimpleWeaponBot(object):
    ''' This bot is created because SmartCombat needs a rewield function that it wants someone else to handle.
    WeaponBot has to wait for the map, which rules it out.  This object is used by SmartCombat and WeaponBot.'''

    # I decided against doing this because I figured I'd just have WeaponBot's methods not work if it doesn't have the map...
    # I also made init not require the map and made the map add_in occur when the map was ready.

    def try_exact_replacement_from_inventory(self):
        wielded_weapon = self.try_weapon_list_from_inventory(self.broken_weapon)
        if wielded_weapon:
            self.broken_weapon.remove(wielded_weapon)

    def try_weapon_list_from_inventory(self, l):
        for w in l:
            if self.try_weapon_from_inventory(w):
                return w

    def try_rewielding(self, command_object, w):
        ref = self.char.inventory.get_reference(w, 2)

        command_object.execute_and_wait(ref)
        if command_object.success:
            return True

        while command_object.broken_error:
            self.char.inventory.set_broken(ref)
            ref = MobTargetDeterminator().increment_ref(ref)
            if self.char.inventory.get_item_name_from_reference(ref) == w:
                command_object.execute_and_wait(ref)
                if command_object.success:
                    return True
            else:
                return False

        # If offhand breaks, we need to try one wield and then correct our variables once we learn which broke of mainhand/offhand

    # def go_replace_weapon(self, w):
    #     self.go_buy_and_wield(self.shattered_weapon)
    #     del self.shattered_weapon

    #     bw = self.broken_weapon
    #     del self.broken_weapon
    #     self.go_buy_and_wield(bw)

    def rewield(self, weapon_ref):
        weapon_name = self.char.inventory.name_from_reference(weapon_ref)
        self.command_handler.smartCombat.wield.execute_and_wait(weapon_ref)
        if not self.command_handler.smartCombat.wield.success:
            self.command_handler.smartCombat.wield.second.execute_and_wait(weapon_ref)
            if not self.command_handler.smartCombat.wield.second.success:
                raise Exception("Couldn't rewield!")
            else:
                self.second = weapon_name
        else:
            self.weapon = weapon_name

    def try_weapon_from_inventory(self, w):
        if self.char.inventory.has(w):
            if hasattr(self, 'weapon'):  # We know that the offhand broke
                if self.try_reequipping_offhand(w):
                    self.second = w
                    return True
            else:
                self.command_handler.smartCombat.wield.execute_and_wait(self.char.inventory.get_reference(w, 2))
                # Should skip unusable items

                if self.command_handler.smartCombat.wield.result in R.already_wielding:
                    if self.second:
                        self.weapon = self.second
                        del self.second
                        self.shield_or_offhand = False
                        self.try_weapon_from_inventory(w)
                    else:
                        raise Exception("TopDownGrind.try_weapons confusion.")
                elif self.command_handler.smartCombat.wield.result in R.weapon_broken:
                    self.char.inventory.unset_usable(self.char.inventory.get_reference(w, 2))
                elif self.command_handler.smartCombat.wield.success:
                    return True
                else:
                    pass
                    # magentaprint("WeaponBot.try_weapon_from_inventory() tried " + str(w))
                    # if self.try_reequipping_mainhand(w):
                    #     self.weapon = w
                    #     return True

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
        if not self.try_exact_replacement_from_inventory():
            self.try_other_possible_weapons_in_inventory()
        self.temporary_weapon = True

