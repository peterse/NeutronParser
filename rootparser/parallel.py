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

#Default mode for paralellization: process-parallel
PARALLEL_POOL = Pool
THREADING = True # do we want to implement threading?

#TODO do we need a wrapper for many-argument functions? What is the model for parallelization over multiple arguments?


#Parallel test #2 - lock instead of queue
#A global lock is inherited by spawned processes instead of pickled
lock = None

class ThreadManager:
    def __init__(self):
        #A shared queue to be accessed as needed by external functions
        #self.queue = Queue()
        self.count = 0

    #for future use?
    @staticmethod
    def init_lock(L):
        global lock
        lock = L

    def run(self, func, target, ParallelPool=PARALLEL_POOL, n_processes=None):
        #strictly serial
        if ParallelPool == None:
            return map(func, target)


        #Apply func to each object in target, launching parallel processes
        pool = ParallelPool()

        if n_processes == None:
            n_processes = cpu_count()
        #Initialize a team of workers depending on the concurrency model
        if type(pool) is multiprocessing.pool.Pool:
            #Initialize the current function by providing it the queue
            #for locks - totally serialized code
            #lock = multiprocessing.Lock()
            #pool = ParallelPool(processes, initializer=self.init_lock, initargs=(lock, ))

            pool = ParallelPool(processes=n_processes)
        elif type(pool) is multiprocessing.pool.ThreadPool:
            pool = ParallelPool(n_processes)
        else:
            raise ParallelError("RunParallel received bad pool specification")


        result = pool.map(func, target)
        #closeout and wait for forks to rejoin main thread before proceeding
        pool.close()
        pool.join()
        return result




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
    current = Parallel.queue.get()
    print current
    current +=1
    Parallel.queue.put(current)
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
