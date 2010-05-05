import unittest
from main.misc_functions import make_list_sellable

class misc_functionsTest(unittest.TestCase):

    def test_make_list_sellable_charecterizationTest(self):
        #setup
        input1 = ['candy cane', 'cleaning rags', 'large bag', 'large bag', 'large bag', 'lasso', 'leaf blade', 'leaf blade', 'leaf blade', 'leaf blade', 'silver chalice', 'silver chalice', 'silver chalice', 'silver chalice', 'silver chalice', 'silver snuff box', 'small restorative', 'small restorative', 'small restorative', 'small restorative', 'small restorative', 'spear', 'spear', 'spear', 'spear', 'spear', 'steel bottle', 'steel bottle', 'steel bottle', 'steel bottle', 'steel bottle', 'stilletos.', 'stilletos.']

        input2 = ["large bag", "large sack", "silver chalice", "steel bottle", "bag", "adamantine sword", 'adamantine axe', "claymore", "poison ring", "spider leg", "scimitar", "small restorative", "spear", "bolos", 'javelin', "leaf blade", "short bow", "heathen amulet", "hard cap", "hard gloves", "hard boots", "panteloons", "travellers cross", "leather mask", "leather collar", "studded leather collar", "mountain boots with crampons", "mountain gloves", "chain mail armour", 'chain mail sleeves', 'chain mail leggings', 'chain mail gloves', 'chain mail hood', 'chain mail boots', "ring mail armour", "ring mail sleeves", "ring mail leggings", "ring mail hood", "ring mail gauntlets", "leather collar", "furry cloak", "white amulet", "white potion", "stilleto", 'rapier', 'heavy crossbow', 'lion charm', 'glowing potion', 'war hammer'] 
        
        #execute
        result = make_list_sellable(input1, input2)
        #assert
        self.assertEquals(['cane', 'rags', 'lasso', 'snuff', 'stilletos.', 'stilletos.'] , result)
        # hmm, on this one there are multiple allowable outputs 
        # and I'm not sure how to allow for that
        
    def test_make_list_sellable_whenTheSecondWordHasANameCollision(self):
            
        input1 = ['candy cane', 'cleaning rags', 
                  'small knife', 'hand knife',
                  'silver chalice', 'silver snuff box']
        
        input2 = ["large bag", "large sack", "silver chalice", "steel bottle", "bag", "adamantine sword", 'adamantine axe', "claymore", "poison ring", "spider leg", "scimitar", "small restorative", "spear", "bolos", 'javelin', "leaf blade", "short bow", "heathen amulet", "hard cap", "hard gloves", "hard boots", "panteloons", "travellers cross", "leather mask", "leather collar", "studded leather collar", "mountain boots with crampons", "mountain gloves", "chain mail armour", 'chain mail sleeves', 'chain mail leggings', 'chain mail gloves', 'chain mail hood', 'chain mail boots', "ring mail armour", "ring mail sleeves", "ring mail leggings", "ring mail hood", "ring mail gauntlets", "leather collar", "furry cloak", "white amulet", "white potion", "stilleto", 'rapier', 'heavy crossbow', 'lion charm', 'glowing potion', 'war hammer']
        
        result = make_list_sellable(input1, input2)
        #assert
        # Also acceptable:
        #self.assertEquals(['cane', 'rags', 'knife', 'hand', 'snuff'] , result)
        self.assertEquals(['cane', 'rags', 'knife', '', 'hand', 'snuff'] , result)
        
    def test_make_list_sellable_whenAllWordsAreUsedEarlier(self):
        
        input1 = ['candy cane', 'cleaning rags', 
                  'large bag', 'small bag', 'hand knife', 'small knife', 
                  'silver chalice', 'silver snuff box']
        
        input2 = []
        
        result = make_list_sellable(input1, input2)
        
        self.assertEquals(['cane', 'rags', 'bag', '', 'small', 'knife', '', 'chalice', 'snuff'] , result)
        #TBD
        #self.assertEquals(['silver 2', 'small 2', 'hand', 'small', 'large'] , result)
            
    def test_make_list_sellable_whenAllWordsAreUsedLater(self):
        
        input1 = ['candy cane', 'cleaning rags', 
                  'large bag', 'small bag', 'hand knife', 'small knife', 'large hat',
                  'silver chalice', 'silver snuff box']
        
        input2 = []
        
        result = make_list_sellable(input1, input2)
        
        self.assertEquals(['cane', 'rags', 'bag', '', 'small', 'knife', '', 'hat', 'chalice', 'snuff'] , result)
        #TBD
        #self.assertEquals(['silver 2', 'small 2', 'hand', 'small', 'large'] , result)
