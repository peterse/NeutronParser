import sys
#Package to test:
sys.path.insert(0, "/home/epeters/NeutronParser/rootparser")

import unittest
from timer import Timer

#For parallel computation
from parallel import RunParallel
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

#Testing parallelization using processes
def test_CPU_bound(func, obj_lst, timer):
    #CPU-bound routine:
    timer.start("CPU-parallel")
    out = RunParallel(func, obj_lst, ParallelPool=Pool)
    timer.end()
    return out
#Testing parallelization using threads
def test_IO_bound(func, obj_lst, timer):
    #I/O-bound routine:
    timer.start("thread-parallel")
    out = RunParallel(func, obj_lst, ParallelPool=ThreadPool)
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
#RunParallelD FUNCTIONS MUST BE DEFINED AT TOP LEVEL

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

#File managers for testing parallel returns
dummyIO = IO.RootIOManager("dummy.root")

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
        arr = RunParallel(parallel_func_3, target_3)

    def test_parallel_4vec_MC(self):
        global dummyIO
        #Run a parallel routine in the rootfile context, using an event generator
        with dummyIO as fh:
            #get the trees
            trees = dummyIO.list_of_trees
            #Run parallel routine from within rootfile context!
            for evt in event.EventParser(0, 10, trees[0]):
                print event.get_4vec_mc(evt)

            #out = RunParallel(event.get_4vec_mc, event.EventParser(0, 10, trees[0]))
        #RunParallelevent.get_4vec_mc

if __name__ == "__main__":
    unittest.main()
