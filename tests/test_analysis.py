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
import filters as fi

#For parallel computation
import parallel
from parallel import ThreadManager
Parallel = ThreadManager(n_processes=parallel.N_THREADS)     #Threading

class AnalysisTest(unittest.TestCase):

    def test_filters(self):
        deck = "sample_filter.txt"
        print "checking filter deck %s" % deck
        print fi.SetFilters(deck)

    def test_ParseEventsNP(self):
        #pass
        return
        #non-OO version for event parsing; still uses cut subtrees
        pid = os.getpid()

        filename = testfile.MC_filename
        path = os.getcwd()
        target = "test_analysis.root"
        dest = os.getcwd()

        analysis.ParseEventsNP(filename, path, target, dest)
if __name__ == "__main__":

#    testfile.recreate_testfile()
    unittest.main()
