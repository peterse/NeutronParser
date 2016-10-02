"""
Methods for parallelization; speedup will depend on implementation and whether the processes are cpu-bound, I/O-bound, etc.
"""
import multiprocessing
from multiprocessing import Pool
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool

from multiprocessing import Queue, Process
from functools import partial

import time
import math

#Default mode for paralellization: process-parallel
PARALLEL_POOL = Pool
THREADING = True # do we want to implement threading?
N_THREADS = 8    # global description of the number of threads

#TODO do we need a wrapper for many-argument functions? What is the model for parallelization over multiple arguments?

#Parallel test #2 - lock instead of queue
#A global lock is inherited by spawned processes instead of pickled
lock = None

class ThreadManager:
    def __init__(self, n_processes=None):
        #A shared queue to be accessed as needed by external functions
        self.Q = Queue()
        self.count = 0

        #default number of processes is CPU count
        if n_processes != None:
            self.n_processes = n_processes
        else:
            self.n_processes = cpu_count()

    #for future use?
    @staticmethod
    def init_lock(L):
        global lock
        lock = L

    def loadQ(self, lst):
        #load the queue from a lst of objects
        for s in lst:
            self.Q.put(s)

    def run(self, func, target, ParallelPool=PARALLEL_POOL):
        #strictly serial
        if ParallelPool == None:
            return map(func, target)

        #Apply func to each object in target, launching parallel processes
        pool = ParallelPool()

        #Initialize a team of workers depending on the concurrency model
        if type(pool) is multiprocessing.pool.Pool:
            #Initialize the current function by providing it the queue
            #for locks - totally serialized code
            #lock = multiprocessing.Lock()
            #pool = ParallelPool(processes, initializer=self.init_lock, initargs=(lock, ))

            pool = ParallelPool(processes=self.n_processes)
        elif type(pool) is multiprocessing.pool.ThreadPool:
            pool = ParallelPool(self.n_processes)
        else:
            raise ParallelError("RunParallel received bad pool specification")


        result = pool.map(func, target)
        #closeout and wait for forks to rejoin main thread before proceeding
        pool.close()
        pool.join()
        return result

    #Different run implementation; excercise finer control over Process dist.
    #Different form from 'run' since Pool does not exist
    #FIXME: Processes need to communicate with a queue to return??
    def run2(self, func, target, Parallel=True):

        if Parallel == False:
            return map(func, target)

        #Distribute the main target array into sub arrays
        split_target = self.distribute_target(target)

        #Error handling
        if split_target == -1:
            raise ParallelError("Cannot distribute target with fewer arguments than proc")

        Ps = []      #list of spawned processes

        #Spawn as many processes as we need and assign to sub-lists
        for i, arg in enumerate(split_target):
            p = Process(target=partial(map,func), args=(arg, ) )
            Ps.append(p)
            p.start()

    #Divide a large array target into n_processes smaller arrays
    #Uneven distribution for small targets
    def distribute_target(self, target):

        #Do not allow distribution if
        if len(target) < self.n_processes:
            return -1

        #get approx subarray length
        N = int(math.floor(len(target) / self.n_processes ))
        out = [ target[i:i+N] for i in range(0, len(target), N) ]

        #Collapse the remaining chunks into the last one
        if len(target) % self.n_processes != 0:
            for rem in out[8:]:
                out[7] += rem
                out.remove(rem)

        return out

        #Assume the value position relates to access time; combine the last two
        #lists if there's more than 8




#FIXME: do we want to limit the input to an array only?
#Decorator for implementing easy parallelism. Decorator is passed the target array
#wrapped function is called in parallel over the target array
#kwargs include threading method and number of processes
# class parallelmethod:
#     """
#     Wraps method to be called in parallel, takes target array as first argument
#     """
#     def __init__(self, target, ParallelPool=PARALLEL_POOL, processes=None):
#         self.target = target
#         self.ParallelPool = ParallelPool
#         self.processes = processes
#
#     def __call__(self, func):
#         """
#         The function is called in parallel, over target array. Each object in the target array must be an acceptable input to func; ie func must have a single argument that matches the contents of target[0]
#         """
#         def applytotarget(*args):
#             return RunParallel(func, self.target, ParallelPool=self.ParallelPool, processes=self.processes)
#         return applytotarget

def do_thing(x,y,z):
    return x + y + z

def do_thing_with_lock(x):
    return x + 1
    current = Parallel.Q.get()
    print current
    current +=1
    Parallel.Q.put(current)
    return current

def f(q):
    s = q.get()
    print s
    s += " augmented"
    time.sleep(1)
    q.put(s)
    #q.close()
    return

def main():
    #cool features of multiprocessing?
    print "number of CPUs: %i" % cpu_count()
    #For future reference: Pool.map is memory intensive, Pool.imap is

    # for y,z in zip(range(10),range(10)):
    #     print partial(do_thing, 5)(y,z)
    Parallel = ThreadManager()
    lst = range(1)
    out = Parallel.run(do_thing_with_lock, lst)
    print out
    # Parallel.queue.put("This is the original string")
    #print Parallel.queue.get()
    # p1 = Process(target=f, args=(Parallel.queue,) )
    # p2 = Process(target=f, args=(Parallel.queue, ))
    # p1.start()
    # p2.start()
if __name__ == "__main__":
    main()
