"""test_ParallelIO.py - testcases for combination IO management and parallel processing"""

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

#Errors and logging
from rootparser_exceptions import ChildThreadError
#import rootparser_exceptions #loggin config
from rootparser_exceptions import ParallelError


#For applying different tests
import random
random.seed()
import event
import rootpy.ROOT as ROOT

#Regenerating our file...
import maketestfiles as testfile
import IO
from IO import versioncontrol

import os

#Boot the thread manager with the current tree
Parallel = ThreadManager(n_processes=8)     #Threading
Time = Timer()

class ParallelIOTest(unittest.TestCase):



    def test_divide_and_process(self):
        #Divide a testfile and sick the threads on it

        #divide the file into the temporary directory
        paths = split_file(testfile.MC_filename, parallel.N_THREADS, dest=testfile.TMP)

        #feed the paths to the ThreadManager
        Parallel.loadQ(paths)

        #explicit function and targets
        func = 



                         #Timing
def args_test(*args):
    for arg in args:
        print arg
if __name__ == "__main__":

    #IO.recreate_testfile()
    #unittest.main()
    args_test([1,2,3,4])
