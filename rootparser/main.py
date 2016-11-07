"""main.py - Run the neutron parser analysis on a given dataset"""
#TODO:
#   kwargs description

import sys
#FIXME:
package = "/home/epeters/NeutronParser/rootparser"
if package not in sys.path:
    sys.path.insert(0, package)

from timer import Timer

#For parallel computation
import parallel
from parallel import ThreadManager

import numpy as np

#For multiprocessing
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

#Errors and logging
from rootparser_exceptions import ChildThreadError, ParallelError
from rootparser_exceptions import log

import rootpy.ROOT as ROOT
import rootpy   #root_open
import event


dirname = "~/NeutronParser/sample"
filename = "merged_CCQEAntiNuTool_minervamc_nouniverse.root"
N_THREADS = Parallel.N_THREADS

TMP = testfile.TMP      #location of temporary
#Boot the thread manager with the current tree
Parallel = ThreadManager(n_processes=parallel.N_THREADS)     #Threading
Time = Timer(quiet=True)

def main():

    #open the file and make a map of parsed events

    #divide the file into the temporary directory
    paths = IO.split_file(filename, N_THREADS, path=dirname, dest=testfile.TMP, recreate=True)

    Time.start("Parse Events" % (i+1) )
    #form an unordered list of sublists of events
    parsed_evts = Parallel.run(event.ParseEvents, paths, ParallelPool=Pool)
    dt1 = Time.end()

    #Join parallel-processed events
    all_evts = IO.join_all_events(parsed_evts)



return 0
