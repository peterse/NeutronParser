import rootpy.ROOT as ROOT
import random

#Using rootpy for tree construction
from rootpy.tree import Tree
from rootpy.io import root_open
#Local python arrays for ROOT-like pointers
from array import array
#mode for generating - mc? data? other?
MODE = "MC"
N_entries = 10000

#Initialize root file
#rf = ROOT.TFile.Open('dummy.root','RECREATE')
#Declare an ntuple with position, momentum
if MODE == "MC":
    #
    # tree = ROOT.TTree("tree1", "tree1")
    #
    # #Python arrays to be manipulated during filling
    # px = array( 'f', N_entries*[ 0. ] )
    # py = array( 'f', N_entries*[ 0. ] )
    # pz = array( 'f', N_entries*[ 0. ] )
    # E = array( 'f', N_entries*[ 0. ] )
    # #Initialize arrays for reading into the RootFile
    # #These are keeping references to their respective arrays
    # tree.Branch("mc_FSPartPx", px, "px")
    # tree.Branch("mc_FSPartPy", py, "py")
    # tree.Branch("mc_FSPartPz", pz, "pz")
    # tree.Branch("mc_FSPartE", E, "E")
    #Fill arrays with random values

    # for i in xrange(N_entries):
    #     p = [random.gauss(-1., 1.) for i in range(4)]
    #     px[i] = p[0]
    #     py[i] = p[1]
    #     pz[i] = p[2]
    #     E[i] = p[3]

    f = root_open("MC_dummy.root", "recreate")

    tree = Tree("test")
    tree.create_branches({
                            "mc_FSPartPx": "F",
                            "mc_FSPartPy": "F",
                            "mc_FSPartPz": "F",
                            "mc_FSPartE": "F",
                            "event": "I"
                            })

    for j in xrange(N_entries):
        p = [random.gauss(-1., 1.) for i in range(4)]
        #pyroot automatically generates members whose names
        #correspond to the branch names!
        tree.mc_FSPartPx = p[0]
        tree.mc_FSPartPy = p[1]
        tree.mc_FSPartPz = p[2]
        tree.mc_FSPartE = p[3]
        tree.event = j
        tree.fill()
    tree.write()
    f.close()

    #ntuple_py = ROOT.TNtuple("mc_FSPartPy", "mc_FSPartPy", "py")
    #ntuple_pz = ROOT.TNtuple("mc_FSPartPx", "mc_FSPartPz", "pz")
    #ntuple_E = ROOT.TNtuple("mc_FSPartE", "mc_FSPartE", "E")
else:
    print "mode not supported"

# #Fill the branch with some random values centered at 0
# for i in xrange(10000):
#     p = [random.gauss(-1., 1.) for i in range(4)]
#     ntuple_px.Fill(p[0])
#     ntuple_py.Fill(p[1])
#     ntuple_pz.Fill(p[2])
#     ntuple_E.Fill(p[3])

#Write and closeout
#rf.Write()
#rf.Close()

#For IO-testing
IOtest = ROOT.TFile.Open("IOtest.root",'RECREATE')
#write some garbagde test trees
testtree1 = ROOT.TTree("testtree1", "testtree1")
testtree2 = ROOT.TTree("testtree2", "testtree2")
IOtest.Write()
IOtest.Close()
