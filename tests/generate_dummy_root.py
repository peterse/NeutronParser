import ROOT
import random

#Local python arrays for ROOT-like pointers
from array import array
#mode for generating - mc? data? other?
MODE = "MC"

#Initialize root file
rf = ROOT.TFile.Open('dummy.root','RECREATE')
#Declare an ntuple with position, momentum
if MODE == "MC":

    N_entries = 10000
    tree = ROOT.TTree("tree1", "tree1")

    #Python arrays to be manipulated during filling
    px = array( 'f', N_entries*[ 0. ] )
    py = array( 'f', N_entries*[ 0. ] )
    pz = array( 'f', N_entries*[ 0. ] )
    E = array( 'f', N_entries*[ 0. ] )
    #Initialize arrays for reading into the RootFile
    #These are keeping references to their respective arrays
    tree.Branch("mc_FSPartPx", px, "px")
    tree.Branch("mc_FSPartPy", py, "py")
    tree.Branch("mc_FSPartPz", pz, "pz")
    tree.Branch("mc_FSPartE", E, "E")

    #Fill arrays with random values
    for i in xrange(N_entries):
        p = [random.gauss(-1., 1.) for i in range(4)]
        px[i] = p[0]
        py[i] = p[1]
        pz[i] = p[2]
        E[i] = p[3]

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
rf.Write()
rf.Close()

#For IO-testing
IOtest = ROOT.TFile.Open("IOtest.root",'RECREATE')
#write some garbagde test trees
testtree1 = ROOT.TTree("testtree1", "testtree1")
testtree2 = ROOT.TTree("testtree2", "testtree2")
IOtest.Write()
IOtest.Close()
