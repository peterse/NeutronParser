"""
IO.py - supports I/O for parsing rootfiles, particularly naming
conventions for finding specific values in the tree
"""

import rootpy.ROOT as ROOT
import rootpy
import maketestfiles as testfile
#import ROOT
import os
#FIXME: Why can't I import exceptions??

######################################################################

# # # # GLOBAL OBJECTS # # # # #
#File managers for testing parallel returns
global_f = None #IO filehandle
tree = None # tree handle
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

            "DATA_PART_XYZ_PREFIX": "derp2",
            "DATA_PART_E": "derp",
            "DATA_PART_ID": None,
            "DATA_INCOMING_PART": None,


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
