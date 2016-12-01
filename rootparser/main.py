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
PATH = sys.argv[2]
target = sys.argv[3]
dest = sys.argv[4]

tmp_dest = sys.argv[5]
try:
    N_THREADS = sys.argv[6]
except IndexError:
    N_THREADS = parallel.N_THREADS
    log.info("Setting N_THREADS to %i" % N_THREADS)

#Boot the thread manager with the current tree
Parallel = ThreadManager(n_processes=N_THREADS)     #Threading
Time = Timer(quiet=True)                            #Timing


def main():
    missing = testEventAccess(filename, PATH)
    if "event" in missing:
        IO.add_event_branch(filename, PATH)
        missing.remove("event")
    if any(missing):
        log.error("Incomplete set of branches: Edit analysis and rerun")
        sys.exit()

    #Parallel ParseEventsNP
    """
    TODO:
        -change func params to tupl of current params?
        - output full name/PATH of target
        -merge target histogram files

    """
    # #open the file and make a map of parsed events
    #
    # #divide the file into the temporary directory and put together
    #The filenames and targets from this routine are stored in the temp dest
    filenames = IO.split_file(filename, N_THREADS, path=PATH, dest=tmp_dest, recreate=False)
    #just the filenames...
    temp = []
    for fullpath in filenames:
        p, fname = IO.split_path(fullpath)
        temp.append(fname)
    filenames = temp
    paths = [tmp_dest for i in range(len(filenames))]
    targets = ["hist%i.root" % i for i in range(len(filenames))]
    dests = [tmp_dest for i in range(len(filenames))]
    #the argument package for ParseEventsNP
    parallel_args = zip(filenames, paths, targets, dests)
    for entry in parallel_args:
        print entry




    sys.exit()
    Time.start("Parse Events")
    #Parse the separate files in parallel
    complete_lst = Parallel.run(ParseEventsNP, parallel_args, ParallelPool=Pool)
    dt1 = Time.end()

    #Output should be clean
    if complete_lst != [0 for i in range(N_THREADS)]:
        log.error("Failure mode returned non-zero in analysis.ParseEventsNP")
        sys.exit()
    else:
        merge_targets = ["%s/%s" % (d, t) for d,t in zip(dests, targets)]

    #Join parallel-processed histogram files


    return 0

if __name__ == "__main__":

    main()
