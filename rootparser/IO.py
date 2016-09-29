"""
IO.py - supports I/O for parsing rootfiles, particularly naming
conventions for finding specific values in the tree
"""

import rootpy.ROOT as ROOT
import rootpy
from rootparser_exceptions import log

#import ROOT
import os
import sys
import math
#Debugging
sys.path.append("/home/epeters/NeutronParser/tests")
import maketestfiles as testfile
#FIXME: Why can't I import exceptions??

######################################################################

# # # # GLOBAL OBJECTS # # # # #
#File managers for testing parallel returns
global_f = None #IO filehandle
tree = None # tree handle
subtrees = []
dummyIO = None #IO file wrapper objecct



######################################################################

#FIXME: temporary home for testfile
def recreate_testfile():
    #Recreate the testfile and reassign global handles
    global dummyIO, tree, global_f
    testfile.generate_MC()
    dummyIO = RootIOManager(testfile.MC_filename)
    #grab the test-tree
    tree = dummyIO.list_of_trees[0]
    tree.GetEvent()
    return





def get_subtree(arg):
    #When a process asks for a tree, give it one through this method
    global tree, subtrees
    #TODO: How will we distribute subtrees among preocesses?

    #Do things with sub-trees
    if tree:
        return tree
    else:
        raise IOError("I/O tree was not generated")


######################################################################
#Sub-Tree splitting:

def path_exists(path):
    #passed a path to a rootfile and the filename, check that both are valid
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
    if N > T:
        #Special case: Return a valid list of fewer entries than requested...
        N = T
    rem = T % N
    dn = int(math.floor(T) / N)         #distance between each cut
    out = [ i*dn for i in range(N ) ]
    return out

def split_file(src, N, path=None, dest=None):
    #Split the main TTree of a Rootfile and distribute it into N different files
    #Populates the global list 'subtrees' with handles of smaller tree types
    #Input: path, src: where we're splitting from
    #       dest, target: where the result is written
    #       N - the number of 'subtrees' we want == (N_cuts + 1)
    #Return: list of 'path/filename' for N files created
    global subtrees, tree

    #Assume we're in the current directory
    if path == None:
        path = os.getcwd()
    if dest == None:
        dest = os.getcwd()

    #Make the temporary file in temp
    tmp = get_tmp_dir()



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



    #Parse the current rootfile and divide its trees up
    with rootpy.io.root_open(src) as s:
        fnames = []
        for path, dirs, obj_lst in s.walk():
            for name in obj_lst:
                handle = s.Get(name)
                if type(handle) is rootpy.tree.tree.Tree:
                    #Where to make our cuts and on which branch
                    cuts = make_cuts_lst(handle.GetEntries(), N)
                    evt_str = get_event_branch(handle)
                    with cd(dest):
                        #Working in destination directory now
                        for i in range(len(cuts)):
                            #FIXME: generate a filename
                            fname = str(i) + ".root"
                            if i == len(cuts) - 1:
                                cutstring = "%s<=%s" % (cuts[i], evt_str)
                            else:
                                cutstring = "%s<=%s&&%s<%s" % (cuts[i], evt_str, evt_str, cuts[i+1])
                            log.debug("Generating %s with %s" % (fname, cutstring))
                            with rootpy.io.root_open(fname, "recreate") as t:
                                #Build a copy tree in the context of j.root
                                #FIXME: Get a standardized TreeTemplate for model= kwarg
                                copied = handle.CopyTree(cutstring)
                                t.write()
                                #Add filename upon successful write
                                fnames.append("%s/%s" % (dest, fname))
    #Return a list of full filenames/paths
    return fnames

def get_tmp_dir():
    #TODO:
    #Use current path to find location of tmp?
    pwd = os.getcwd()

def get_trees(fh):
    #TODO:
    #Passed an active filehandle, put active TTrees into a list

    return

def divide_tree(N_PIPELINES):
    #Take the global tree handle and distribute it into global subtree list
    #Create a total of N_PIPELINES subtrees
    global tree, subtrees


######################################################################
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

######################################################################

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

        #keep track of repeated names
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

            "DATA_PART_XYZ_PREFIX": "derp2",
            "DATA_PART_E": "derp",
            "DATA_PART_ID": None,
            "DATA_INCOMING_PART": None,

            "RECON_VTX": "CCQEAntiNuTool_vtx"
            }

#Ordered list of ROOT file-type
#Index is used in function calls with datatype-specific leafnames
datatype_lst = ["MC", "DATA", "RECON"]

#Update the lookup_dct
#TODO:
def update_lookup_dct():
    return

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
