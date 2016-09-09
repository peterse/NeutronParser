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

# # # # # Test-specific filenames # # # #
mc_filename = "MC_dummy.root"
#File managers for testing parallel returns
dummyIO = IO.RootIOManager(mc_filename)
trees = dummyIO.list_of_trees
tree = trees[0]
tree.GetEvent()

#Boot the thread manager with the current tree
Parallel = ThreadManager()
Parallel.queue.put(tree)

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

#Attempt to clash access methods for a given tree
#call GetEvent, then show a value now and 3 s later

def parallel_access(pair):
    index = pair[0]
    tree_handle = pair[1]

    tree_handle.GetEvent(index)
    #Access immediately after getting the event
    t1 = tree_handle.GetLeaf("event").GetValue()
    print "%s: Accessing event %i" % (index, t1)

    #sleep for a short random amount of time (do not preserve order among threads)
    time.sleep(random.randint(1,3))

    #Access the tree again; see if context is saved
    t2 = tree_handle.GetLeaf("event").GetValue()
    print "%s: Accessing event %i" % (index, t2)
    print (t1, t2)
    return (t1, t2)

def parallel_access_2(index):

    #This will be wrapped to avoid >1 arguments
    tree = Parallel.queue.get()
    tree.GetEvent(index)
    #Access immediately after getting the event
    t1 = tree.GetLeaf("event").GetValue()
    Parallel.queue.put(tree)
    time.sleep(random.randint(1,3))
    Parallel.queue.get(tree)
    t2 = tree_handle.GetLeaf("event").GetValue()
    return (t1, t2)

#wrap the parallel access routine to reference our global tree
def parallel_access_sametree(val):
    return parallel_access_2(val, tree)
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class ParallelTest(unittest.TestCase):

    def test_IO_CPU_serial_speeds(self):

        return #skip...
        #boot the timer
        Time = Timer()

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
        global tree

        #attempt to access tree events in parallel
        N = 3
        #obj_arr = zip(range(N), [tree for i in range(N)])
        obj_arr = zip(range(N), [tree]*N)
        #tree.GetEvent(0)
        results = Parallel.run(parallel_access_2, obj_arr )
        print results


if __name__ == "__main__":
    unittest.main()
