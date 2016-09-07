import ROOT
import random

#Initialize root file
rf = ROOT.TFile.Open('dummy.root','RECREATE')
#Declare an ntuple with position, momentum
ntuple = ROOT.TNtuple("branch_1", "branch_1", "x:y:z:vx:vy:vz")

#Fill the branch with some random values centered at 0
for i in xrange(10000):
    p = [random.gauss(0., 1.) for i in range(6)]
    ntuple.Fill(p[0], p[1], p[2], p[3], p[4], p[5])

#Write and closeout
rf.Write()
rf.Close()
