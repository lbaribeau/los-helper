###############################################################################

import unittest
from main.misc_functions import extract_sellable_and_droppable

class misc_functionsTest(unittest.TestCase):

    def test_extract_sellable_and_droppable_characterizationTest(self):
        #setup
        input1 = ['candy cane', 'cleaning rags', 'large bag', 'large bag', 
                  'large bag', 'lasso', 'leaf blade', 'leaf blade', 
                  'leaf blade', 'leaf blade', 'silver chalice', 
                  'silver chalice', 'silver chalice', 'silver chalice', 
                  'silver chalice', 'silver snuff box', 'small restorative', 
                  'small restorative', 'small restorative', 
                  'small restorative', 'small restorative', 'spear', 'spear', 
                  'spear', 'spear', 'spear', 'steel bottle', 'steel bottle', 
                  'steel bottle', 'steel bottle', 'steel bottle', 
                  'stilletos.', 'stilletos.']

        input2 = ["large bag", "large sack", "silver chalice", "steel bottle", 
                  "bag", "adamantine sword", 'adamantine axe', "claymore", 
                  "poison ring", "spider leg", "scimitar", 
                  "small restorative", "spear", "bolos", 'javelin', 
                  "leaf blade", "short bow", "heathen amulet", "hard cap", 
                  "hard gloves", "hard boots", "panteloons", 
                  "travellers cross", "leather mask", "leather collar", 
                  "studded leather collar", "mountain boots with crampons", 
                  "mountain gloves", "chain mail armour", 
                  'chain mail sleeves', 'chain mail leggings', 
                  'chain mail gloves', 'chain mail hood', 'chain mail boots', 
                  "ring mail armour", "ring mail sleeves", 
                  "ring mail leggings", "ring mail hood", 
                  "ring mail gauntlets", "leather collar", "furry cloak", 
                  "white amulet", "white potion", "stilleto", 'rapier', 
                  'heavy crossbow', 'lion charm', 'glowing potion', 
                  'war hammer'] 
        
        #execute
        result = extract_sellable_and_droppable(input1, input2)
        #assert
        #self.assertEquals(['cane', 'rags', 'lasso', 'snuff', 'stilletos.', 'stilletos.'] , result)
        # hmm, on this one there are multiple allowable outputs 
        # and I'm not sure how to allow for that
        #self.assertEquals(['candy', 'cleaning', 'lasso', 'silver 6', 
        #                   'stilletos', 'stilletos 2' ].reverse(), result)
        self.assertEquals(['stilletos 2', 'stilletos', 'silver 6', 
                           'lasso', 'cleaning', 'candy'], result)
      
        
    def test_extract_sellable_and_droppable_whenTheSecondWordHasANameCollision(self):
            
        input1 = ['candy cane', 'cleaning rags', 
                  'small knife', 'hand knife',
                  'silver chalice', 'silver snuff box']
        
        input2 = ["large bag", "large sack", "silver chalice", 
                  "steel bottle", "bag", "adamantine sword", 
                  'adamantine axe', "claymore", "poison ring", "spider leg", 
                  "scimitar", "small restorative", "spear", "bolos", 
                  'javelin', "leaf blade", "short bow", "heathen amulet", 
                  "hard cap", "hard gloves", "hard boots", "panteloons", 
                  "travellers cross", "leather mask", "leather collar", 
                  "studded leather collar", "mountain boots with crampons", 
                  "mountain gloves", "chain mail armour", 
                  'chain mail sleeves', 'chain mail leggings', 
                  'chain mail gloves', 'chain mail hood', 
                  'chain mail boots', "ring mail armour", 
                  "ring mail sleeves", "ring mail leggings", 
                  "ring mail hood", "ring mail gauntlets", "leather collar", 
                  "furry cloak", "white amulet", "white potion", "stilleto", 
                  'rapier', 'heavy crossbow', 'lion charm', 'glowing potion', 
                  'war hammer']
        
        result = extract_sellable_and_droppable(input1, input2)
        #assert
        # Also acceptable:
        #self.assertEquals(['cane', 'rags', 'knife', 'hand', 'snuff'] , result)
        #self.assertEquals(['cane', 'rags', 'knife', '', 'hand', 'snuff'] , result)
        #self.assertEquals(['candy', 'cleaning', 'small', 'hand', 
        #                   'silver 2'].reverse()[:], result)
        self.assertEquals(['silver 2', 'hand','small','cleaning','candy'], 
                          result)
        
        
    def test_extract_sellable_and_droppable_whenAllWordsAreUsedEarlier(self):
        
        input1 = ['candy cane', 'cleaning rags', 
                  'large bag', 'small bag', 'hand knife', 'small knife', 
                  'silver chalice', 'silver snuff box']
        
        input2 = []
        
        result = extract_sellable_and_droppable(input1, input2)
        
        #self.assertEquals(['cane', 'rags', 'bag', '', 'small', 'knife', '', 'chalice', 'snuff'] , result)
        #TBD
        #self.assertEquals(['silver 2', 'small 2', 'hand', 'small', 'large'] , result)
        #self.assertEquals(['candy', 'cleaning', 'large', 'small', 'hand', 
        #                   'small 2', 'silver', 'silver 2'].reverse()[:],
        self.assertEquals(['silver 2','silver','small 2','hand','small',
                           'large','cleaning','candy'], 
                           result)    
                
    def test_extract_sellable_and_droppable_whenAllWordsAreUsedLater(self):
        
        input1 = ['candy cane', 'cleaning rags', 
                  'large bag', 'small bag', 'hand knife', 'small knife', 
                  'large hat',
                  'silver chalice', 'silver snuff box']
        
        input2 = []
        
        result = extract_sellable_and_droppable(input1, input2)
        
        #self.assertEquals(['cane', 'rags', 'bag', '', 'small', 'knife', '', 'hat', 'chalice', 'snuff'] , result)
        #TBD
        #self.assertEquals(['silver 2', 'small 2', 'hand', 'small', 'large'] , result)
        #self.assertEquals(['candy','cleaning','large','small','hand',
        #                   'small 2','large 2','silver',
        self.assertEquals(['silver 2','silver','large 2','small 2','hand','small',
                            'large','cleaning','candy'], result)
        
        
    def test_extract_sellable_and_droppable_whenThereAreManyOfOneItem(self):
        # If there are many (ie. three) of one item we want to do 
        # sell item 3; sell item 2; sell item 1;
        # because (ie. grey cloaks) they are not all guaranteed to sell.
        # The current version of doesn't pass this test yet.
        input1 = ['candy cane', 'cleaning rags',
                 'grey cloak', 'grey cloak', 'grey cloak',
                 'silver chalice', 'silver snuff box']
        input2 = []
       
        result=extract_sellable_and_droppable(input1, input2)
     
        #self.assertEquals(['cane', 'rags', 'cloak 3', 'cloak 2', 'cloak', 'chalice', 'snuff'])
        self.assertEquals(['silver 2', 'silver', 'grey 3', 'grey 2', 'grey', 
                           'cleaning', 'candy'], result)
        
        
    def test_extract_sellable_and_droppable_whenThereAreSixtyFourOfOneItem(self):
        
        input1 = ['grey cloak']
        for i in range(0,6):
            x = input1[:]
            input1.extend(x)
        
        input2=[]
        
        result = extract_sellable_and_droppable(input1, input2)
        
        desired_result=['grey']
        for i in range(2,65):
            desired_result.append('grey ' + str(i))
        desired_result.reverse()
        
        self.assertEquals(desired_result, result)
        


