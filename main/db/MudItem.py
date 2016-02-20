
from peewee import *
from db.Database import *
from db.GenericMudObject import *
from misc_functions import magentaprint

class MudItem(GenericMudObject):
    def __init__(self, name):
        self.obj = Item(name=name)
        self.reference = self.obj.name.split(' ')[0]  # ... this reference is likely incorrect without an integer
        self.is_unusable = False

    def map(self):
        self.obj.map()

    def is_of_type(self, model_name, data_name, level=-1):
        is_of_type = False

        if self.obj.itemtype is not None:
            if self.obj.itemtype.has_model_and_data(model_name, data_name):
                is_of_type = True
                if level != -1:
                    if self.obj.level is not None:
                        if self.obj.level is not level:
                            is_of_type = False
                    else:
                        is_of_type = False

        return is_of_type

    def get_suitable_item_of_type(model_name, data_name, level=1):
        magentaprint("MudItem.get_suitable_item_of_type() model: " + str(model_name) + ', data_name: ' + str(data_name) + ', level: ' + str(level))
        areastoreitems = AreaStoreItem.get_by_item_type_and_level(model_name, data_name, level)
        magentaprint("MudItem areastoreitems: " + str(areastoreitems))
        # magentaprint("MudItem found " + str(len(areastoreitems)) + " items.")

        muditems = {}  
        for item in areastoreitems:
            magentaprint("MudItem loop item: " + str(item))
            muditems[item.area.id] = MudItem(item.item.name)  # keyed by area id apparently

        return muditems

    def get_purchase_location_id(self): #model to help track sizes
        magentaprint("MudItem get_purchase_location_id() self: " + str(self) + ", self.obj: " + str(self.obj) + ", obj.id: " + str(self.obj.id))
        return AreaStoreItem.get_by_item(self.obj.id).area.id

    @property
    def name(self):
        return self.obj.name

# class MudItemMeta():
#     def __init__(self, id, is_unusable=False):
#         self.id = id
#         self.is_unusable = is_unusable
