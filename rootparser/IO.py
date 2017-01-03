"""
IO.py - supports I/O for parsing rootfiles, particularly naming
conventions for finding specific values in the tree
"""

import rootpy.ROOT as ROOT
import rootpy
from rootparser_exceptions import log

#Tree templating & functions
from rootpy.tree import Tree, TreeModel, FloatArrayCol
from rootpy import stl #std library?

#histogramming interfac
#import histogram as hi
#import ROOT
import os
import sys
import subprocess #call, check_output
import shutil
import math

#Debugging
sys.path.append("/home/epeters/NeutronParser/tests")
#FIXME: Why can't I import exceptions??

######################################################################

# # # # GLOBAL OBJECTS # # # # #
#File managers for testing parallel returns
global_f = None #IO filehandle
tree = None # tree handle
subtrees = {}
subhists = {}

#where combined histogram objects are written to
OUTFILE = None

#rootpy isn't very helpful in providing class type for hists
hist_type = type(rootpy.plotting.Hist(1,0,1))

######################################################################
#Histogram management

def get_subhist():
    #grab a stashed histogram dictionary
    global subhists
    pid = os.getpid()
    out = subhists.get(pid)

    if out:
        return out
    else:
        raise IOError("PID %s subhist not found" % str(pid))

def put_subhist(hist_dct):
    #store a hist dict for this PID
    global subhists
    pid = os.getpid()
    subhists[pid] = hist_dct

def join_all_histograms(file_lst, target, dest):
    """
    For a list of TFiles with identical content, add all hist content into
    a single master histogram
    Args:
        file_lst: a list of strings for full paths of targets
        target: The name of the merged file
        dest: Where the merged file will be saved
    Return:
        String with full path of merged file

    Warning! One target histogram file will be destroyed!
    """
    f_p = [(d,f) for d,f in [split_path(p) for p in file_lst] ]
    target_path = "%s/%s" % (dest, target)

    #copy the first file as a base for addition
    #shutil.copy(file_lst[0], target_path)


    #build upon the first rootfile's histograms
    base = "%s/%s" % f_p[0]
    log.info("The following histogram files will be summed into %s\n" % base \
            + "  \n".join(["%s/%s" % (d,f) for d,f in f_p[1:]]) )

    #get a list of the histograms we're going to iterate over:
    all_hists = []
    with cd(dest):
        with rootpy.io.root_open(base) as s1:
            for p, d, obj_lst in s1.walk():
                for name in obj_lst:
                    handle = s1.Get(name)
                    if type(handle) is hist_type:
                        all_hists.append(name)

        i=0
        for other_file in file_lst[1:]:
            #BUG: opening these as inner context dumped entire contents into outer context...
            with rootpy.io.root_open(other_file, "r") as s2:
                #iterate over the histograms we know we've generated
                for histname in all_hists:
                    hist2 = s2.Get(histname)
                    with rootpy.io.root_open(base, "UPDATE") as s1:
                        #add the histograms into a clone...
                        hist1 = s1.Get(histname)
                        hist1.Add(hist2)
                        hist1.Write("temp")
                        #s1.Write()
                        #...and murder the original - THE PRESTIGE!
                        s1.Delete(histname+";1")
                        s1.Get("temp").SetName(histname)
                        s1.Get(histname).Write()
                        s1.Delete("temp;1")

            #skip those you can't find (try)

    log.info("Histograms collapsed into file %s" % base)
    return base

######################################################################

def join_all_events(evt_lst):
    #passed a list of (lists of event objects) concatenate them (in order)
    #This requires reconstruction of event numbers - occurs at end of event.fill

    index_sorted = sorted(evt_lst, key=lambda x: x[0].index)
    #print [evt.index for evt in index_sorted]
    #Flatten the list according to the index of the first event of each sublst
    out = [evt for sublst in index_sorted for evt in sublst ]
    return out

def put_subtree(pid, subtree):
    #When a process starts, it needs to store its respective tree globally
    #store it in a dct under the callers PID
    global subtrees
    pid = os.getpid()
    subtrees[pid] = subtree

def get_subtree():
    #When a process asks for a tree, give it one through this method
    #Expects to be called within the context of a process
    global subtrees
    pid = os.getpid()
    out = subtrees.get(pid)

    if out:
        return out
    else:
        raise IOError("PID %s tree not found" % str(pid))


        #raise IOError("I/O tree was not generated")

def get_next_tree(fh):
    #Given a  rootfile handle, generate the next tree object
    #Precondition: fh must be an active (open) file handle
    #FIXME:
    #FIXME: (I think) this must be fully exhausted in the file context...
    #FIXME: needs to give ONLY TREES to maintain backwards compatibility

    # for sub in fh.GetListOfKeys():
    #     name = sub.ReadObj().GetName()
    #     yield fh.Get(name)


    for path, dirs, obj_lst in fh.walk():
        for name in obj_lst:
            # log.info("name "+ name)
            # log.info("getname "+ fh.Get(name).GetName())
            handle = fh.Get(name)
            if type(handle) is rootpy.tree.tree.Tree:
                yield handle
                #continue    #move onto the next tree

######################################################################
#Sub-Tree splitting:

def path_exists(path):
    #check that the directory 'path' exists
    try:
        with cd(path) as d:
            pass
    except:
        #FIXME: what's the error I'm looking for?
        print sys.exc_info()[0]
        return False
        sys.exit()


    return True

def file_exists(f):
    #try to find the file in the current context
    try:
        rootpy.io.root_open(f)
    except rootpy.io.DoesNotExist:
        return False
        #raise IOError("root file ")
    return True

#TODO:

def get_event_branch(tree):
    #Passed a treehandle, return a string for its 'event' branch

    #Make sure our supposed event branch exists
    return "event"

def make_cuts_lst(T, N):
    #Divide T into N segments
    #return a list of cut indices

    #This indicates a broken tree; pass it up the pipe
    #FIXME: where do we handle this?
    if T == 0:
        return [0 for i in range(N)]

    if N > T:

        diff = N - T
        N = T
    else:
        diff = 0

    rem = T % N
    dn = int(math.floor(T) / N)         #distance between each cut
    out = [ i*dn for i in range(N ) ]
    #Special case: Return a list with repeating cut indices for N > T:
    #eg N = 8, T = 5 -> out = [0, 1, 2, 3, 4, 5, 5, 5]
    if diff:
        last = out[-1]
        for i in range(diff):
            out.append(last)
    return out

def split_file(src, N, path=None, dest=None, recreate=True):
    #Split the main TTree of a Rootfile and distribute it into N different files
    #Populates the global list 'subtrees' with handles of smaller tree types
    #Input: path, src: where we're splitting from
    #       dest, target: where the result is written
    #       N - the number of 'subtrees' we want == (N_cuts + 1)
    #       recreate - overwrite the files. if False, this will keep the prev
    #                   files iff there are 'N' of them
    #Return: list of 'path/filename' for N files created
    global subtrees, tree

    #Assume we're in the current directory
    if path == None:
        path = os.getcwd()
    if dest == None:
        dest = os.getcwd()

    #Do a check on N/files before calling it.
    if recreate == False:
        with cd(dest):
            fnames = os.listdir(os.getcwd())
            N_files = len(fnames)
            if N_files == N:
                return ["%s/%s" % (dest, fname) for fname in fnames]
            else:
                log.warning("Number of files at %s does not match N_pipelines; recreating files..." % dest)

    #Make sure the source file and its path are valid
    if not path_exists(path):
        raise IOError("Bad path at %s - Could not enter directory" % path)

    with cd(path) as d:
        if not file_exists(src):
            raise IOError("Bad file path at %s/%s - could not enter file '%s'" % (path, src, src))

    #Make sure the destination is valid
    #User must handle cleanup! We have no idea the contesxt of their dest
    if not path_exists(dest):
        raise IOError("Bad destination at %s - Could not enter directory" % dest)

    src = "%s/%s" % (path, src)
    #Parse the current rootfile and divide its trees up


    all_hists = []
    all_trees_meta = []  #list of (tree_handle, cuts_list, evt_str)
    fnames = []          #filenames to return

    log.info("Slicing %s into %i files at %s" % (src, N, dest))
    #CONTEXT: SOURCE FILE FROM WHICH WE WILL CUT TREES AND HISTS
    with rootpy.io.root_open(src, "READ") as s:

        #FIXME : we don't really need to copy over hists
        # #1: get a list of all the histograms in this file
        for path, dirs, obj_lst in s.walk():
            for name in obj_lst:
                handle = s.Get(name)
                if type(handle) is hist_type:
                    all_hists.append(handle)

        #2: get a list of all the trees in this file
        for path, dirs, obj_lst in s.walk():
            i_tree = -1
            for name in obj_lst:
                handle = s.Get(name)
                if type(handle) is rootpy.tree.tree.Tree:
                    i_tree += 1
                    this_tree = handle
                    #Where to make our cuts and along which branch
                    T = handle.GetEntries()
                    cuts = make_cuts_lst(T, N)
                    evt_str = get_event_branch(handle)
                    #all_trees_meta.append((handle, cuts, evt_str))


        # #3: for each tree in the source file, write cuts into N_THREADS target files
        #
        # print "TUPLES"
        # for tupl in all_trees_meta:
        #     print tupl, "\n"

                    #OUTER CONTEXT: SOURCE FILE FROM WHICH WE WILL CUT TREES AND HISTS
                    #INNER CONTEXT(S): ALL TARGET FILES INTO WHICH WE WILL WRITE CUT TREES/HISTS
                    with cd(dest):
                        #Working in destination directory now
                        for i in range(len(cuts)):
                            #Slice trees along each pair of cut indices (uniform across trees)
                            #FIXME: generate a filename
                            fname = str(i) + ".root"
                            if i == len(cuts) - 1:
                                cutstring = "%s<=%s" % (cuts[i], evt_str)
                            else:
                                cutstring = "%s<=%s&&%s<%s" % (cuts[i], evt_str, evt_str, cuts[i+1])
                            log.info("Generating %s with %s" % (fname, cutstring))

                            #Initialize vs. write-to file
                            if i_tree == 0:
                                MODE = "RECREATE"
                            else:
                                MODE = "UPDATE"

                            with rootpy.io.root_open(fname, MODE) as t:
                                #Build a copy tree in the context of j.root
                                #FIXME: Get a standardized TreeTemplate for model= kwarg
                                copied = handle.CopyTree(cutstring)

                                #Move the histograms INTO this file once.
                                # if i_tree == 0:
                                #     ROOT.gROOT.SetBatch()
                                #     c = ROOT.TCanvas()
                                #FIXME : we don't really need to copy over hists
                                #We want to write once.
                                if i_tree == 0:
                                    for i, hist in enumerate(all_hists):
                                        hist.Write()
                                #         hist.Draw(cutstring)
                                #         c.Update()
                                #         #print i, hist.GetName()

                                t.write()
                                    #NEED TO GET THE ACTUALLY HISTOGRAM DRAWN IN THE TREE!!!
                                    # hist = this_tree.Draw(histname, selection=cutstring, hist=histname)
                                    # hist = ROOT.gPad.GetPrimitive(histname)
                                    # #current context is fname
                                    # hist.Write()


                                #Add filename upon first successful write
                            if i_tree == 0:
                                fnames.append("%s/%s" % (dest, fname))

    #Return a list of full path/filename
    return fnames

def get_tmp_dir():
    #TODO:
    #Use current path to find location of tmp?
    pwd = os.getcwd()

def split_path(fstr):
    #split the given filepath into (directory, file)
    i = fstr.rfind("/")
    return fstr[:i], fstr[i+1:]

def get_trees(fh):
    #TODO:
    #Passed an active filehandle, put active TTrees into a list

    return

def divide_tree(N_PIPELINES):
    #Take the global tree handle and distribute it into global subtree list
    #Create a total of N_PIPELINES subtrees
    global tree, subtrees

def add_event_branch(filename, path):
    #Passed a root ttree, add event branch
    filepath = "%s/%s" % (path, filename)
    with rootpy.io.root_open(filepath, mode="UPDATE") as fh:
        for i, subtree in enumerate(get_next_tree(fh)):
        # for path, dirs, obj_lst in fh.walk():
        #     for treename in obj_lst:
        #         subtree = fh.Get(treename)
            brname = "event"
            treename = subtree.GetName()
            log.info("Adding branch '%s' to tree %s" % (brname, treename))
            #BUG? for the second tree in this iteration, the create_branches
            #   command gives a 'with the same name' error = implying it sees
            #   a branch by the name of 'event' in the new tree...
            subtree.create_branches({"event": "I"})
            #subtree.Branch(brname, 0)
            #subtree.write()
            #fh.Get(treename).Write(treename, 2)
            #subtree.write()
            #BUG: GetEntries() returns half of the true no. events...
            #   ... or somewhere in the writing process I'm doubling the entries
            N = subtree.GetEntries()

            log.info("Writing %i entries to 'event' branch in %s" % (N, subtree.GetName()))
            # for br in subtree.iterbranchnames():
            #     if br == brname:
            #         print "Found event branch"
            #print "tree has event branch? "+str(subtree.has_branch(brname))

            #These set write status
            #subtree.SetBranchStatus("*",0)
            #subtree.SetBranchStatus(brname, 1)

            #Fill directly into the branch object
            for i in xrange(N):
                subtree.GetEntry(i)
                subtree.event = i
                subtree.GetBranch(brname).Fill()

            fh.Get(treename).Write(treename, 2)
            return

                #subtree.create_branches({brname: 'I'})

                # try:
                #
                # except ValueError:
                #     log.info("Overwriting 'event' branch for tree %s in %s" % (subtree.GetName(), filepath))
                #     subtree.GetListOfBranches().Remove(subtree.GetBranch("event"))
                #     subtree.write(subtree.GetName(), 2)
                #     return
                #     subtree.create_branches({'event': 'I'})


                #PROBLEM: Tree1 has 3M entries but 1.8M entries are getting written to its event branch
                #This corresponds to n_entries in Tree0

                #Tree0 is getting misread as to have an event branch already
                #There is crosstalk in the tree reading systme:
                    #GetEntries() reads from Tree0
                    #GetListOfBrnachs() reads from Tree1
                    #Happens event though these are confirmed to be different trees per iteration

                #Solutions?:
                #   don't fuck with rootpy.io
                #

        return

######################################################################lp
class cd:
    """Context management for directory changes"""
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        #Change to the argument directory
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, typ, val, traceback):
        #Go back to the original directory
        os.chdir(self.saved_path)



#FIXME: Disentegrate this class and make methods act on globals
class RootFileManager:
    """Class for parsing a ROOT file and creating py objects that parallel
    the root structure"""

    def __init__(self, filename):

        self.filename = filename

        #Check for path correctness
        if self.file_exists() == False:
            raise IOError("File not found")

        self.list_of_trees = []
        self.trees_found = False
        return

    def file_exists(self):
        return self.filename in os.listdir(os.getcwd())


    #TODO: More robust; copy over more functionality from dctROOT except cleaner and more modular...
    #TODO: Rewrite using rootpy file.walk() method!
    def get_list_of_trees(self, obj_handle=None):
        #Descend into the ROOT file recursively, picking out the handles of TTrees. Return a list of TTrees

        if self.trees_found:
            return self.list_of_trees

        if obj_handle == None:
            obj_handle = ROOT.TFile.Open(self.filename, "read")

        obj_name = obj_handle.GetName()
        obj_type = type(obj_handle)

        used_names = []
        #Descend into lower directories if necessary
        if obj_type is rootpy.io.file.File:
            for sub in obj_handle.GetListOfKeys():
                #Deal with trees that are named the same
                if sub.GetName() in used_names:
                    new_name = sub.GetName()+"x"
                    sub.SetName(new_name)
                    used_names.append(new_name)
                    sub = obj_handle.Get(new_name)
                else:
                    used_names.append(sub.GetName())
                    sub = obj_handle.Get(sub.GetName())
                self.get_list_of_trees(sub)
        #Grab current tree and exit
        elif obj_type is rootpy.tree.tree.Tree:
            self.list_of_trees.append(obj_handle)
            return
        elif obj_type is hist_type:
            return
        else:
            #"I don't recognize this and I don't know what to do"
            return

        self.trees_found = True
        return self.list_of_trees



######################################################################
class RootIOManager:
    """
    Manage contexts for accessing root files
    """
    #TODO: One file or manyfiles?
    def __init__(self, filename):

        self.filename = filename
        self.file_manager = RootFileManager(filename)

        self.list_of_trees = self.file_manager.get_list_of_trees()


    def __enter__(self):
        self.open_file = ROOT.TFile.Open(self.filename, "read")
        return self.open_file

    def __exit__(self, exception_type, exception_val, trace):
        #self.open_file.Write()
        self.open_file.Close()


#A conversion dictionary for the VALUE_YOU_NEED: branch_to_access
lookup_dct = {
            "MC_N_PART": "mc_nFSPart",
            "MC_PART_XYZ_PREFIX": "mc_FSPartP",
            "MC_PART_E": "mc_FSPartE",
            "MC_PART_ID": "mc_FSPartPDG",
            "MC_INCOMING_PART": "mc_incoming",
            "MC_INCOMING_ENERGY": "mc_incomingE",
            "MC_VTX":  "mc_vtx",
            "MC_TYPE": "mc_intType",

            "DATA_PART_XYZ_PREFIX": None,
            "DATA_PART_E": None,
            "DATA_PART_ID": None,
            "DATA_INCOMING_PART": None,
            "DATA_BLOB_PREFIX": "CCQEAntiNuTool_isoblob",

            "RECON_VTX": "CCQEAntiNuTool_vtx",
            "RECON_MU_P_PREFIX": "CCQEAntiNuTool_",
            "EVENT_BR": "event"
            }

#Ordered list of ROOT file-type
#Index is used in function calls with datatype-specific leafnames
datatype_lst = ["MC", "DATA", "RECON"]

#Update the lookup_dct
#TODO:
def update_lookup_dct():
    return

def expand_prefix(br_name):
    #Passed a branchname prefix string, return a list
    #of the expanded branches
    if br_name == "CCQEAntiNuTool_isoblob":
        suffs = ["E", "X", "Y", "Z"]
    elif br_name == "mc_FSPartP":
        suffs = ["x", "y", "z"]
    else:
        raise ValueError("Branch prefix %s not recognized" % br_name)
    return [br_name+suffix for suffix in suffs]

def is_prefix_br(br_name):
    #passed a branch name string, use lookup_dct to determine
    #if its a prefix-name

    for k, v in lookup_dct.iteritems():
        if v == None:
            continue
        #cover the prefix branchname case
        if v in br_name:
            #the br_name is either the expanded prefix or the prefix
            return "_PREFIX" in k and v == br_name
    raise ValueError("Branch  %s not recognized" % br_name)

#Set up wrappers for implementing functions specific to a version of a tree
#BASE Particle utilities must take the names of the branches they're
#searching as args
def versioncontrol(func):
    #Replace function default values with their matching value in the lookup dict
    def substitute_and_call(*args, **kwargs):
        substitute = []
        for key in func.func_defaults:
            if key in lookup_dct:
                substitute.append(lookup_dct[key])
            else:
                substitute.append(key)
        func.func_defaults = tuple(substitute)
        return func(*args, **kwargs)

    return substitute_and_call



if __name__ == "__main__":
    pass
