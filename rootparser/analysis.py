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

import rootpy
import root_numpy as rnp
import numpy as np

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
        self.particle_lst = []
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

        #angle comparisons
        self.mu_dot_n_T = None

        self.rvb = None
        #Post-Filter
        self.final_E_n = None       #Final neutron/blob energy


def MLsandbox(filename, path, target, dest, hist=True, filt=True, dump=True):
    pid = os.getpid()
    filepath = "%s/%s" % (path, filename)
    log.info("PID %s parsing %s" % (pid, filepath))

    with rootpy.io.root_open(filepath) as fh:
        for subtree in IO.get_next_tree(fh):
            #pass the tree to the global space for access by funcs
            IO.put_subtree(pid, subtree)

            #convert our subtree into an np array
            #TODO:
            datatype = 0
            filterlst = make_filter_list(datatype)
            tree_arr = rnp.tree2array(subtree)
            print tree_arr.dtype.names
            print tree_arr[0]

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
                else:
                    try:
                        subtree.GetLeaf(br_name).GetValue()
                    except ReferenceError:
                        missing_br.append(br_name)

            if report:
                print "Tree %s missing branches:" % subtree.GetName()
                for br in missing_br:
                    print "   ", br

    #non-zero return idicates error
    return any(missing_br)





def ParseEventsNP(filename, path, target, dest, hist=True, filt=True, dump=True, ML=False):
    #filename is the file being analyzed
    #   path is its location
    #target is the desired output filename
    #   dest is its location
    #High-level parsing routine
    pid = os.getpid()

    filepath = "%s/%s" % (path, filename)
    log.info("PID %s parsing %s" % (pid, filepath))



    if hist or hist_target:
        hist_target = "%s/%s" % (dest, target)
        #Initialize histograms
        export_lst = hi.extend_export_lst(hi.all_export_lst)
        subhist_dct = hi.init_hist_dct(export_lst)
        IO.put_subhist(subhist_dct)



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
                if e_i > 10000:
                    break
                if e_i % 1000 == 0:
                    log.info("Processing event %i" % e_i)

                #PARTICLES
                particle_lst = get_particle_lst(e_i, datatype)

                #MUON
                mu = fetch_mu(particle_lst)
                if mu is None:
                    continue    #FIXME: we need statistics - apply filter!
                P_mu = mu.P

                #BLOBS
                #FIXME
                blobs = make_blob_neutrons(e_i, datatype=2)
                blob = pick_blob(blobs)

                #MC NEUTRON
                mc_neutrons = fetch_neutrons_mc(particle_lst)
                n_neutrons = len(mc_neutrons)
                if n_neutrons == 1:
                    mc_n_P = mc_neutrons[0].P
                #Case for n_neutrons != 1:
                else:
                    continue        #FIXME: apply filter!

                #KINE-NEUTRON
                mc_kine_n_P = make_kine_neutron(P_mu)

                #VERTEX
                mc_vtx = get_vtx(e_i, datatype=0)
                recon_vtx = get_vtx(e_i, datatype=2)
                if True:
                    #FIXME: condition for acceptable vertex discrepancy...
                    #FIXME: Not working right now- weirdness w TLorentzVector?
                    vtx = mc_vtx

                #Summarize this event
                evt = EventSummary(e_i, datatype)
                evt.n_parts = 0
                evt.n_neutrons = n_neutrons
                evt.n_blobs = len(blobs)
                evt.n_protons = count_protons(particle_lst)
                #mc-specific metadata
                if datatype == 0:
                    evt.int_type = get_mc_int_type(e_i)


                #CALCULATED QUANTITIES

                #filters: 'continue' means we're done with this event
                if not fi.AntiQE_like_event(evt):
                    #log.info("Event %i not CCQE-like" % e_i )
                    continue

                #histogramming
                lookup_dct = {
                            "recon_kine_n_P": None,
                             "mc_kine_n_P": mc_kine_n_P,
                             "mc_n_P": mc_n_P,
                             "n_blob": blob
                             }
                hi.make_comp_hists(lookup_dct)      #N-COMPARISONS
                hi.make_neutron_hists(lookup_dct)   #INDIVIDUAL NEUTRONS

                #Checking relative angles

                #MC kine-neutron vs. SINGLE mc neutron
                dangle, separation = Mm.compare_vecs(mc_n_P, mc_kine_n_P)
                # print mc_n_P, type(mc_n_P)
                # print mc_kine_n_P, type( mc_kine_n_P)
                # print P_mu, type(P_mu)
                # print dangle

                #print dangle

                continue
                #ML training set
                #TODO: IF this is a good kine event,
                if True:
                    category_lst[e_i] = 1
                else:
                    continue


            #FIXME
            #only iterate first tree?
            break

        #Set up ML arrays
        if ML:
            tree_arr = rnp.tree2array(subtree)

        #Write out histograms
        hi.write_hists(hist_target)

@versioncontrol
def get_mc_int_type(e_i, typ="MC_TYPE"):
    #MC datatype indicates what ccque event type was run in the interaction
    return int(IO.get_subtree().GetLeaf(typ).GetValue())

def make_kine_neutron(P_mu):
    #passed an event, generate an MC and recon neutron, if possible
    return Mm.make_neutron_P(P_mu)

def pick_blob(blobs_lst):
    #TODO: What if there's a lot of blobs?
    #criteria for choosing the best blob
    blob = blobs_lst[0]
    return blob

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
