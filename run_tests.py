import sys
import unittest
from test.MudReaderThreadTest import MudReaderThreadTest
from test.misc_functionsTest import misc_functionsTest
from test.BotThreadTest import BotThreadTest

if __name__=='__main__':
    suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(MudReaderThreadTest))
    unittest.TextTestRunner().run(suite)
    
    suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(misc_functionsTest))
    unittest.TextTestRunner().run(suite)
        
    suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(BotThreadTest))
    unittest.TextTestRunner().run(suite)
