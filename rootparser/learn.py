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

#Correlation functions
import scipy

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
import matplotlib.pyplot as plt

import inspect
#logging
from rootparser_exceptions import log



BRANCHES_TO_GET = ["CCQEAntiNuTool_Q2", "mc_targetZ",
        "mc_Q2", "mc_nFSPart",
        "event", "CCQEAntiNuTool_E_mu",
        "CCQEAntiNuTool_px_mu", "CCQEAntiNuTool_py_mu",
        "CCQEAntiNuTool_pz_mu", "mc_intType",
        "mc_incomingE"]

COLUMNS_TO_MAKE = ["blob_dE", "blob_dX", "blob_dY", "blob_dZ",
        "dphiXY", "dthetaXZ", "dthetaYZ"]

col_classes = {"CCQEAntiNuTool_Q2": "ratio",
                "mc_targetZ": "nomial",
                "mc_Q2": "ratio",
                "mc_nFSPart": "ratio",
                "event": "ordinal",
                "CCQEAntiNuTool_E_mu": "ratio",
                "CCQEAntiNuTool_px_mu": "ratio",
                "CCQEAntiNuTool_py_mu": "ratio",
                "CCQEAntiNuTool_pz_mu": "ratio",
                "mc_intType": "nominal",
                "mc_incomingE": "ratio"}

#TODO:
def check_col_classes(cols, class_dct):
    #Make sure that all df columns are classified
    return

def branches_to_get():
    #Return a list of branchnames that we care about
    out = []
    #
    #
    # #Basic requirements: All of the data we've parsed
    # for k, br in IO.lookup_dct.iteritems():
    #     if br is None:
    #         continue
    #     #Expand prefixes
    #     if "PREFIX" in k:
    #         out += IO.expand_prefix(br)
    #     else:
    #         out.append(br)

    #TODO: Additional branches on which to regress
    #Correlation studies: remove unecessary vars
    out = ["CCQEAntiNuTool_Q2", "mc_targetZ",
            "mc_Q2", "mc_nFSPart",
            "event", "CCQEAntiNuTool_E_mu",
            "CCQEAntiNuTool_px_mu", "CCQEAntiNuTool_py_mu",
            "CCQEAntiNuTool_pz_mu", "mc_intType",
            "mc_incomingE"]

    return out

def columns_to_create():
    #just a list of columns that analysisNP will output
    out = ["blob_dE", "blob_dX", "blob_dY", "blob_dZ",
            "dphiXY", "dthetaXZ", "dthetaYZ"]
    return out

def make_correlation_pairs():
    #put together pairs of column names to correlate
    out = []
    global col_classes
    for x in branches_to_get():
        #I have listed all of the columns to analyze..
        for y in columns_to_create():
            #only use ratio-valued vars
            if col_classes.get(x) == "ratio":
                out.append((x,y))

    return out

def pad_array(arr):
    """
    Given a ragged array of arrays, pad the array entries
    By default, pad to the largest array length to preserve all data
    """

    #Get a list of entry lengths for the ragged array
    lens = np.array( map(lambda x: len(x), arr) )
    N = max(lens)

    pad_lens = N - lens
    pads = [np.zeros(L) for L in pad_lens]

    merged = [None for i in range(len(arr))]
    for i, (row, pad) in enumerate(zip(arr, pads)):
        merged[i] = np.concatenate( (row, pad) )

    return np.array(merged)


def flatten_array(arr):
    """
    Take the given np.array and remove nested tupls. Send the tupl components to
    named fields with <original name>[i] in a new structured arr
    Args:
        -arr: a np array with nested tuples

    Return: A flat structured array w/ numeric dtypes only. Will not contain
    the same columns as the input arr
    """

    new_arrs = []
    base = "uncomparable_string"

    #We will keep track of (new) column names to conver to
    #a structured array after concatating all of the padded arrs
    fieldnames = []
    formats = []

    #Flatten columns whose entries are objects == np.arrays
    log.info("Flattening vector-type columns and padding to max vector length")
    for i, name in enumerate(arr.dtype.names):

        dt = arr.dtype.fields[name][0]
        # print name, dt.type
        # print arr[name][0]
        # print "ndim:", arr[name][0].ndim
        # print "shape:", arr[name][0].shape
        # print "kind:", dt.kind
        # print "dtype", np.dtype(dt)
        # print "is scalar:", np.issctype(np.dtype(dt)), "\n"
        # #print "is object:", np.dtype(dt) == np.dtype(object)
        # #print "can cast:", np.can_cast(np.dtype(dt), np.dtype(object)), "\n"
        # continue

        if np.dtype(dt)==np.dtype(object) or dt.type==np.void:
            # 1: produce a padded array for this column
            padded = pad_array(arr[name])
            dims = np.shape(padded)

            #2: generate new formats and fieldnames
            i_fieldnames = [name+str(j) for j in range(dims[1])]
            i_formats = [type(val) for val in padded[0]]
            #dt_dct = dict(names=fieldnames, formats=formats)

            #3: produce a new structured array based on this data
            #Bit of a hack to get this to behave...
            #new = np.core.records.fromarrays(padded.transpose(), dtype=dt_dct)

            new = padded
            #I'm taking it on good faith that padding succeeded
            #new = new.reshape(len(new), len(new[0]))
        else:
            #Otherwise, keep scalar columns (but make them columns!)
            i_fieldnames = [name]
            i_formats = [type(arr[name][0])]
            new = arr[name]
            # new = np.array(arr[name], dtype=dt_dct)
            new = new.reshape(len(new), 1)


        #4 stack these columns onto the rest of our flattened arrs
        fieldnames += i_fieldnames
        formats += i_formats
        if base == "uncomparable_string":
            base = new
        else:
            base = np.hstack( (base,new) )

    #4: label the columns in the new, padded, 2D array
    dt_dct = dict(names=fieldnames, formats=formats )
    out = np.core.records.fromarrays(base.transpose(), dtype=dt_dct)
    return out

    # return
    # for i, col in enumerate(arr[0]):
    #
    #     #Make a new ndarray with names as col[i] for i-many entries
    #
    #     #get current field info, datatype, etc.
    #     fieldname = arr.dtype.names[i]
    #     try:
    #         dims = len(col)
    #     except TypeError:
    #         dt = type(col)
    #         dims = 1
    #     else:
    #         dt = type(col[0])
    #
    #     #The flattened array will do the following
    #     #mc_FSPartPz -> mc_FSPartPz0 ... mc_FSPartPz<N_MAX-1>
    #     #mc_vtx -> mc_vtx0,... mcvtx3
    #     #etc...
    #
    #     #nested particle values
    #     if IO.is_prefix_br(fieldname):
    #         names = IO.expand_prefix(fieldname)
    #         for br_name in names:
    #             for i in range(N_MAX):
    #                 fieldnames.append(br_name+str(i))
    #                 formats.append(dt)
    #     #length-3,4 vectors
    #     elif dims > 1:
    #         for i in range(dims):
    #             fieldnames.append(fieldname+str(i))
    #             formats.append(dt)
    #     #scalars
    #     else:
    #         fieldnames.append(fieldname)
    #         formats.append(dt)
    #
    #
    # print dt_dct
    # return dt_dct
    #
    # padded = pad_array()
    #
    # return dt_dct
    # newdt = np.dtype(  )
    # out = np.array()

def reconstruct_vals_mc(df):
    """
    Analysis-specific calculations to reconstruct important
    quantities from the labeled df and then shave it
    """

    #Fat cost: Pick our correct particles

    # df["E_mu"] = pd.Series( , index=df.index)
    # df["px_mu"] =
    # df["py_mu"] =
    # df["pz_mu"] =

def make_clean_dataframe(filename, dct):
    """
    Take a prepared dct from ParseEventsNP that finds good events
    and categorizes/locates blobs. Form an np.array from the
    rootfile using these events only, and keeping only relevant
    columns
    Args:
        filename - rootfile
    """

    #DEBUG:
    FNAME = "/home/epeters/NeutronParser/sample4/merged_CCQEAntiNuTool_minervamc_nouniverse_nomec.root"
    DCT = {"event": range(20), "DERP": range(20,40)}

    if filename is None:
        filename = FNAME
    if dct is None:
        dct = DCT

    #convert the input dct to a dataframe
    tags_df = pd.DataFrame(dct)

    #Select specific branches
    brs = branches_to_get()
    log.info("The following branches will be captured: %s" \
                % "\n\t".join(brs))

    #Various filters to save our precious memory
    mc_FSPart_max = 10
    selection_str = "mc_nFSPart < %i" % mc_FSPart_max


    #FNAME = testfile.MC_filename
    with rootpy.io.root_open(filename) as fh:
        for subtree in IO.get_next_tree(fh):

            #Do the initial np conversion
            log.info("Converting tree %s to numpy array..." % subtree.GetName())
            #tree_arr = rnp.tree2array(subtree, branches=brs, selection=selection_str)
            tree_arr = rnp.tree2array(subtree, branches=brs)
            log.info("...conversion finished")

            #Select for good events from input dct
            good_evts = set(dct.get("event"))
            @np.vectorize
            def selected(e_i): return e_i in good_evts
            tree_arr = tree_arr[ selected(tree_arr["event"])]

            #Flatten the array out so that vectors do not produce ragged edges
            #TRUNCATES AT MAX PARTICLES
            tree_arr = flatten_array(tree_arr)
            if len(tree_arr) == 0:
                continue
            tree_df = pd.DataFrame(tree_arr)

            #merge the tree_array with the input tags:
            df_all = pd.merge(tags_df, tree_df, on="event")

            return df_all


def pearson_correlate_cols(df, pairs, report=True, plot=True):
    """
    Compute the correlation between each pair of columns in pairs
    Args:
        -df: dataframe, containing all cols listed in pairs
        -pairs: list of tuples of (col1, col2) string names
    Return:
        -out: list of (col1, col2, r, pval)
    """
    out = []
    from scipy.stats import pearsonr

    if plot:
        count = 1
        fig = plt.figure()

    for i, pair in enumerate(pairs):
        x = df[pair[0]]
        y = df[pair[1]]
        r, pval = pearsonr(x,y)
        grp = (pair[0], pair[1], r, pval)
        if report:
            print "Columns %s vs %s:\n   r=%f p=%f" % grp

        if plot:

            ax = fig.add_subplot(2,2,count)
            ax.set_xlabel(pair[0])
            ax.set_ylabel(pair[1])
            ax.scatter(x,y)
            count += 1
            #plot full fig or final plotset
            if count == 4 or i == len(pairs)-1:
                plt.show()
                fig = plt.figure()
                count = 1

        out.append(grp)
    #Sort by the pair r-values
    return sorted(out, key=lambda x: x[2])

def plot_cols(df, col1, col2, fig=None):
    #plot col2 vs col1
    if fig==None:
        fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel(col1)
    ax.set_ylabel(col2)
    ax.scatter(df[col1], df[col2])

    return ax


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

def main():
    #TEST
    dct = IO.load_obj("../temp/0.pickle")
    df = make_clean_dataframe(None, dct)
    pairs = make_correlation_pairs()
    return df, pairs
    #pairs = [()]
    #correlations = pearson_correlate_cols(full_df, pairs)


if __name__ == "__main__":
    main()
