
# from main.misc_functions import magentaprint

from main.print_magenta import magentaprint
from main.reactions.referencing_list import ReferencingList

class MobTargetDeterminator(object):
    def on_mob_arrival(self, old_target_reference, arrived_mobs, mob_list):
        magentaprint("MobTargetDeterminator old ref: " + str(old_target_reference))
        if old_target_reference:
            prev_mob_list = ReferencingList(mob_list.list)
            prev_mob_list.remove_from_list(arrived_mobs)
            old_target_name = str(prev_mob_list.get(old_target_reference))

            if old_target_name:
                if arrived_mobs[0] < old_target_name and any([s.startswith(old_target_reference.split()[0]) for s in arrived_mobs[0].split(' ')]):
                    magentaprint("MobTargetDeterminator new ref: " + str(self.increment_ref(old_target_reference, len(arrived_mobs))))
                    return self.increment_ref(old_target_reference, len(arrived_mobs))
                else:
                    return old_target_reference
            else:
                return old_target_reference
        else:
            return old_target_reference

    def on_mob_departure(self, old_target_reference, departed_mob_name, mob_list):
        if old_target_reference:
            prev_mob_list = ReferencingList(mob_list.list)
            prev_mob_list.add(departed_mob_name)
            old_target_name = str(prev_mob_list.get(old_target_reference))

            if old_target_name:
                if departed_mob_name < old_target_name and any([s.startswith(old_target_reference.split()[0]) for s in departed_mob_name.split(' ')]):
                    return self.decrement_ref(old_target_reference)
                else:
                    return old_target_reference
            else:
                return old_target_reference
        else:
            return old_target_reference

        # elif self.character.mobs.read_match(M_obj) < old_target_reference):
        # TODO: fix targetting when a mob of same name lower in stack arrives

    # def determine_if_ref_is_affected(self, )

    def increment_ref(self, ref, qty=1):
        if len(ref.split(' ')) > 1:
            return ref.split(' ')[0] + ' ' + str(int(ref.split(' ')[1]) + qty)  # ref++
        else:
            return ref + ' ' + str(qty + 1)

    def decrement_ref(self, ref):
        if len(ref.split(' ')) > 1:
            if int(ref.split(' ')[1]) > 2:
                return ref.split(' ')[0] + ' ' + str(int(ref.split(' ')[1]) - 1)
            else:
                return ref.split(' ')[0]
        else:
            magentaprint("SmartCombat.decrement_ref() can't decrement " + ref + '.')
            return ref
