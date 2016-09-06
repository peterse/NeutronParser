import sys
#Package to test:
sys.path.insert(0, "/home/epeters/NeutronParser/rootparser")

import unittest
from timer import Timer

#For parallel computation
from parallel import parallelize
import numpy as np
from functools import partial

#For multiprocessing
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool


#Testing parallelization using processes
def test_CPU_bound(func, obj_lst, timer):
    #CPU-bound routine:
    timer.start("CPU-parallel")
    out = parallelize(func, obj_lst, ParallelPool=Pool)
    timer.end()
    return out
#Testing parallelization using threads
def test_IO_bound(func, obj_lst, timer):
    #I/O-bound routine:
    timer.start("thread-parallel")
    out = parallelize(func, obj_lst, ParallelPool=ThreadPool)
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
#PARALLELIZED FUNCTIONS MUST BE DEFINED AT TOP LEVEL

#increment every member of a list by 1
def parallel_func_1(val):
    return val + 1
target_1 = range(10000000)

#Pythagorean theorem; single argument
def parallel_func_2(tupl):
    return np.sqrt(np.square(tupl[0]) + np.square(tupl[1]) )
target_2 = zip(range(100000),range(100000))


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class ParallelTest(unittest.TestCase):

    def test_IO_CPU_serial_speeds(self):

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


if __name__ == "__main__":
    unittest.main()
