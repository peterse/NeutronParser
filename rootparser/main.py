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
from rootparser_exceptions import ChildThreadError, ParallelError, MissingBranchError
from rootparser_exceptions import log

import rootpy.ROOT as ROOT
import rootpy   #root_open

#Analysis framework
import event
from analysis import ParseEventsNP, testEventAccess

#TODO: set this up as argparse, etc.




#Boot the thread manager with the current tree
Parallel = ThreadManager(n_processes=parallel.N_THREADS)     #Threading
N_THREADS = parallel.N_THREADS


filename = "merged_CCQEAntiNuTool_minervamemc_nouniverse.root"
path = "~/NeutronParser/sample2"
target = "Analysis2.root"
dest = path

Time = Timer(quiet=True)


def main():

    if testEventAccess(filename, path) == 1:
        log.error("Incomplete set of branches: Edit analysis and rerun")
        #sys.exit()
    ParseEventsNP(filename, path, target, dest)

    # #open the file and make a map of parsed events
    #
    # #divide the file into the temporary directory
    # paths = IO.split_file(filename, N_THREADS, path=dirname, dest=testfile.TMP, recreate=True)
    #
    # Time.start("Parse Events" % (i+1) )
    # #form an unordered list of sublists of events
    # parsed_evts = Parallel.run(event.ParseEvents, paths, ParallelPool=Pool)
    # dt1 = Time.end()
    #
    # #Join parallel-processed events
    # all_evts = IO.join_all_events(parsed_evts)

    return 0

if __name__ == "__main__":
    main()
