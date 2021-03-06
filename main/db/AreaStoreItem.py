from peewee import *
from db.BaseModel import *
from db.Item import *
from db.ItemType import *
from db.ItemTypeModel import *
from db.ItemTypeData import *
from db.Area import *
from misc_functions import *

class AreaStoreItem(BaseModel):
    area = ForeignKeyField(Area)
    item = ForeignKeyField(Item)

    '''Private AreaStoreItem Functions'''
    def map(self):
        is_new_mapping = False
        areastoreitem = AreaStoreItem.get_by_area_and_item(self.area.id, self.item.id)

        if areastoreitem is None:
            super(AreaStoreItem, self).save()
        else:
            self.id = areastoreitem.id
            self.area = areastoreitem.area
            self.item = areastoreitem.item
            #update other fields if you want

        return is_new_mapping

    def to_string(self):
        return str(self.id) + ", " + str(self.area.id) + ", " + str(self.item.name)

    '''Static AreaStoreItem Functions'''
    def get_by_area_and_item(areaid, itemid):
        try:
            areastoreitem = AreaStoreItem.select().where((AreaStoreItem.area == areaid) & (AreaStoreItem.item == itemid)).get()
        except AreaStoreItem.DoesNotExist:
            areastoreitem = None

        return areastoreitem

    def get_by_item(itemid):
        areastoreitem = AreaStoreItem.select().where(AreaStoreItem.item == itemid).get()

        return areastoreitem

    def get_by_item_type_and_level(model_name, data_name, level=1):
        # print("AreaStoreItem.get_by_item_type_and_level(): model_name: " + str(model_name) + ", data_name: " + str(data_name) + ", level: " + str(level))
        items = []
        # magentaprint("ItemTypeModel.get_by_name(model_name).get().id: " + ItemTypeModel.get_by_name(model_name).get().id)

        # print("AreaStoreItem ItemTypeModel.get_by_name(model_name).get().id: model_name: " + str(model_name) + ', data_name: ' + str(data_name))
        # print('AreaStoreItem ItemTypeModel: ' + str(ItemTypeModel))
        # print('AreaStoreItem ItemTypeModel get_by_name: ' + str(ItemTypeModel.get_by_name(model_name)))  
        # myitemtypemodel = ItemTypeModel.get_by_name(model_name)  
        # # print('AreaStoreItem itemtypemodel: ' + str(ItemTypeModel.get_by_name(model_name).get()))  # This one
        # print('AreaStoreItem itemtypemodel: ' + str(myitemtypemodel.get()))  # This one
        # print('AreaStoreItem itemtypemodel.id: ' + str(ItemTypeModel.get_by_name(model_name).get().id))
        itemtypemodel = ItemTypeModel.get_by_name(model_name).get().id
        # print('AreaStoreItem itemtypemodel: ' + str(itemtypemodel))

        itemtypedata = ItemTypeData.get_by_name(data_name).get().id
        # print('AreadStoreItem itemtypemodel: %s, itemtypedata: %s' % (str(itemtypemodel), str(itemtypedata)))

        # items = AreaStoreItem.select().join(Item).where(Item.level == level).join(ItemType).where(ItemType.model == itemtypemodel and ItemType.data == itemtypedata)
        items = AreaStoreItem.select().join(Item).where(Item.level == level).join(ItemType).where((ItemType.model==itemtypemodel) & (ItemType.data==itemtypedata))
        print("AreaStoreItem get_by_item_type_and_level returning " + str(items))

        return items

    def get_by_item_type_and_level_max(model_name, data_name, level_max=1):
        items = []
        itemtypemodel = ItemTypeModel.get_by_name(model_name).get().id
        itemtypedata = ItemTypeData.get_by_name(data_name).get().id
        print("AreaStoreItem get model_name/data_name: " + model_name + '/' + data_name + ", ids: " + str(itemtypemodel) + "/" + str(itemtypedata) )
        items = AreaStoreItem.select().join(Item).where(Item.level<=level_max).join(ItemType).where((ItemType.model==itemtypemodel) & (ItemType.data==itemtypedata))
        # obj = NamedModel.select().where(fn.Lower(NamedModel.name) == fn.Lower(name)).get()
        print("AreaStoreItem get_by_item_type_and_level_max returning " + str(items))
        return items

    def get_by_name(item_name):
        print("AreaStoreItem.get_by_name() item_name: " + str(item_name))
        items = AreaStoreItem.select().join(Item).where(Item.name == item_name)
        print("AreaStoreItem.get_by_name() returning: " + str(item_name))
        return items

    def get_by_area(aid):
        return AreaStoreItem.select().where(AreaStoreItem.area == aid)


