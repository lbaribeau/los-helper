import sys, unittest

# from main.import_tools import *
# import_subdir("")
# import_subdir("main")
# import_subdir("data")
# import_subdir("bots")
# import_subdir("reactions")

# from main.misc_functions import *

# from test.misc_functionsTest import misc_functionsTest #out of date
# from test.DatabaseTest import data_functionsTest

#from test.MudReaderThreadTest import MudReaderThreadTest
#from test.BotThreadTest import BotThreadTest
#from test.MudObjectDictTests import MudObjectDict_functionsTest
from test.test_los_helper import TestLosHelper
#from test.mob_target_determinator_test import MobTargetDeterminatorTest

if __name__ == '__main__':
    # magentaprint("meow tests are being run meow", False)

	#The following test cases are out of date with the code in main
    #suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(MudReaderThreadTest))
    #unittest.TextTestRunner().run(suite)
    
    # suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(misc_functionsTest))
    # unittest.TextTestRunner().run(suite)
    
    # suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(data_functionsTest))
    # unittest.TextTestRunner().run(suite)

    # suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(BotThreadTest))
    # unittest.TextTestRunner().run(suite)

    # suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(MudObjectDict_functionsTest))
    # unittest.TextTestRunner().run(suite)

    suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(TestLosHelper))
    unittest.TextTestRunner().run(suite)

    # suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(MobTargetDeterminatorTest))
    # unittest.TextTestRunner().run(suite)

