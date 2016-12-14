import sys
#Package to test:
sys.path.insert(0, "/home/epeters/NeutronParser/rootparser")

import unittest
from timer import Timer


#For IO files
import maketestfiles as testfile
import IO

from rootparser_exceptions import RootFileError, log
#For IO tools
import ROOT
import rootpy.ROOT as rROOT
import rootpy.io
#from analysis import testEventAccess
import os       #getcwd()

#Some related functions
import random
random.seed()

SPLIT_FILES = None

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

    def test_add_event_branch(self):
        IO.add_event_branch(testfile.MC_filename, os.getcwd())
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

    def test_index_cuts(self):
        #SKIP
        return
        #Make sure we divide a total number into the right number of segments
        T = random.randint(0, 1000)
        for x in [ 3, 8, 17, T, T+1]:
            cuts = IO.make_cuts_lst(T, x)
            self.assertEqual(len(cuts), x)

    #
    def test_filesplit(self):
        #Attempt to split a file's trees using the IO.
        tmp = "%s/tmp" % os.getcwd()
        N = 8
        file_lst = IO.split_file(testfile.MC_filename, 8, dest=tmp)
        #keep for later use
        global SPLIT_FILES
        SPLIT_FILES = file_lst
        self.assertEqual(N, len(file_lst))
        for f in file_lst:
            try:
                rootpy.io.root_open(f)
            except rootpy.ROOTError as e:
                print e
                raise RootFileError("File %s could not be opened")

    def test_get_next_tree(self):
        #check the eponymous funtion
        #skip
        return
        count = 0
        with rootpy.io.root_open(testfile.MC_filename) as fh:
            trees = IO.get_next_tree(fh)
            for tree in trees:
                count += 1
        self.assertEqual(count, testfile.n_trees)
        log.info("Counted %i trees in file %s" % (count, testfile.MC_filename) )

    def test_join_all_histograms(self):

        #pre = os.getcwd()
        #SPLIT_FILES = ["%s/tmp/%s" % (pre, fname) for fname in os.listdir("%s/tmp" % os.getcwd()) ]
        global SPLIT_FILES
        if SPLIT_FILES is None:
            log.error("Need to re-run split_file test and keep result paths")
            raise ValueError
        else:
            merge_targets = SPLIT_FILES
        target = "test_merge.root"
        dest = testfile.TMP_HIST
        hist_out = IO.join_all_histograms(merge_targets, target, dest)


if __name__ == "__main__":
    #Initialize some globals to play with
    testfile.recreate_testfile()
    dummyIO = IO.RootIOManager(testfile.MC_filename)
    tree = dummyIO.list_of_trees[0]
    tree.GetEvent()
    #Run the tests
    unittest.main()
