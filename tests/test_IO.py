import sys
#Package to test:
sys.path.insert(0, "/home/epeters/NeutronParser/rootparser")

import unittest
from timer import Timer

#For IO tools
import ROOT
import IO




class IOTest(unittest.TestCase):

    #Test context management for rootfiles
    def test_open_file(self):
        global testfile, ROOTIO
        with RootIO as fh:
            pass

    #test find-trees utility
    def test_get_list_of_trees(self):
        global testfile, ROOTIO
        #Should find trees:
        self.assertTrue(any(RootIO.list_of_trees))




if __name__ == "__main__":
    #Initialize some globals to play with
    testfile = "IOtest.root"
    RootIO = IO.RootIOManager(testfile)
    #Run the tests
    unittest.main()
