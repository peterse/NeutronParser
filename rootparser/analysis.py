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

import event

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

def ParseEventsNP(filepath, hist=True, filt=True, dump=True):
    #High-level parsing routine
    pid = os.getpid()
    log.info("PID %s parsing %s" % (pid, filepath))

    if hist:
        #Initialize histograms
        export_lst = hi.extend_export_lst(hi.all_export_lst)
        subhist_dct = hi.init_hist_dct(export_lst)
        IO.put_subhist(subhist_dct)

    #Parse input files
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

            #Iterate over the event and get necessary components
            for e_i in enumerate(tree_arr):

                #PARTICLES
                particle_lst = get_particle_lst(e_i, datatype)
                #MUON
                P_mu = fetch_mu(particle_lst).P

                #VERTEX
                #FIXME: we're getting a vertex from MC OR DATA - resolve conflicts?
                mc_vtx = get_vtx(e_i, datatype=0)
                recon_vtx = get_vtx(e_i, datatype=2)
                if True:
                    #FIXME: condition for acceptable vertex discrepancy...
                    #FIXME: Not working right now- weirdness w TLorentzVector?
                    vtx = mc_vtx

                #BLOB
                blob = make_blob_neutron(e_i, datatype=2)

                #KINE-NEUTRON
                mc_kine_n_P = make_kine_neutron(P_mu)

                #filters

                #histogramming

                #N-COMPARISONS
                lookup_dct = {
                            "recon_kine_n_P": None,
                             "mc_kine_n_P": mc_kine_n_P,
                             "mc_n_P": None,
                             "n_blob": blob}

                for n_pair in hi.n_pairs:
                    n0 = n_pair[0]
                    n1 = n_pair[1]
                    #ENERGIES
                    E_compare = make_n_comp_energy_name(n_pair)
                    fill_hist(E_compare, n0[0], n1[0])

            #FIXME
            #only iterate first tree?
            break


def make_kine_neutron(P_mu):
    #passed an event, generate an MC and recon neutron, if possible
    return Mm.make_neutron_P(P_mu)

def make_blob_neutron(e_i, datatype):

    #TODO: What if there's a lot of blobs?
    if datatype == 0:
        raise AttributeError("mc blob in progress")
    elif datatype == 1:
        pass
    elif datatype == 2:
        blob = get_blob_neutron_data(e_i)

    return blob
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
            n_blobs = int(IO.get_subtree().GetLeaf(blob_prefix+dim).GetValue())
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
            val = IO.get_subtree().GetLeaf(blob_prefix+suffix).GetValue()
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
        raise AttributeError("Cannot parse events with more/less than 1 muon")

def main():

    return

if __name__ == "__main__":
    main()
