import rootpy.ROOT as ROOT
import random

#Using rootpy for tree construction
from rootpy.tree import Tree, TreeModel, FloatArrayCol
from rootpy.io import root_open
from rootpy import stl #std library?

from rootpy.tree.treetypes import Array     #custom branching
from rootpy.tree.treebuffer import TreeBuffer
import re       #regex compile, functions
#Local python arrays for ROOT-like pointers
from array import array

import os
import IO
import shutil   #rmtree


"""Module of methods for creating different rootfiles in the current directory"""

#filenames to  be used cross-library
MC_filename = "MC_dummy.root"
DATA_filename = "DATA_dummy.root"
treename = "test"
treename2 = "test2"
TMP = os.getcwd() + "/tmp"
#testfile-specific attributes
filesize = 100000
n_trees = 2
#Postcondition: MC_dummy.root will be recreated
#kwargs:
#   lightweight - if True, only 'event' will be filled in the primary tree


######################################################################
#A template tree object to allow vectors
class TreeTemplate(TreeModel):
    """A template for constructing special-object TTrees"""
    #Specify branches of special types ahead of time
    mc_vtx = FloatArrayCol(4)


######################################################################

#FIXME: temporary home for testfile
def recreate_testfile():
    #Recreate the testfile and reassign global handles
    global dummyIO, tree, global_f
    generate_MC()
    dummyIO = IO.RootIOManager(MC_filename)
    #grab the test-tree
    tree = dummyIO.list_of_trees[0]
    tree.GetEvent()
    #flush the tmp folder
    #shutil.rmtree(TMP)
    #os.mkdir(TMP)
    return

def generate_MC(lightweight=False):
    #Recreate the MC testfile

    print "Generating file %s" % MC_filename
    f = root_open(MC_filename, "recreate")




    tree = Tree(treename, model=TreeTemplate)
    #tree = Tree(treename)
    #Branches are customized objects based on dct keys
    tree.create_branches({
                            "mc_FSPartPx": "F",
                            "mc_FSPartPy": "F",
                            "mc_FSPartPz": "F",
                            "mc_FSPartE": "F",
                            "event": "I",
                            "mc_nFSPart": "I",
                            "mc_FSPartPDG": "I",
                            "mc_incoming": "I",
                            "mc_incomingE": "F",
                            })
    #Custom branching: Hand-make a treebuffer and feed its special types into tree
    # print "Testing:"
    # r =  re.compile(TreeBuffer.ARRAY_PATTERN)
    # print r.pattern
    # Array()
    # my_branches = {"mc_vtx": "TVector3"}
    # print dict(my_branches)
    # arraybuffer = TreeBuffer( branches= my_branches)
    # tree.create_branches(TreeBuffer)



    for j in xrange(filesize):
        tree.event = j
        tree.mc_nFSPart = 1 #For event checking
        if lightweight:
            tree.fill()
            continue

        #simulate momenta, energies
        p = [random.gauss(0., 1.) for i in range(5)]
        vtx = [random.gauss(0., 10.) for i in range(4)]

        tree.mc_FSPartPx = p[0]
        tree.mc_FSPartPy = p[1]
        tree.mc_FSPartPz = p[2]
        tree.mc_FSPartE = p[3]
        tree.mc_FSPartPDG = 2112        #neutron

        tree.mc_incoming = -13          #neutrino
        tree.mc_incomingE = p[4]        #neutrino energy

        #vtx
        tree.mc_vtx.clear()
        for i, vtx_dim in enumerate(vtx):
            tree.mc_vtx[i] = vtx_dim
        tree.fill()

    tree.write()

    #second tree for testing tree parsing
    tree2 = Tree(treename2, model=TreeTemplate)
    tree2.create_branches({
                            "event": "I"
                            })
    tree2.write()

    f.close()



if __name__ == "__main__":
    #mode for generating - mc? data? other?
    MODE = "MC"

    #Initialize root file
    #rf = ROOT.TFile.Open('dummy.root','RECREATE')
    #Declare an ntuple with position, momentum
    if MODE == "MC":
        generate()
    else:
        print "mode not supported"
