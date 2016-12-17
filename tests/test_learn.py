import sys
package = "/home/epeters/NeutronParser/rootparser"
if package not in sys.path:
    sys.path.insert(0, package)

import unittest
from rootparser_exceptions import log

#IO
import os       #getpid
import rootpy   #.io, root_open
import root_numpy
import IO
import maketestfiles as testfile

import learn

#For parallel computation
import parallel
from parallel import ThreadManager
Parallel = ThreadManager(n_processes=parallel.N_THREADS)     #Threading

class AnalysisTest(unittest.TestCase):


    def test_convert2numpy(self):
        test_dct = {}
        learn.make_clean_data(testfile.MC_filename, test_dct)
        log.info("Testing root2array function")



if __name__ == "__main__":

    testfile.recreate_testfile()
    unittest.main()
