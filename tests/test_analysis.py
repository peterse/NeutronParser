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

import analysis

#For parallel computation
import parallel
from parallel import ThreadManager
Parallel = ThreadManager(n_processes=parallel.N_THREADS)     #Threading

class AnalysisTest(unittest.TestCase):


    def test_convert2numpy(self):
        log.info("Testing root2array function")
        with rootpy.io.root_open(testfile.MC_filename) as fh:
            for tree in IO.get_next_tree(fh):
                arr = root_numpy.tree2array(tree)

    def test_ParseEventsNP(self):
        analysis.ParseEventsNP(testfile.MC_filename)

if __name__ == "__main__":

    testfile.recreate_testfile()
    unittest.main()
