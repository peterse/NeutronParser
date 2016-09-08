"""
Methods for parallelization; speedup will depend on implementation and whether the processes are cpu-bound, I/O-bound, etc.
"""
import multiprocessing
from multiprocessing import Pool
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool

#from functools import partial

#Default mode for paralellization: process-parallel
PARALLEL_POOL = Pool

#TODO do we need a wrapper for many-argument functions? What is the model for parallelization over multiple arguments?

def RunParallel(func, target, ParallelPool=PARALLEL_POOL, processes=None):
    #Apply func to each object in target, launching parallel processes
    pool = ParallelPool()
    if processes == None:
        processes = cpu_count()
    #Initialize a team of workers depending on the concurrency model
    if type(pool) is multiprocessing.pool.Pool:
        pool = ParallelPool(processes=processes)
    elif type(pool) is multiprocessing.pool.ThreadPool:
        pool = ParallelPool(processes)
    else:
        raise ParallelError("RunParallel received bad pool specification")

    result = pool.map(func, target)
    #closeout
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


def main():
    #cool features of multiprocessing?
    print "number of CPUs: %i" % cpu_count()
