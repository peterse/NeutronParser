import sys
#Package to test:
sys.path.insert(0, "/home/epeters/NeutronParser/rootparser")

import unittest
from timer import Timer

#For IO files
import maketestfiles as testfile

#For IO tools
import ROOT
import rootpy.ROOT as rROOT
import IO
import os       #getcwd()


def get_ROOT_tree(filename, treename):
    f = ROOT.TFile.Open(filename, "read")
    tree = f.Get(treename)
    return tree

def get_rROOT_tree(filename, treename):
    f = rROOT.TFile.Open(filename, "read")
    tree = f.Get(treename)
    return tree

class IOTest(unittest.TestCase):

    #Test context management for rootfiles
    def test_open_file(self):
        global dummyIO
        with dummyIO as fh:
            pass

    #test find-trees utility
    def test_get_list_of_trees(self):
        global dummyIO
        #Should find trees:
        self.assertTrue(any(dummyIO.list_of_trees))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_testfile(self):
        #test the file IO using different access methods
        #pass
        return

        #pyROOT
        tree = get_ROOT_tree(testfile.MC_filename, testfile.treename)
        out = []
        for i in range(testfile.filesize):
            tree.GetEntry(i)
            out.append( (i, tree.GetLeaf("event").GetValue()) )

        for pair in out:
            if pair[0] != pair[1]:
                print pair

        #ROOTpy
        rtree = get_rROOT_tree(testfile.MC_filename, testfile.treename)
        out = []
        for i in range(testfile.filesize):
            rtree.GetEntry(i)
            out.append( (i, rtree.GetLeaf("event").GetValue()) )

        for pair in out:
            if pair[0] != pair[1]:
                print pair

    def test_filesplit(self):
        #Attempt to split a file's trees using the IO.
        IO.split_file(testfile.MC_filename, "splitfile.root", testfile.filesize)



if __name__ == "__main__":
    #Initialize some globals to play with
    dummyIO = IO.RootIOManager(testfile.MC_filename)
    tree = dummyIO.list_of_trees[0]
    tree.GetEvent()
    #Run the tests
    unittest.main()
