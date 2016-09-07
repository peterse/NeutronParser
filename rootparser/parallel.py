"""Methods for parallelization; speedup will depend on implementation and whether the processes are cpu-bound, I/O-bound, etc."""
import multiprocessing
from multiprocessing import Pool
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool

#from functools import partial


#TODO do we need a wrapper for many-argument functions? What is the model for parallelization over multiple arguments?

def parallelize(func, target, ParallelPool=Pool):
    pool = ParallelPool()
    #Initialize a team of workers depending on the concurrency model
    if type(pool) is multiprocessing.pool.Pool:
        pool = ParallelPool(processes=1)
    elif type(pool) is multiprocessing.pool.ThreadPool:
        pool = ParallelPool(cpu_count())
    else:
        raise ParallelError("parallelize received bad pool specification")

    result = pool.map(func, target)
    #closeout
    pool.close()
    pool.join()

    return result




def main():
    #cool features of multiprocessing?
    print "number of CPUs: %i" % cpu_count()
