"""test_histogram.py - testing and dev for rootpy, matplotlib histograms"""


import sys
package = "/home/epeters/NeutronParser/rootparser"
if package not in sys.path:
    sys.path.insert(0, package)

import unittest
from rootparser_exceptions import log

#IO
import os       #getpid
import rootpy   #.io, root_open
import IO
import maketestfiles as testfile

import histogram

#For multiprocessing
import parallel
from parallel import ThreadManager
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool


Parallel = ThreadManager(n_processes=parallel.N_THREADS)     #Threading

def TestFillHists(tupl):
    #WARNING: this doesn't test 2D hist fill functionality
    #it's a pain to simulate calling this from _within_ a parallel func
    #versus calling it _as_ the parallelized function

    path, histname, vals = tupl[0], tupl[1], tupl[2]

    #TODO: currently writing to tmp_hist/<pid>.root
    #writing hists to a file
    pid = os.getpid()
    path = "%i.root" % pid

    #working in the subprocess' context...
    log.info("initializing histograms")
    histogram.init_histograms()
    histogram.fill_hist(histname, vals)

    #...then filling in the output file context
    histogram.write_hists(path)

    #return whether the put was successful
    #WARNING: histograms only survive in the subprocesses' context!!
    return pid in IO.subhists

class HistogramTest(unittest.TestCase):


    def test_get_put_hist(self):
        #test separate processes get/put to hist dict


        func = TestFillHists
        args = [(None, "null", 0) for i in range(parallel.N_THREADS) ]

        #put histograms in parallel; get them during the same process
        good_put = Parallel.run(func, args, ParallelPool=Pool)
        self.assertTrue(all(good_put))



if __name__ == "__main__":

    #testfile.recreate_testfile()
    unittest.main()
