"""test_ParallelIO.py - testcases for combination IO management and parallel processing"""

import sys
#Package to test:
package = "/home/epeters/NeutronParser/rootparser"
if package not in sys.path:
    sys.path.insert(0, package)

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
Parallel = ThreadManager(n_processes=parallel.N_THREADS)     #Threading
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

        #now: subtrees[PID] = None

    def test_join_all_events(self):
        #functionality for sorting sublists of events by evt.index
        evt_lst = []
        log.info("Testing join_all_events function")
        with rootpy.io.root_open(testfile.MC_filename) as fh:
            for subtree in IO.get_next_tree(fh):
                IO.put_subtree(os.getpid(), subtree )
                #Create a list of sublists of events in backwards index order
                for i in reversed(range(10)):
                    evts = range(10*i, 10*(i+1))
                    temp = [event.Event(j, IO.get_subtree()) for j in evts]
                    evt_lst.append(temp)
                out = IO.join_all_events(evt_lst)
                break
        self.assertEqual([evt.index for evt in out], range(100))


    def test_divide_and_process(self):
        #Divide a testfile and sick the threads on it
        #divide the file into the temporary directory
        paths = IO.split_file(testfile.MC_filename, parallel.N_THREADS, path=os.getcwd(), dest=testfile.TMP, recreate=True)

        #explicit function and targets
        func = event.ParseEvents
        args = paths

        i = 0
        Time.start("CPU-ParallelIO OO fill() trial %i" % (i+1) )
        #an unordered list of sublists of events
        cpu_out = Parallel.run(func, args, ParallelPool=Pool)
        Time.end()
        all_evts = IO.join_all_events(cpu_out)

        #self.assertEqual(fill_good, [0 for i in paths])
        #Serial func takes in a single filename
        func = event.ParseEvents
        args = [testfile.MC_filename]

        Time.start("SerialIO OO fill() trial %i" % (i+1) )
        serial_out = Parallel.run(func, args, ParallelPool=None)
        Time.end()
        serial_out = IO.join_all_events(serial_out)
        #print [evt.index for evt in serial_out]
        #print [evt.index for evt in all_evts]

        for i in range(len(serial_out)):
            #print serial_out[i].index, all_evts[i].index
            print serial_out[i], all_evts[i]
        #self.assertEqual(serial_out, all_evts)
    #Timing
    def test_TimeParseEvents(self):
        return


if __name__ == "__main__":

    testfile.recreate_testfile()
    unittest.main()
    #args_test([1,2,3,4])
