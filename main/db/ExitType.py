from peewee import *
from db.BaseModel import *
from db.NamedModel import NamedModel
from misc_functions import *

class ExitType(NamedModel):

    '''Private Area Functions'''
    def map(self):
        is_new_mapping = False

        exit_type = ExitType.get_exit_type_by_name(self.name)

        if (exit_type is None): #in this case we've discovered a new exit
            super(ExitType, self).save()
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
            #magentaprint("matching exit to: " + str(name))
            exit_types = ExitType.select().join(ExitSynonym, JOIN.LEFT_OUTER).where((ExitType.name == name) | (ExitSynonym.name == name) ).get()
            #magentaprint("matched exit to: " + exit_types.to_string())
        except ExitType.DoesNotExist:
            #print("Could not find exit Type with name: " + name, False)
            exit_types = None

        # print("Matched exit given: " + str(name) + ", to: " + str(exit_types))
        return exit_types

    def get_exit_type_by_name_and_opposite(name, exit_id): #this should always be unique
        exit_types = None

        try:
            exit_types = ExitType.select().join(ExitOpposite).where((ExitType.name == name) & (ExitOpposite.exit.name == name)).get()

        except ExitType.DoesNotExist:
            exit_types = None

        return exit_types

class ExitOpposite(BaseModel):
    exit = ForeignKeyField(ExitType, related_name='exit_to')
    opposite = ForeignKeyField(ExitType, related_name='exit_from')

class ExitSynonym(BaseModel):
    name = CharField()
    exit = ForeignKeyField(ExitType, null=True)