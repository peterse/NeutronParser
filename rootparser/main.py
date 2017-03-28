"""main.py - Run the neutron parser analysis on a given dataset"""
#TODO:
#   kwargs description

import sys
import os
#FIXME:
package = "/home/epeters/NeutronParser/rootparser"
if package not in sys.path:
    sys.path.insert(0, package)

from timer import Timer

#For parallel computation
import parallel
from parallel import ThreadManager



#For multiprocessing
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

#Errors and logging
from rootparser_exceptions import ChildThreadError, ParallelError, MissingBranchError
from rootparser_exceptions import log

import rootpy.ROOT as ROOT
import rootpy   #root_open
import numpy as np

#Analysis framework
import event
from analysis import ParseEventsNP, testEventAccess, testDuplicateAccess
import analysis
#Debugging
import MINERvAmath as Mm

#I/O
import IO
import shutil
#filtering
import filters as fi

#TODO: set this up as argparse, etc.

script = sys.argv[0]
filename = sys.argv[1]
PATH = sys.argv[2]

target = sys.argv[3]
dest = sys.argv[4]

tmp_dest_files = sys.argv[5]
tmp_dest_hists = sys.argv[6]
tmp_other = sys.argv[7]

filt = sys.argv[8]

#Threading
try:
    N_THREADS = sys.argv[9]
except IndexError:
    N_THREADS = 8
log.info("Setting N_THREADS to %i" % N_THREADS)
parallel.N_THREADS = N_THREADS

#Boot the thread manager with the current tree
Parallel = ThreadManager(n_processes=N_THREADS)     #Threading
Time = Timer(quiet=True)                            #Timing


def main():
    duplicate = analysis.testDuplicateAccess(filename, PATH)
    missing = analysis.testEventAccess(filename, PATH)
    if "event" in missing:
        IO.add_event_branch(filename, PATH)
        missing.remove("event")
    if any(missing):
        log.error("Incomplete set of branches: Edit analysis and rerun")
        sys.exit()
    else:
        log.info("All branches present in tree %s", filename)

    #Basic data quality/efficiency stuff
    #basic_analysis = analysis.basicPlot(filename, PATH, target, dest)

    # #open the file and make a map of parsed events
    #
    # #divide the file into the temporary directory and put together

    #TODO: file checker here: make sure the following exist:
    #   tmp_dest_files
    #   tmp_dest_hists

    #Set the filters based on the filter card
    all_filters = fi.SetFilters(filt)
    #TODO: pickle out filters for parsing during learn
    IO.pickle_filters(all_filters)



    #The filenames and targets from this routine are stored in the temp dest
    filenames = IO.split_file(filename, N_THREADS, path=PATH, dest=tmp_dest_files, recreate=False)

    #Create ParseEvents args package using just filenames
    temp = []
    for fullpath in filenames:
        p, fname = IO.split_path(fullpath)
        temp.append(fname)
    filenames = temp
    paths = [tmp_dest_files for i in range(len(filenames))]
    targets = ["hist%i.root" % i for i in range(len(filenames))]
    dests = [tmp_dest_hists for i in range(len(filenames))]
    tmp = [tmp_other for i in range(len(filenames))]
    #the argument package for ParseEventsNP:
    #(file_to_analyze, path, target_histogram, target_directory, tmp)
    parallel_args = zip(filenames, paths, targets, dests, tmp)

    #Parse the separate files in parallel
    Time.start("Parse Events")
    if N_THREADS > 1:
        event_dct_lst = Parallel.run(analysis.ParseEventsNP, parallel_args, ParallelPool=Pool)
    else:
        event_dct_lst = map(analysis.ParseEventsNP, parallel_args)
    dt1 = Time.end()

    #Join parallel-processed histogram files
    Time.start("Merge Histograms")
    merge_lst = ["%s/%s" % (d, t) for d,t in zip(dests, targets)]
    all_hist_file = IO.join_all_histograms(merge_lst, target, dest)
    dt2 = Time.end()

    #Post-processing final hist_file
    #hi.post_process_hists(all_hist_file)


    #Learn: Regression, correlation

    #cleanup
    for filepath in merge_lst:
        os.remove(filepath)


    return 0


if __name__ == "__main__":

    main()
