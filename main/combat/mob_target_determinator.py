
# from main.misc_functions import magentaprint

from print_magenta import magentaprint
from reactions.referencing_list import ReferencingList

class MobTargetDeterminator(object):
    # TODO: the wrong enemy could still be engaged when an enemy arrives immediately after the kill command is sent
    def on_mob_arrival(self, old_target_reference, arrived_mobs, mob_list):
        # magentaprint("MobTargetDeterminator old ref: " + str(old_target_reference))
        # Argh I'm worried about race condition.... 'bandit' wasn't in the list
        if old_target_reference:
            prev_mob_list = ReferencingList(mob_list.list) # not yet previous mob list
            prev_mob_list.remove_from_list(arrived_mobs) # Simulate the pre-arrival list to determine the intended target
            # So that removed the bandit sentry?
            old_target_name = str(prev_mob_list.get(old_target_reference)) # bandit sentry?

            if old_target_name:
                if arrived_mobs[0] < old_target_name and any([s.startswith(old_target_reference.split()[0]) for s in arrived_mobs[0].split(' ')]):
                    magentaprint("MobTargetDeterminator old/new ref: %s/%s" % \
                        (str(old_target_reference), 
                        str(self.increment_ref(old_target_reference, len(arrived_mobs)))))
                    new_target= self.increment_ref(old_target_reference, len(arrived_mobs))
                else:
                    # magentaprint("MTD decided not to change target reference")
                    new_target= old_target_reference
            else:
                magentaprint("MTD couldn't figure out previous target(!)")
                new_target= old_target_reference
        else:
            magentaprint("MTD wasn't given a previous reference to work with(!)")
            new_target= old_target_reference
        magentaprint("MTD called for target: {}, current mobs.list: {}, arrivals: {}. New_target: {}.".format(old_target_reference, mob_list.list, arrived_mobs, new_target))
        return new_target
        # Ok an issue was that the bandit sentry wasn't in the old list since he was hiding at first
        # Erhm did MTD fail here??? Target act 2 (an actress)... "An actor just arrived" (half-word example) Why would that not work??

    def on_mob_departure(self, old_target_reference, old_mob_referencing_list, departed_mob_ref):
        # old_mob_referencing_list is what the list was before some mob wandered off (includes mob that wandered off in it)
        if old_target_reference:
            # prev_mob_list = ReferencingList(old_mob_referencing_list.list) # ok it's not previous list yet
            # prev_mob_list.add(departed_mob_ref) # ok now it is 
            # old_target_name = str(prev_mob_list.get(old_target_reference))
            # Ehrm need to make sure the departed mob is in the list!

            # target_name       = str(old_mob_referencing_list.get(old_target_reference))
            index_of_target = old_mob_referencing_list.index(old_target_reference)

            # if (departed_mob_name < target_name and any([s.startswith(old_target_reference.split()[0]) for s in departed_mob_name.split(' ')])) or \
                # (departed_mob_name == target_name and departed_mob_ref < old_target_reference):

            index_of_departed_mob = old_mob_referencing_list.index(departed_mob_ref)
            # departed_mob_name = str(old_mob_referencing_list.get(departed_mob_ref))
            if index_of_departed_mob == None or index_of_target == None:
                return old_target_reference
            departed_mob_name = str(old_mob_referencing_list.list[index_of_departed_mob])
            # if (departed_mob_name < target_name and any([s.startswith(old_target_reference.split()[0]) for s in departed_mob_name.split(' ')])) or \
            #     (departed_mob_name == target_name and departed_mob_ref < old_target_reference):
            if any([s.startswith(old_target_reference.split()[0]) for s in departed_mob_name.split(' ')]) and index_of_target > index_of_departed_mob:
                # (departed_mob_name == target_name and departed_mob_ref < old_target_reference):
                # (If departed mob is alphabetically before our target and has the same word in it that we are using to target...)
                # Or if they have the same name but number 1st left while we are targeting number 3) (Edge case!)
                magentaprint("MobTargetDeterminator new ref: " + str(self.decrement_ref(old_target_reference)))
                return self.decrement_ref(old_target_reference)
            else:
                # old target reference is fine (ie. departed_mob_name > target_name)
                return old_target_reference
        else:
            return old_target_reference
            # Hmm do we really have to check "if old_target_reference"? I guess it's being defensive
            # I guess if we get notified, and we really have a target, the execution can just run through this

        # elif self.character.mobs.read_mob_name_from_regex_match(M_obj) < old_target_reference):
        # TODO: fix targetting when a mob of same name lower in stack arrives!!!! (When did I write this?? Wow!)
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
