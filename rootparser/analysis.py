"""analysis.py - non-OO event analysis"""


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
import scipy

#evts and filters
import event
import filters as fi

#Debugging
sys.path.append("/home/epeters/NeutronParser/tests")
import maketestfiles as testfile
from parallel import ThreadManager
from multiprocessing import Pool

import inspect
#logging
from rootparser_exceptions import log

#Using templates for branchnames, create the list to filter
#which branches we extract into the NP array
def make_filter_list(datatype):
    if datatype == 0:
        return make_filter_list_mc()
@versioncontrol
def make_filter_list_mc(
                    xyz_prefix="MC_PART_XYZ_PREFIX", energy="MC_PART_E"):
    return

def convert2np(TTree):
    #use root_numpy conversion
    #are vectors supported?
    arr = rnp.root2array(TTree)
    return arr

class EventSummary:
    """A stand in for an event description; has necessary evt attributes to
    apply filters before histogramming"""
    def __init__(self, index, datatype=0):
        #Instance attributes
        self.index = index         #event number
        self.datatype = datatype

        self.P = [0, 0, 0, 0]       #Total event momentum
        #Event filling:
        #   1) discover the number of particles
        #   2) iterate over particles creating 'Particle' objects
        #self.n_parts = self.fetch_n_parts()

        #neutron blob comparison
        self.n_parts = 0
        self.n_neutrons = 0
        self.n_blobs = 0
        self.n_protons = 0

        #neutrons in this event
        self.lookup_dct = {}

        #angle comparisons
        self.mu_dot_n_T = None

        self.rvb = None
        #Post-Filter
        self.final_E_n = None       #Final neutron/blob energy

    def __str__(self):
        #A representation of this event; dump particles?
        index = "Event %s" % str(self.index)
        parts = "Neutrons: \n  %s" % "\n  ".join([str(k)+":"+str(v) for k,v in self.lookup_dct.iteritems()])
        return "\n".join([index, parts, " "])
        #return str(self.particle_lst)




def testDuplicateAccess(filename, path, report=True):
    """
    Passed a root filename, attempt to discover duplicate trees
    Warning! This will edit the names of trees in the file
    """

    filepath = "%s/%s" % (path, filename)

    #1 - Check if duplicates exist
    #BUG: cannot use rootpy interface - doesn't read TKeys
    used_names = []
    duplicate = False
    with rootpy.io.root_open(filepath, "read") as fh:
        for sub in fh.GetListOfKeys():
            name = sub.GetName()
            #I have to assume TKeys and TTrees share the name for now
            if name not in used_names:
                used_names.append(name)
            else:
                duplicate = True
    if duplicate == False:
        log.info("No duplicated detected - file %s good.", filepath)
        return

    #2 - if we find a duplicate, tear the whole thing down.
    with rootpy.io.root_open(filepath, "UPDATE") as fh:
        #BUG: rootpy couldn't see the duplicate tree objects like this...
        # for path, dirs, obj_lst in fh.walk():

        i = 0          #indexing name
        for sub in fh.GetListOfKeys():
            current_name = "Tree%i" % i
            old_name = sub.ReadObj().GetName()
            log.info("Changing tree '%s' to '%s'" % (old_name, current_name))
            #fh.Get(old_name).Write(current_name)
            sub.SetName(current_name)
            fh.Get(old_name).SetName(current_name)
            #fh.Write(filename, 2) #opt=2 - OVERWRITE mode to kill previous 'cycles' of TTrees
            #sub.ReadObj().SetName(current_name)
            #fh.Get(old_name).Write(current_name)
            #fh.Delete(old_name)
            #fh.Write()
            i+=1

    with rootpy.io.root_open(filepath, "UPDATE") as fh:
        for path, dirs, obj_lst in fh.walk():
            for name in obj_lst:
                #currently both required
                fh.Get(name).SetName(name)  #Changing the tree name
                fh.Get(name).Write(name, ROOT.TObject.kOverwrite)    #Changing the structure name
                    #opt=2 - OVERWRITE mode to kill previous
                #fh.Delete(name+";")
                #fh.Delete(name)
    #
    # with rootpy.io.root_open(filepath, "read") as fh:
    #     for path, dirs, obj_lst in fh.walk():
    #         for name in obj_lst:
    #             print "object name: ", name
    #             print "structure name: ", fh.Get(name).GetName()
            # #Deal with trees that are named the same
            # if treename in used_names:
            #     new_name = treename+"x"
            #     log.warning("Modifying treename %s -> %s in %s" %\
            #                 (treename, new_name, filename) )
            #     #sub.SetName(new_name)
            #     s1.Delete(treename)
            #     used_names.append(new_name)
            # else:
            #     used_names.append(treename)
    return

def testEventAccess(filename, path, report=True):
    #Passed a root filename, attempt to call all functions
    #Return a report (object?) on the accessible features
    #Called from main thread.
    missing_br = []

    filepath = "%s/%s" % (path, filename)
    with rootpy.io.root_open(filepath) as fh:
        log.info("Checking trees in %s" % filename)
        for subtree in IO.get_next_tree(fh):
            log.info("  Checking branches in tree '%s'" % subtree.GetName())
            subtree.GetEvent(0)
            #IO.put_subtree(pid, subtree)
            for k, br_name in IO.lookup_dct.iteritems():
                #'None' is a work in progress
                if br_name is None:
                    continue

                #Prefix branches are iterated over, special treatment
                if k == "DATA_BLOB_PREFIX":
                    for suffix in ["X_sz", "Y_sz", "Z_sz", "E", "X", "Y", "Z"]:
                        try:
                            subtree.GetLeaf(br_name + suffix).GetValue()
                        except ReferenceError:
                            missing_br.append(br_name + suffix)
                elif k == "MC_PART_XYZ_PREFIX":
                    for suffix in ["x", "y", "z"]:
                        try:
                            subtree.GetLeaf(br_name + suffix).GetValue()
                        except ReferenceError:
                            missing_br.append(br_name + suffix)
                #TODO: do we want to check vector-filled leafs?
                elif k == "RECON_MU_P_PREFIX":
                    for suffix in ["px_mu", "py_mu", "pz_mu", "E_mu"]:
                        try:
                            subtree.GetLeaf(br_name + suffix).GetValue()
                        except ReferenceError:
                            missing_br.append(br_name + suffix)
                else:
                    try:
                        subtree.GetLeaf(br_name).GetValue()
                    except ReferenceError:
                        missing_br.append(br_name)
            #'Event' branch
            try:
                subtree.GetLeaf("event").GetValue()
            except ReferenceError:
                missing_br.append("event")

            if report and any(missing_br):
                print "Tree %s missing branches:" % subtree.GetName()
                for br in missing_br:
                    print "   ", br

    # return a list of missingbranches
    return missing_br






def ParseEventsNP(tupl, hist=True, filt=True, dump=True, ML=True):
    """
    Using an input filename
    Return:
      The input tuple - this will be parsed to grab the target histograms
    Args:
    tupl components
      [0] filename is the file being analyzed
      [1] path is its location
      [2] target is the desired output filename
      [3] dest is its location

    KWArgs:
      filt:
      dump:
      hist:
      ML:
    """
    pid = os.getpid()

    filename, path = tupl[0], tupl[1]
    target, dest, tmp = tupl[2], tupl[3], tupl[4]
    filepath = "%s/%s" % (path, filename)
    log.info("PID %s parsing %s" % (pid, filepath))

    if hist:
        hist_target = "%s/%s" % (dest, target)
        #Initialize histograms
        export_lst = hi.extend_export_lst(hi.all_export_lst)
        subhist_dct = hi.init_hist_dct(export_lst)
        IO.put_subhist(subhist_dct)

    #Set up a dct that can become a simple column/array dataframe
    #Contains tags, classifications
    #TODO: Move this to learn
    if ML:
        ML_out = {
                "event": [],          #!!!RELATIVE event number
                "blob_good": [],      #bool: was the blob a 'good' fit?
                "CCQE": [],           #bool: was this event CCQE?
                "dphiXY": [],         #float: angle was off?
                "dthetaXZ": [],       #float: angle was off?
                "dthetaYZ": [],       #float: angle was off?
                "blob_dX": [],
                "blob_dY": [],
                "blob_dZ": [],
                "blob_dE": []        #float: was the energy off?

        }

    #Parse input files
    with rootpy.io.root_open(filepath) as fh:
        for subtree in IO.get_next_tree(fh):
            #pass the tree to the global space for access by funcs
            IO.put_subtree(pid, subtree)
            N_events = subtree.GetEntries()
            if ML:
                #A list of categories for classification/regression
                #Default to "False"
                category_lst = [0 for n in range(N_events) ]
            #convert our subtree into an np array
            #TODO:
            datatype = 0
            filterlst = make_filter_list(datatype)
            #Iterate over the event and get necessary components
            for e_i in xrange(N_events):
                IO.get_subtree().GetEvent(e_i)

                #DEBUG:

                if e_i % 10000 == 0:
                    log.info("  (%s:) Processing event %i" % (pid, e_i))

                #PARTICLES
                particle_lst = get_particle_lst(e_i, datatype)
                # for p in particle_lst:
                #     print p.name, p.P

                #MUON
                mu = fetch_mu(particle_lst)
                if mu is None:
                    continue    #FIXME: we need statistics - apply filter!
                mc_mu_P = mu.P
                recon_mu_P = get_mu_data(e_i)

                #MC NEUTRON
                mc_neutrons = fetch_neutrons_mc(particle_lst)
                n_neutrons = len(mc_neutrons)
                if n_neutrons == 1:
                    mc_n_P = mc_neutrons[0].P
                    #FIXME:
                    #Case for neutron at rest...
                    if mc_n_P[0] < Mm.m_n + 5:
                        continue

                #Case for n_neutrons != 1, or no free neutron:
                else:
                    continue        #FIXME: apply filter!

                """
                Neutron notes from Tejin:
                - blob is >100mm from muon track
                - vtx: is fiducial, is tracker region
                - muon: Single mu+

                -Measure theta_c -> angle of neutron blob below plane of ???
                    -HEIDI: What is that coordinate system in Tejin pg. 16/

                """

                #KINE-NEUTRONS
                try:
                    mc_kine_n_P = make_kine_neutron(mc_mu_P)
                except ValueError:
                    #log.warning("MakeKineNeutron: Negative Neutron Energy calculated.")
                    mc_kine_n_P = None

                try:
                    recon_kine_n_P = make_kine_neutron(recon_mu_P)
                except ValueError:
                    #log.warning("MakeKineNeutron: Negative Neutron Energy calculated.")
                    recon_kine_n_P = None

                if mc_kine_n_P is None or recon_kine_n_P is None:
                    continue

                #VERTEX
                mc_vtx = get_vtx(e_i, datatype=0)
                recon_vtx = get_vtx(e_i, datatype=2)
                if True:
                    #FIXME: condition for acceptable vertex discrepancy...
                    #FIXME: Not working right now- weirdness w TLorentzVector?
                    #FIXME: recon vtx wasn't showing up
                    vtx = mc_vtx

                if not vtx:
                    continue

                #BLOBS
                #FIXME: before or after neutron rotation?
                blobs = make_blob_neutrons(e_i, datatype=2)
                n_blobs = len(blobs)
                if n_blobs == 0:
                    #NO BLOB
                    continue
                blob = pick_blob(blobs, vtx, mc_n_P, option="dangle")


                # CONVERSIONS, ROTATIONS
                mc_kine_n_P = Mm.convert_E2T(mc_kine_n_P, Mm.m_n)
                recon_kine_n_P = Mm.convert_E2T(recon_kine_n_P, Mm.m_n)
                mc_n_P = Mm.convert_E2T(mc_n_P, Mm.m_n)
                RVB = make_rvb(blob, vtx)

                #rotations on mc parts
                mc_kine_n_P = Mm.yz_rotation(mc_kine_n_P, datatype=0)
                mc_n_P = Mm.yz_rotation(mc_n_P, datatype=0)
                mc_mu_P = Mm.yz_rotation(mc_mu_P, datatype=0)

                #phiT on data muon vs. neutron blbo
                phiT_blob = Mm.calculate_phi_T(recon_mu_P[1:], RVB[1:],1)

                #FIXME: Do we rotate the kine or make it using rotated mc?



                #EVENT SUMMARY
                evt = EventSummary(e_i, datatype)
                evt.n_parts = 0
                evt.n_neutrons = n_neutrons
                evt.n_blobs = n_blobs
                evt.n_protons = count_protons(particle_lst)
                evt.phiT = phiT_blob    #blob vs recon muon
                #mc-specific metadata
                if datatype == 0:
                    evt.int_type = get_mc_int_type(e_i)

                #neutrons in this event
                #TODO: PROTECT THESE KEYNAMES!!!
                evt.dct = {
                                    "recon_kine_n_P": recon_kine_n_P,
                                    "mc_kine_n_P": mc_kine_n_P,
                                    "mc_n_P": mc_n_P,
                                    "n_blob": RVB,
                                    "mc_mu": mc_mu_P,
                                    "data_mu": recon_mu_P
                             }

                #FILTERS

                if not fi.AntiQE_like_event(evt):
                    #log.info("Event %i not CCQE-like" % e_i )
                    continue

                # if not fi.phiT_good(evt):
                #     continue
                #print DEBUG

                # log.info("Event %i particles:\n" % e_i)
                # print "VTX", vtx
                # print "BLOB", blob[1:]
                # print "RVB: ", RVB[1:]
                # print "DTHETA", Mm.compare_vecs(blob[1:], RVB[1:])
                # print "MUON: ", mc_mu_P[1:]
                # print "MC NEUTRON: ", mc_n_P[1:], "\n\n"

                #HISTOGRAMMING
                #Calculations are made in histogram library for locality
                if hist:

                    hi.make_comp_hists(evt.dct)      #N-COMPARISONS
                    hi.make_neutron_hists(evt.dct)   #INDIVIDUAL NEUTRONS

                    #DATA QUALITY

                    #Measure angular distribution
                    for mu in hi.MUONS:
                        mu_P = evt.dct.get(mu)
                        hi.make_vec_angle_hists(mu, mu_P)

                    for n in hi.NEUTRONS:
                        n_P = evt.dct.get(n)
                        if n_P is None:
                            continue
                        hi.make_vec_angle_hists(n, n_P)

                    #Measure transverse angle separation between particles

                    for pair in hi.ANGLE_PAIRS:
                        parts = [evt.dct.get(name) for name in pair]
                        #Transverse angular separation (phi_T)
                        phi_XY = hi.make_Dphi_hist(pair[0], pair[1], parts[0], parts[1])
                        #ThetaX, ThetaY separation
                        theta_XZ, theta_YZ = hi.make_Dtheta_hists(pair[0], pair[1], parts[0], parts[1])

                        #Keep blob stats
                        if ML and pair == ("n_blob", "mc_n_P"):
                            ML_out.get("dphiXY").append(phi_XY)
                            ML_out.get("dthetaXZ").append(theta_XZ)
                            ML_out.get("dthetaYZ").append(theta_YZ)




                #Checking relative angles

                #MC kine-neutron vs. SINGLE mc neutron
                dangle, separation = Mm.compare_vecs(mc_n_P[1:], mc_kine_n_P[1:])
                dblob = mc_n_P - RVB
                blob_good = False
                #ML training set
                if ML:
                    ML_out.get("event").append(e_i)
                    ML_out.get("CCQE").append(True)
                    ML_out.get("blob_good").append(blob_good)
                    ML_out.get("blob_dE").append(dblob[0])
                    ML_out.get("blob_dX").append(dblob[1])
                    ML_out.get("blob_dY").append(dblob[2])
                    ML_out.get("blob_dZ").append(dblob[3])
                    # ML_out.get("mc_n_i").append(mc_neutrons[0].index)
                    # ML_out.get("mu_i").append(mu.index)
                    #Pass along our selected neutrons
                    for k_n, vec in evt.lookup_dct.iteritems():
                        ML_out[k_n] = vec

                continue


                #TODO: IF this is a good kine event,
                if True:
                    category_lst[e_i] = 1
                else:
                    continue


            #FIXME
            #only iterate first tree?
            break

        if hist:
            #Write out histograms
            hi.write_hists(hist_target)
        if ML:
            #Output a dictionary of good events with classifiers
            return IO.dump_obj(ML_out, IO.picklename(filename), tmp )
        #FIXME: Different return objects is bad...
        else:
            return filepath


def make_rvb(blob, vtx):
    #Passed a blob and the vtx position, make the vtx->blob vector
    #First entry will be blob energy

    #blob has format [E,x, y, z]
    #vtx has format [x, y, z, t]
    rvb = [blob[0],0,0,0]
    for i in range(len(rvb)):
        if i == 0:
            continue
        rvb[i] = blob[i] - vtx[i-1]

    return np.array(rvb)



@versioncontrol
def get_mc_int_type(e_i, typ="MC_TYPE"):
    #MC datatype indicates what ccque event type was run in the interaction
    return int(IO.get_subtree().GetLeaf(typ).GetValue())

def make_kine_neutron(P_mu):
    #passed an event, generate an MC and recon neutron, if possible
    return Mm.make_neutron_P(P_mu)

def pick_blob(blobs_lst, vtx, neutron, option="dangle"):
    """
    Passed a list of blobs detected, choose the best based
    on criteria specified by 'option'
    Args:
        -blobs_lst: A list of blob 4-vectors [E,X,Y,Z]
        -vtx: vtx position (x,y,z,t)
        -neutron: comparison neutron (E, px, py, pz)
    kwargs:
        -option:
            'dangle' - calculate the RVB for each blob, then
            pick the blob that has the smallest dangle vs neutron.
            'distance' - ...that has the smallest separation
    """

    if option in ["dangle", "distance"]:
        if option == "dangle":
            best = 180
            spot = 0
        elif option == "distance":
            best = 9999
            spot = 1
            #out, temp = None

        for i, blob in enumerate(blobs_lst):
            #FIXME: Is there a simpler, single-step solution
            rvb = make_rvb(blob, vtx)
            temp = Mm.compare_vecs(rvb[1:], neutron[1:])[spot]
            #keep this blob, its rvb, new best angle
            if temp < best:
                best = temp
                out = blob
        try:
            return out
        except UnboundLocalError:
            print "Broken pick_blob"
            print blobs_lst
            print neutron
            print temp
            raise ValueError

    else:
        raise NotImplementedError("Option %s doesn't exist" % option)


def make_blob_neutrons(e_i, datatype):

    if datatype == 0:
        raise AttributeError("mc blob in progress")
    elif datatype == 1:
        pass
    elif datatype == 2:
        blobs = get_blob_neutron_data(e_i)
    return blobs

@versioncontrol
def get_blob_neutron_data(e_i, blob_prefix="DATA_BLOB_PREFIX"):
    #return a list of blob [E, x, y, z] vectors for the current evt

    #ReferenceError
    #Check for the true number of blobs
    for i,dim in enumerate(["X_sz", "Y_sz", "Z_sz"]):
        #!?!?! #FIXME
        n_blobs = 1
        continue
        if i==0:
            try:
                n_blobs = int(IO.get_subtree().GetLeaf(blob_prefix+dim).GetValue())
            except ReferenceError:
                log.error("Could not access branch %s" % blob_prefix+dim)
                sys.exit()
			#Skip empty events as early as possible
            if n_blobs == 0:
				return [None]
                #parse the rest of blob dims for consistency
        elif int(IO.get_subtree().GetLeaf(blob_prefix+dim).GetValue())!= n_blobs:
            log.warning("Error at event %i: Inconsistent number of blobs" % e_i)
            return None

    #Iterate over x, y, z positions and fetch blob vecs
    vecs_out = [[0,0,0,0] for i in range(n_blobs)]
    for dim, suffix in enumerate(["E", "X", "Y", "Z"]):

        for i in range(n_blobs):
            try:
                val = IO.get_subtree().GetLeaf(blob_prefix+suffix).GetValue()
            except ReferenceError:
                log.error("Could not access branch %s" % blob_prefix+suffix)
                sys.exit()
            #Reject bad values
            if val < -9999:
                return None
            vecs_out[i][dim] = val

    return [np.array(lst) for lst in vecs_out]

def get_mu(e_i, datatype):
    #TODO
    return

@versioncontrol
def get_mu_data(e_i, mu_branch="RECON_MU_P_PREFIX"):

    out = [0,0,0,0]
    for i, suffix in enumerate(["E_mu", "px_mu", "py_mu", "pz_mu"]):
        out[i] = event.fetch_val_base(e_i, mu_branch+suffix)
    return np.array(out)

def get_vtx(e_i, datatype=0):
    if datatype == 0:
        return get_vtx_mc(e_i)
    elif datatype == 1:
        return get_vtx_data(e_i)
    elif datatype == 2:
        #TODO:
        pass
@versioncontrol
def get_vtx_mc(e_i, vtx_branch="MC_VTX"):
    #Passed an event index, return the mc VTX "4-vec"
    return event.fetch_vec_base(e_i, vtx_branch)
@versioncontrol
def get_vtx_data(e_i, vtx_branch="RECON_VTX"):
    #Passed an event index, return the mc VTX "4-vec"
    return event.fetch_vec_base(e_i, vtx_branch)

#FIXME: Different fill methods depending on MC, DATA, RECON
def get_n_parts(e_i, datatype=0):
    if datatype == 0:
        return get_n_parts_mc(e_i)
    elif datatype == 1:
        return get_n_parts_data(e_i)
    elif datatype == 2:
        #TODO:
        pass
@versioncontrol
def get_n_parts_mc(evt, nparts_leaf="MC_N_PART"):
    #Get the number of particles in this event
    try:
        out = int(IO.get_subtree().GetLeaf(nparts_leaf).GetValue())
    except IOError:
        #get_subtree() failed
        log.error("Leaf %s does not exist - could not access n_parts" % nparts_leaf)
        os._exit()
    else:
        return out
@versioncontrol
def get_n_parts_data(evt, nparts_leaf="????"):
    #TODO:
    return None

def get_particle_lst(e_i, datatype):
    #Return a list of particle objects for this event index
    n_parts = get_n_parts(e_i, datatype)
    particle_lst = []   #a list of par

    #Initialize a list of particles for the event
    p_i = 0
    for i in range(n_parts):
        particle_lst.append(event.Particle(p_i, e_i))
        p_i += 1
    for part in particle_lst:
        #Fill the particle's name, returning success/failure
        good_fill = event.fill_particle(part, datatype=datatype)

    #Add the neutrino foundation - calculate later
    nu = event.get_neutrino(p_i, e_i, datatype=datatype)
    particle_lst.append(nu)

    return particle_lst

def fetch_mu(particle_lst):
    #return the particle object for a antimuon(s) in the event
    mu_lst = filter(lambda x: abs(x.ID)==13, particle_lst)
    if len(mu_lst) == 1:
        return mu_lst[0]
    else:
        return None
        #raise AttributeError("Cannot parse events with more/less than 1 muon")

def fetch_neutrons_mc(particle_lst):
    #compile a list of mc neutrons in this event
    #only relevant for mc
    n_lst = filter(lambda x: abs(x.ID)==2112, particle_lst)
    return n_lst

def count_protons(particle_lst):
    p_lst = filter(lambda x: abs(x.ID)==2212, particle_lst)
    return len(p_lst)

def main():

    return

if __name__ == "__main__":
    main()
