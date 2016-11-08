"""analysis.py - non-OO event analysis"""


from IO import versioncontrol
import MINERvAmath as Mm


#utilities
import time
import sys
import os

#File management
import IO
import histogram as hi

import rootpy
import root_numpy as rnp
import numpy as np


#Debugging
sys.path.append("/home/epeters/NeutronParser/tests")
import maketestfiles as testfile
from parallel import ThreadManager
from multiprocessing import Pool
import inspect
#logging
from rootparser_exceptions import log

#Using templates for branchnames, create the list to filter which
@versioncontrol
def make_filter_list(datatype,
                    xyz_prefix="MC_PART_XYZ_PREFIX", energy="MC_PART_E"):
    return

def convert2np(TTree):
    #use root_numpy conversion
    #are vectors supported?
    arr = rnp.root2array(TTree)
    return arr

def ParseEventsNP(filepath, hist=True, filt=True, dump=True):
    #High-level parsing routine
    pid = os.getpid()
    log.info("PID %s parsing %s" % (pid, filepath))

    if hist:
        #Initialize histograms
        a = None
        #FIXME
        # export_lst = hi.extend_export_lst(hi.all_export_lst)
        # subhist_dct = init_hist_dct(export_lst)
        # IO.put_subhist(subhist_dct)

    #Parse input files
    with rootpy.io.root_open(filepath) as fh:
        for subtree in IO.get_next_tree(fh):
            #convert our subtree into an np array
            #TODO:
            datatype = None
            filterlst = make_filter_list(datatype)
            tree_arr = rnp.tree2array(subtree)

            print inspect.getargspec(rnp.tree2array)

def main():

    return

if __name__ == "__main__":
    main()
