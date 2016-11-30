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

#Debugging
import MINERvAmath as Mm

#I/O
import IO

#TODO: set this up as argparse, etc.

script = sys.argv[0]
filename = sys.argv[1]
path = sys.argv[2]
target = sys.argv[3]
dest = sys.argv[4]

tmp_dest = sys.argv[5]


#Boot the thread manager with the current tree
Parallel = ThreadManager(n_processes=parallel.N_THREADS)     #Threading
N_THREADS = parallel.N_THREADS

Time = Timer(quiet=True)


def main():

    missing = testEventAccess(filename, path)
    if "event" in missing:
        IO.add_event_branch(filename, path)
        missing.remove("event")
    if any(missing):
        log.error("Incomplete set of branches: Edit analysis and rerun")
        sys.exit()

    #Parallel ParseEventsNP
    """
    TODO:
        -change func params to tupl of current params?
        - output full name/path of target
        -merge target histogram files

    """
    # #open the file and make a map of parsed events
    #
    # #divide the file into the temporary directory and put together
    #The filenames and targets from this routine are stored in the temp dest
    filenames = IO.split_file(filename, N_THREADS, path=path, dest=tmp_dest, recreate=True)
    paths = [tmp_dest for i in range(len(filenames))]
    targets = ["hist%i.root" for i in range(len(filenames))]
    dests = [tmp_dest for i in range(len(filenames))]
    #the argument package for ParseEventsNP
    parallel_args = zip(filenames, paths, targets, dests)

    Time.start("Parse Events")
    #Parse the separate files in parallel
    parsed_evts = Parallel.run(ParseEventsNP, parallel_args, ParallelPool=Pool)
    dt1 = Time.end()
    #
    # #Join parallel-processed events

    return 0

if __name__ == "__main__":
    main()
