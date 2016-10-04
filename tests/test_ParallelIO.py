"""test_ParallelIO.py - testcases for combination IO management and parallel processing"""

import sys
#Package to test:
sys.path.insert(0, "/home/epeters/NeutronParser/rootparser")

import unittest
from timer import Timer
import time

#For parallel computation
import parallel
from parallel import ThreadManager

import numpy as np
from functools import partial

#For multiprocessing
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

#Errors and logging
from rootparser_exceptions import ChildThreadError
#import rootparser_exceptions #loggin config
from rootparser_exceptions import ParallelError
from rootparser_exceptions import log


#For applying different tests
import random
random.seed()
import event
import rootpy.ROOT as ROOT
import rootpy   #root_open

#Regenerating our file...
import maketestfiles as testfile
import IO
from IO import versioncontrol

import os

#Boot the thread manager with the current tree
Parallel = ThreadManager(n_processes=8)     #Threading
Time = Timer()

class ParallelIOTest(unittest.TestCase):

    def test_Q_put_get(self):
        #Basic functionality for the local Q @ Parallel
        lst = ["A", "B", "C"]
        Parallel.loadQ(lst)
        log.info("Dumping from the Queue:")
        while not Parallel.Q.empty():
            log.info("  Queue item: %s" % Parallel.Q.get())

    def test_put_get_subtree(self):
        #Grab trees from the testfile and put them to the main namespace
        with rootpy.io.root_open(testfile.MC_filename) as fh:
            log.info("Putting subtrees to IO.subtrees")
            PID = os.getpid()
            for subtree in IO.get_next_tree(fh):
                put = subtree
                IO.put_subtree(PID, subtree)
                #WARNING: All computation on the tree goes here
                # - - - - - -
                break
                #Next iteration will overwrite this PID's global tree

            #WARNING: global handles are deleted when fh closes
            #Get the tree while we're still in the fh context
            log.info("Getting PID:%s subtree from IO.subtrees" % str(PID))
            got = IO.get_subtree()
            self.assertEqual(put, got)
            for i in subtree.GetListOfBranches():
                print i
            subtree.GetEvent(5)
            print subtree.GetBranch("mc_vtx").FindLeaf("mc_vtx").GetValue(2)
        #now: subtrees[PID] = None

    def test_divide_and_process(self):

        return
        #Divide a testfile and sick the threads on it
        #divide the file into the temporary directory
        paths = IO.split_file(testfile.MC_filename, parallel.N_THREADS, path=os.getcwd(), dest=testfile.TMP)

        print paths
        #process the paths in parallel
        #Parallel.loadQ(paths)

        #explicit function and targets
        func = event.ParseEvents
        args = paths
        Parallel.run(func, args, ParallelPool=Pool)


                         #Timing
def args_test(*args):
    for arg in args:
        print arg

if __name__ == "__main__":

    testfile.recreate_testfile()
    unittest.main()
    #args_test([1,2,3,4])
