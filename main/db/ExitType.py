from peewee import *
from db.BaseModel import *
from db.NamedModel import NamedModel
from misc_functions import *

class ExitType(NamedModel):

    '''Private Area Functions'''
    def map(self):
        # This assumes "self" has ".name" set on it, and it'll add an entry to the DB if one doesn't exist
        # The "ExitType" table is a table of exit names, and there are indices, ie. "north" is 5
        # What this does is saves a new entry if .name draws a blank but if .name exists already then we get self.id set, which is a number associated with the exit text
        # ie. "north" is exit number 5... every "north" points to the same record... because the db needs it to be a number
        is_new_mapping = False

        exit_type = ExitType.get_exit_type_by_name(self.name)

        if (exit_type is None): #in this case we've discovered a new exit
            super(ExitType, self).save() # BaseModel intercepts this to implemnent "-fake" test environment but otherwise this is peewee.Model "save"
            # Presumably and ID is assigned and whatever is in ".name" is written into the table
            is_new_mapping = True
            return is_new_mapping
        else:
            self.id = exit_type.id

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + self.name

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    '''Static ExitType Functions'''
    def get_exit_type_by_name(name): #this should always be unique
        exit_types = None

        try:
            exit_types = ExitType.select().where((ExitType.name == name)).get()
        except ExitType.DoesNotExist:
            #magentaprint("Could not find exit Type with name: " + name, False)
            exit_types = None

        return exit_types

    def get_exit_type_by_name_or_shorthand(name):
        exit_types = None

        #print("Finding exit from given argument: " + str(name))
        try:
            #exit_types = ExitType.select().join(ExitSynonym, JOIN_LEFT_OUTER).where((ExitType.name == name) | (ExitSynonym.name == name) ).get() # worked in 2016, now bad identifier
            #exit_types = ExitType.select().join(ExitSynonym, join_type='LEFT_OUTER').where((ExitType.name == name) | (ExitSynonym.name == name) ).get() # syntax error
            exit_types = ExitType.select().join(ExitSynonym, JOIN.LEFT_OUTER).where((ExitType.name == name) | (ExitSynonym.name == name) ).get() # 2022, works
        except ExitType.DoesNotExist:
            #print("Could not find exit Type with name: " + name, False)
            exit_types = None

        magentaprint("ExitType.py given parameter name: "+str(name))
        magentaprint("ExitType.py get_exit_type_by_name_or_shorthand() matched exit, given " + str(name) + ", to: " + str(exit_types))
        # raise # Gives a stack trace... mudReaderThread s.notify(r, match), cartography, notify, self.area(M), C.MUD_AREA= MudAea.map( (line 202), in map, MudArea.discern_location, in discern_location... (line 61 MudArea.py)
        return exit_types

    def get_exit_type_by_name_and_opposite(name, exit_id): #this should always be unique
        exit_types = None

        try:
            exit_types = ExitType.select().join(ExitOpposite).where((ExitType.name == name) & (ExitOpposite.exit.name == name)).get()

        except ExitType.DoesNotExist:
            exit_types = None

        return exit_types

# "ExitType" is the table of exits, ie, "north" is id 5, "south" is id 6
# Then "AreaExit" uses those index codes, ie, "north" (5) is used to go from area 4 to area 20

# These (ExitOpposite, ExitSynonym) don't seem to be used... DB has the table but no rows
# I think that the point for opposite was to understand how north and south mean the opposite but,
# there are places in the game where that is not true
# so why adopt it at all.

# Synonym is for, like, "n" is short for "north", "ou" works as a short form for "out"
# So the code might want recognize that equivalence to understand what happened when "n" was typed

class ExitOpposite(BaseModel):
    exit = ForeignKeyField(ExitType, related_name='exit_to')
    opposite = ForeignKeyField(ExitType, related_name='exit_from')

class ExitSynonym(BaseModel):
    name = CharField()
    exit = ForeignKeyField(ExitType, null=True)
