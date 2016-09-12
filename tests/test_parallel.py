import sys
#Package to test:
sys.path.insert(0, "/home/epeters/NeutronParser/rootparser")

import unittest
from timer import Timer
import time

#For parallel computation
from parallel import ThreadManager
import numpy as np
from functools import partial

#For multiprocessing
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

#For applying different tests
import random
random.seed()
import event
import IO
import rootpy.ROOT as ROOT

#Regenerating our file...
from generate_dummy_root import generate

# # # # # Test-specific filenames # # # #
mc_filename = "MC_dummy.root"
def refresh_testfile():
    generate()
    dummyIO = IO.RootIOManager(mc_filename)
    trees = dummyIO.list_of_trees
    tree = trees[0]
    tree.GetEvent()
    time.sleep(1)
    return

#File managers for testing parallel returns
global_f = None #global file handle, assigned in file managing contexts
tree = None #global tree handle
refresh_testfile()


#Boot the thread manager with the current tree
Parallel = ThreadManager()

#timing
Time = Timer()

#Testing parallelization using processes
def test_CPU_bound(func, obj_lst, timer):
    #CPU-bound routine:
    timer.start("CPU-parallel")
    out = Parallel.run(func, obj_lst, ParallelPool=Pool)
    timer.end()
    return out
#Testing parallelization using threads
def test_IO_bound(func, obj_lst, timer):
    #I/O-bound routine:
    timer.start("thread-parallel")
    out = Parallel.run(func, obj_lst, ParallelPool=ThreadPool)
    timer.end()
    return out
#Serial execution similar to parallel setups
def test_serial(func, obj_lst, timer):
    #serial - map onto a new list by hand
    timer.start("serial")
    new_lst = []
    for obj in obj_lst:
        new_lst += [func(obj)]
    timer.end()
    out = new_lst
    return out

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#test functions for parallelization
#Parallel.runD FUNCTIONS MUST BE DEFINED AT TOP LEVEL

#increment every member of a list by 1
def parallel_func_1(val):
    return val + 1
target_1 = xrange(10000000)

#Pythagorean theorem; single argument
def parallel_func_2(tupl):
    return np.sqrt(np.square(tupl[0]) + np.square(tupl[1]) )
target_2 = zip(range(100000),range(100000))

#Testing decorators
class ArrayObject:
    """
    Generic object class to test parallelization of functions
    """
    def __init__(self):
        self.x = random.randint(-10,10)
        self.y = random.randint(-10,10)
        self.z = random.randint(-10,10)

#Pythagorean theorem on triplet of an object
def parallel_func_3(obj):
    summ = np.sum(map(np.square, [obj.x, obj.y, obj.z]))
    return np.sqrt(summ)
target_3 = [ ArrayObject() for i in range(10)]


# def parallel_cleanup():
#     #Find an index of pids_finished to set true, then attempt to closeout the queue
#     for i, b in enumerate(Parallel.pids_finished):
#         if b == False:
#             Parallel.pids_finished[i] = True
#             break
#     print Parallel.pids_finished
#     if all(Parallel.pids_finished):
#         while not Parallel.queue.empty():
#             Parallel.queue.get()


#Feeling out proper IO handling for fastest parallel file processing

def tree_access(index):
    #This will be wrapped to avoid >1 arguments
    try:
        tree.GetEvent(index)
        t1 = tree.GetLeaf("event").GetValue()
    except TypeError:
        sys.exit("ERROR: Bad read in ROOT file")
    else:
        return t1

def tree_access_2(index):
    global_f.Get("test").GetEvent(index)
    t1 = global_f.Get("test").GetLeaf("event").GetValue()
    return t1

def parallel_access_2(index):

    #This will be wrapped to avoid >1 arguments
    tree.GetEvent(index)
    #Access immediately after getting the event
    #print "Accessing index %i #1" % index
    t1 = tree.GetLeaf("event").GetValue()
    time.sleep(random.randint(1,3))
    #print "Accessing index %i #2" % index
    t2 = tree.GetLeaf("event").GetValue()
    #print "Queue putd (#2) (index %i)" % index

    return (t1, t2)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class ParallelTest(unittest.TestCase):

    def test_IO_CPU_serial_speeds(self):

        return #skip...
        #grab the timer
        global Time
        #Run the test
        for func, obj in [(parallel_func_1, target_1), (parallel_func_2, target_2)]:

            #Run timing
            t1 = test_serial(func, obj, Time)
            t2 = test_IO_bound(func, obj, Time)
            t3 = test_CPU_bound(func, obj, Time)

            #Check results
            self.assertEqual(t1, t2)
            self.assertEqual(t1, t3)

    def test_parallel_object(self):
        return #skip..
        arr = Parallel.run(parallel_func_3, target_3)

    def test_parallel_4vec_MC(self):
        return #skip..
        global dummyIO
        #Run a parallel routine in the rootfile context, using an event generator
        with dummyIO as fh:
            #get the trees
            trees = dummyIO.list_of_trees
            #Run parallel routine from within rootfile context!
            for evt in event.EventParser(0, 10, trees[0]):
                print event.get_4vec_mc(evt)

            #out = Parallel.run(event.get_4vec_mc, event.EventParser(0, 10, trees[0]))
        #Parallel.runevent.get_4vec_mc

    def test_parallel_GetEvent_collision(self):
        #skip
        return
        global tree
        #attempt to access tree events in parallel
        N = 80
        #array of indices to access
        obj_arr = range(N)
        out = Parallel.run(parallel_access_2, obj_arr)
        for pair in out:
            self.assertEqual(pair[0], pair[1])
        return

    def test_TTreeIO_timing(self):
        global Time, tree
        N_grab = 20
        N_entries = 1000000

        func = tree_access

        entries = range(N_entries)

        #test many serial accesses
        # Time.start("serial IO")
        # for i in range(N_grab):
        #     sp = Parallel.run(func, entries, ParallelPool=None)
        # Time.end()
        # refresh_testfile()
        #
        # Time.start("thread-parallel IO")
        # for i in range(N_grab):
        #     tp = Parallel.run(func, entries, ParallelPool=ThreadPool)
        # Time.end()
        # refresh_testfile()

        for i in range(N_grab):
            Time.start("process-parallel IO trial %i" % (i+1) )
            pp = Parallel.run(tree_access, entries, ParallelPool=Pool)
            Time.end()
            refresh_testfile()
        return

        print pp == sp
        print tp == sp
        for i, val in enumerate(sp):
            if val != tp[i]:
                print i, val, tp[i]
            if val != pp[i]:
                print i, val, pp[i]
if __name__ == "__main__":
    #enter read only context
    #print test_parallel_GetEvent_collision()
    unittest.main()
