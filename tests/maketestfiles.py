import rootpy.ROOT as ROOT
import random

#Using rootpy for tree construction
from rootpy.tree import Tree
from rootpy.io import root_open
#Local python arrays for ROOT-like pointers
from array import array

"""Module of methods for creating different rootfiles in the current directory"""

#filenames to  be used cross-library
MC_filename = "MC_dummy.root"
DATA_filename = "DATA_dummy.root"
treename = "test"
#testfile-specific attributes
filesize = 100000

#Postcondition: MC_dummy.root will be recreated
#kwargs:
#   lightweight - if True, only 'event' will be filled in the primary tree
def generate_MC(lightweight=False):
    #Recreate the MC testfile
    print "Generating file %s" % MC_filename
    f = root_open(MC_filename, "recreate")
    tree = Tree(treename)

    #Branches are customized objects based on dct keys
    tree.create_branches({
                            "mc_FSPartPx": "F",
                            "mc_FSPartPy": "F",
                            "mc_FSPartPz": "F",
                            "mc_FSPartE": "F",
                            "event": "I",
                            "mc_nFSPart": "I",
                            "mc_FSPartPDG": "I"
                            })

    for j in xrange(filesize):
        tree.event = j
        tree.mc_nFSPart = 1 #For event checking
        if lightweight:
            tree.fill()
            continue

        #simulate momenta, energies
        p = [random.gauss(0., 1.) for i in range(4)]
        tree.mc_FSPartPx = p[0]
        tree.mc_FSPartPy = p[1]
        tree.mc_FSPartPz = p[2]
        tree.mc_FSPartE = p[3]
        tree.mc_FSPartPDG = 2112        #neutron
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
