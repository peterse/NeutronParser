from multiprocessing import Pool
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool as ThreadPool
import time as time
import numpy as np

from timer import Timer

def numpy_compute(arr):
    arr = np.square(arr)
    print len(arr)
    #print "squaring complete"

def test_CPU_bound(func, obj_lst):

    #CPU-bound routine:
    Time.start("CPU-parallel")
    #Boot the threads
    pool = ThreadPool(cpu_count())

    #Map a function of an object to a list of objects to process
    pool.map(func, obj_lst)

    # join threads, finish off timer
    pool.close()
    pool.join()
    Time.end()


def test_IO_bound(func, obj_lst):
    #I/O-bound routine:
    Time.start("thread-parallel")
    #Boot the threads
    pool = ThreadPool(cpu_count())

    #Map a function of an object to a list of objects to process
    pool.map(func, obj_lst)

    # join threads, finish off timer
    pool.close()
    pool.join()
    Time.end()

def test_serial(func, obj_lst):
    #serial
    Time.start("serial")
    for arr in dummy_arr:
        numpy_compute(arr)
    Time.end()

def main():
    #cool features of multiprocessing?
    print "number of CPUs: %i" % cpu_count()

    Time = Timer()
    #set up a list of objects to manipulate with separate threads
    dummy_arr = [ np.array(range(100*i)) for i in range(2000) ]

    test_serial(numpy_compute, dummy_arr)
    test_IO_bound(numpy_compute, dummy_arr)
    test_CPU_bound(numpy_compute, dummy_arr)







    return 0




if __name__ == "__main__":
    main()
