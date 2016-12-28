"""learn.py - implement different forms of Machine Learning on
    the neutron blob data
"""

from IO import versioncontrol
import MINERvAmath as Mm


#utilities
import time
import sys
import os

#File management
import IO
import histogram as hi
import ROOT

import rootpy
import root_numpy as rnp

#Numpy, and formatting
import numpy as np
np.set_printoptions(suppress=True)
import pandas as pd

#evts and filters
import event
import filters as fi

#regex for matching br names
import re

#Debugging
sys.path.append("/home/epeters/NeutronParser/tests")
import maketestfiles as testfile
from parallel import ThreadManager
from multiprocessing import Pool

import inspect
#logging
from rootparser_exceptions import log


def branches_to_get():
    #Return a list of branchnames that we care about
    out = []

    #Basic requirements: All of the data we've parsed
    for k, br in IO.lookup_dct.iteritems():
        if br is None:
            continue
        #Expand prefixes
        if "PREFIX" in k:
            out += IO.expand_prefix(br)
        else:
            out.append(br)

    #TODO: Additional branches on which to regress

    return out

def flatten_array(arr):
    """
    Take the given np.array and remove nested tupls. Send the tupl components to
    named fields with <original name>[i] in a new structured arr
    Args:
        -arr: a np array with nested tuples

    Return: A flat structured array w/ numeric dtypes only. Will not contain
    the same columns as the input arr
    """

    #FIXME
    #Current strategy: Allow a maximum of 10 particles , 10 blobs
    #Make a new ndarray with names as col[i] for i-many entries
    N_MAX = 10
    fieldnames = []
    formats = []
    for i, col in enumerate(arr[0]):

        #get current field info, datatype, etc.
        fieldname = arr.dtype.names[i]
        try:
            dims = len(col)
        except TypeError:
            dt = type(col)
            dims = 1
        else:
            dt = type(col[0])

        #The flattened array will do the following
        #mc_FSPartPz -> mc_FSPartPz0 ... mc_FSPartPz<N_MAX-1>
        #mc_vtx -> mc_vtx0,... mcvtx3
        #etc...

        #nested particle values
        if IO.is_prefix_br(fieldname):
            names = IO.expand_prefix(fieldname)
            for br_name in names:
                for i in range(N_MAX):
                    fieldnames.append(br_name+str(i))
                    formats.append(dt)
        #length-3,4 vectors
        elif dims > 1:
            for i in range(dims):
                fieldnames.append(fieldname+str(i))
                formats.append(dt)
        #scalars
        else:
            fieldnames.append(fieldname)
            formats.append(dt)

    dt_dct = dict(names=fieldnames, formats=formats)
    return dt_dct
    newdt = np.dtype(  )
    out = np.array()

def make_clean_data(filename, dct):
    """
        Take a prepared dct from ParseEventsNP that finds good events
        and categorizes/locates blobs. Form an np.array from the rootfile
        using these events only, and keeping only relevant columns
        Arguments:
            filename - rootfile
    """

    FNAME = "/home/epeters/NeutronParser/sample4/merged_CCQEAntiNuTool_minervamc_nouniverse_nomec.root"

    #Select specific branches
    brs = branches_to_get()

    #FNAME = testfile.MC_filename
    with rootpy.io.root_open(FNAME) as fh:
        for subtree in IO.get_next_tree(fh):

            #Do the initial np conversion
            log.info("Converting tree %s to numpy array..." % subtree.GetName())
            tree_arr = rnp.tree2array(subtree, branches=brs)
            log.info("...conversion finished")

            #Flatten the array out
            #tree_arr = flatten_array(tree_arr)

            if len(tree_arr) == 0:
                continue
            return tree_arr
            rows = len(tree_arr)
            cols = len(tree_arr[0])
            print rows, cols
            print tree_arr[0]
            for item in tree_arr[0]:
                print item, type(item)
            test1 = np.array([0,1,2,3])
            test2 = np.array([ (0,1, np.array([2,3])) ], dtype="int8, int8, 2int8")
            df1 = pd.DataFrame(test1)
            print "df1"
            df2 = pd.DataFrame(test2)
            print "df2"


            return
            tree_arr.reshape(rows, cols)
            #AGh - DataFrame isn't taking...problems:
            #   cannot contain list types
            #   cannot contain nested tupls -> remake into 5000Xlen(tuple) ndarray?

            return
            print tree_arr.shape
            print tree_arr.ndim
            df = pd.DataFrame(tree_arr)
            print df.info()
            return
            print tree_arr.dtype.names
            print tree_arr

def BlobClassifier(tupl, hist=True, filt=True, dump=True, ML=False):

    """
    Passed a
    Return:
      The input tuple - this will be parsed to grab the target histograms
    Args:
    tupl components
      [0] filename is the file being analyzed
      [1] path is its location
      [2] target is the desired output filename
      [3] dest is its location

    KWArgs:
      filt:
      dump:
      hist:
      ML:
    """
    return



def MLsandbox(filename, path, target, dest, hist=True, filt=True, dump=True):
    pid = os.getpid()
    filepath = "%s/%s" % (path, filename)
    log.info("PID %s parsing %s" % (pid, filepath))

    with rootpy.io.root_open(filepath) as fh:
        for subtree in IO.get_next_tree(fh):
            #pass the tree to the global space for access by funcs
            IO.put_subtree(pid, subtree)

            #convert our subtree into an np array
            #TODO:
            datatype = 0
            filterlst = make_filter_list(datatype)
            tree_arr = rnp.tree2array(subtree)
            print tree_arr.dtype.names
            print tree_arr[0]
