import rootpy.ROOT as ROOT
import random

#Using rootpy for tree construction
from rootpy.tree import Tree, TreeModel
from rootpy.io import root_open
from rootpy import stl #std library?
#Local python arrays for ROOT-like pointers
from array import array

"""Module of methods for creating different rootfiles in the current directory"""

#filenames to  be used cross-library
MC_filename = "MC_dummy.root"
DATA_filename = "DATA_dummy.root"
treename = "test"
#testfile-specific attributes
filesize = 10000

#Postcondition: MC_dummy.root will be recreated
#kwargs:
#   lightweight - if True, only 'event' will be filled in the primary tree



def generate_MC(lightweight=False):
    #Recreate the MC testfile
    print "Generating file %s" % MC_filename
    f = root_open(MC_filename, "recreate")

    #A template tree object to allow
    class TreeTemplate(TreeModel):

        #Specify branches of special types ahead of time
        mc_vtx = stl.vector(float)



    tree = Tree(treename, model=TreeTemplate)

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

    for j in xrange(filesize):
        tree.event = j
        tree.mc_nFSPart = 1 #For event checking
        if lightweight:
            tree.fill()
            continue

        #simulate momenta, energies
        p = [random.gauss(0., 1.) for i in range(5)]
        vtx = [random.gauss(0., 10.) for i in range(3)]

        tree.mc_FSPartPx = p[0]
        tree.mc_FSPartPy = p[1]
        tree.mc_FSPartPz = p[2]
        tree.mc_FSPartE = p[3]
        tree.mc_FSPartPDG = 2112        #neutron

        tree.mc_incoming = -13          #neutrino
        tree.mc_incomingE = p[4]        #neutrino energy

        #vtx
        tree.mc_vtx.clear()
        for vtx_dim in vtx:
            tree.mc_vtx.push_back(vtx_dim)

        tree.fill()

    tree.write()
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
