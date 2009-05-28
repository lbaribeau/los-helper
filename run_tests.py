import sys
import unittest
from test.MudReaderThreadTest import MudReaderThreadTest

if __name__=='__main__':
    suite = unittest.TestSuite(unittest.TestLoader().loadTestsFromTestCase(MudReaderThreadTest))
    unittest.TextTestRunner().run(suite)
