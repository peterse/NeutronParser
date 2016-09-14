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
import rootparser_exceptions #loggin config



#For applying different tests
import random
random.seed()
import event
import IO
import rootpy.ROOT as ROOT

#Regenerating our file...
import maketestfiles as testfile


# # # # GLOBAL OBJECTS # # # # #
#File managers for testing parallel returns
#initialized at ParallelTest.__init__
global_f = None #IO filehandle
tree = None # tree handle
dummyIO = None #IO file wrapper objecct

#Boot the thread manager with the current tree
Parallel = ThreadManager()

#timing
Time = Timer()

# # # # # # #

# # # GLOBAL FUNCTIONS # # # #
#multiprocessing requires functions defined in global context
#otherwise, 'cannot pickle' error is raised

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

#Feeling out proper IO handling for fastest parallel file processing
def tree_access(index):
    #This will be wrapped to avoid >1 arguments
    while True:
        try:
            tree.GetEvent(index)
            t1 = tree.GetLeaf("event").GetValue()
            return t1
        except:
            #print sys.exc_info()[0]
            #There was a clash for access, take a nap!:
            time.sleep(.001)

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

def recreate_testfile():
    global dummyIO, tree
    testfile.generate_MC()
    dummyIO = IO.RootIOManager(testfile.MC_filename)
    #grab the test-tree
    tree = dummyIO.list_of_trees[0]
    tree.GetEvent()
    time.sleep(1)
    return


# # # # # # # # # # # # # # # # # # #

class ParallelTest(unittest.TestCase):

    #Overload the TestCase init; needs to be passed proper initialization args/kwargs
    def __init__(self, *args, **kwargs):
        super( ParallelTest, self).__init__(*args, **kwargs)
        #refresh the testfile
        #self.recreate_testfile()

    #Recreate a rootfile that ~may~ have been corrupted

    #Diagnostic to shot index, value that do not agree between lists
    #Returns the index range of disagreement (start, end)
    def lst_compare(self, a, b):

        for i, val in enumerate(a):
            #if no differences are found, the range is 0-length
            start = -1
            end = -1
            if val != b[i]:
                if start == -1:
                    start = i
                #save the most recent disagreement
                end = i
                #print i, val, b[i]
        return start, end


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
        return
        global Time, tree, dummyIO
        #5 trials for Accessing
        N_grab = 20

        func = tree_access
        entries = range(testfile.filesize)


        # #test many serial accesses
        # for i in range(N_grab):
        #     Time.start("serial IO trial %i" % (i+1) )
        #     sp = Parallel.run(func, entries, ParallelPool=None)
        #     Time.end()
        #     self.assertEqual(sp, entries)

        #FIXME: thread-parallel not working!
        #Getting repeats of read entries; this may mean the pool.map is working improperly
        # for i in range(N_grab):
        #     Time.start("thread-parallel IO trial %i" % (i+1) )
        #     tp = Parallel.run(func, entries, ParallelPool=ThreadPool)
        #     Time.end()
        #     stp = sorted(tp)
        #     a, b = self.lst_compare(sorted(tp), entries)
        #     print stp == entries
        #     for val in stp:
        #         if stp.count(val) >1:
        #             print val
        #     if stp != entries:
        #         print len(stp), len(set(stp))

                # for i, val in enumerate(stp):
                #     if val not in set(stp):
                #         print i, val, "not in set"
                #     else:
                #         entries.pop(i)
                #     stp.pop(i)
                # for i, val in enumerate(entries):
                #     if val not in stp:
                #         print i, val, "not in TP"
                #     else:
                #         stp[i] = -1
                #     entries[i] = -1
                #print stp[a-1], stp[a], stp[b], stp[b-1]
                # for pair in zip(stp, entries):
                #     if pair[0] != pair[1]:
                #         print pair
                #print stp
                #print entries
            #self.assertEqual(list(sorted(tp)), entries)

        #Test process-parallel access
        for i in range(N_grab):
            Time.start("process-parallel IO trial %i" % (i+1) )
            pp = Parallel.run(tree_access, entries, ParallelPool=Pool)
            Time.end()
            self.assertEqual(entries, pp)
            #temp = pp
            #self.recreate_testfile()
        return

    def test_event_fill(self):
        #Test the Event.fill method, in series then in parallel
        global tree, dummyIO
        #Initialize an event generator fo rhe current tree
        func = event.fill_event
        evts = event.EventParser(0, testfile.filesize, tree)

        #Number of trials
        N_grab = 5

        #Fill the events Serial
        for i in range(N_grab):
            #Regenerate event generator
            evts = event.EventParser(0, testfile.filesize, tree)

            Time.start("serial fill() trial %i" % (i+1) )
            out = Parallel.run(func, evts, ParallelPool=None)
            Time.end()
            self.assertEqual(range(testfile.filesize), out)

        #Fill the events in CPU-parallel
        for i in range(N_grab):
            #Regenerate event generator
            evts = event.EventParser(0, testfile.filesize, tree)
            
            Time.start("CPU-parallel fill() trial %i" % (i+1) )
            out = Parallel.run(func, evts, ParallelPool=Pool)
            Time.end()
            self.assertEqual(range(testfile.filesize), out)



if __name__ == "__main__":
    #enter read only context
    #print test_parallel_GetEvent_collision()
    recreate_testfile()
    unittest.main()
