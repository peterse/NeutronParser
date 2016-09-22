from IO import versioncontrol
import numpy as np
import MINERvAmath
import dctROOTv9 as dR


#utilities
import time
import sys
import os

#File management
import IO


"""MC.py - Root tools for interfacing with an MC-generated Minerva tree"""

#how do we want to design events around a filetype using low function overhead?
#   1. class inheritance: Subclass an event to MC_Event, DATA_Event... ugh
#   2. conditional method definitions -> requires Class to have arguments...
#   3. conditional within method to return submethod with correct leafname kwargs


######################################################################
class Event:
    """A general event characterized by a list of particle objects and some metadata"""
    #Class-wide attributes
    #   index: The event number handled by this object
    #   tree_handle: the active TTree
    #   filetype: Determines which functions to implement based on branch names

    def __init__(self, index, tree_handle, filetype=0):
        #Instance attributes
        self.particle_lst = []      #FIXME: Distinguish 'natural' particles from
                                    #generated ones?
        self.particles_extra = []
        self.index = index          #event number
        self.tree = tree_handle     #active TTree
        self.filetype = filetype



        self.n_parts = 0
        self.P = [0, 0, 0, 0]       #Total event momentum
        #Event filling:
        #   1) discover the number of particles
        #   2) iterate over particles creating 'Particle' objects
        #self.n_parts = self.fetch_n_parts()

        return

    def __str__(self):
        #A representation of this event; dump particles?
        return str(self.particle_lst)

    # # # Container methods # # #
    def __len__(self):
        return len(self.particle_lst)

    def __getitem__(self, key):
        #Get a particle using 'key' - how will we arrange this
        return self.particle_lst[key]

    def __setitem__(self, key, val):
        self.particle_lst[key] = val

    def __delitem__(self, key):
        del self.particle_lst[key]

    def __iter__(self):
        return iter(self.particle_lst)

    def get_neutrons(self):

        return

    def get_protons(self):

        return

    def get_leptons(self):

        return


    def __iadd__(self, particle):
        #define addition
        self.particle_lst.append(particle)
        return self

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#Global-scoped method for parsing events
#Will modify the 'Event' object passed into it
def fill_event(evt_obj):

    #Attempt to fill an event

    #IO: Get number of particles
    b1 = fetch_n_parts_mc(evt_obj)

    #IO: Get particle momenta and all other necessary attributes
    b2 = fill_parts(evt_obj)

    #CPU: Do calculations within the particles
    #b3 = calculate_parts(evt_obj)

    #Proper return conditional on successful methods
    if b1 and b2:
        return evt_obj
    else:
        #TODO: handling bad event fills
        return None

@versioncontrol
def fetch_n_parts_mc(evt, nparts_leaf="MC_N_PART"):
    #Get the number of particles in this event
    while True:
        try:
            k = IO.get_subtree().GetEvent(evt.index) #FIXME: nullified by subtreeing
            out = int(IO.get_subtree().GetLeaf(nparts_leaf).GetValue())

            #FIXME: Eventually, only assign
            evt.n_parts = out
            return True

        except:
            #There was a clash for access, take a nap!:
            time.sleep(.001)
        else:
            pass

def fetch_vec_base(e_i, leafname):
    #Return the value of a general leaf/branch
    #Return type: list
    out = [0, 0, 0, 0]
    #FIXME: Are we sure this is the general order of vector components?
    for i, dim in enumerate([ "x", "y", "z", "t"]):
        out[i] = IO.get_subtree().GetLeaf(leafname).GetValue(i)

    return out

@versioncontrol
def get_vtx_mc(e_i, vtx_branch="MC_VTX"):
    #Passed an event index, return the mc VTX "4-vec"
    return fetch_vec_base(e_i, branch)

@versioncontrol
def get_vtx_data(e_i, vtx_branch="RECON_VTX"):
    #Passed an event index, return the mc VTX "4-vec"
    return fetch_vec_base(e_i, branch)



def get_name_base(p_i, inc=False, nu_branch, id_branch):
	#Get the ID,name of a particle based on FS PDG or incoming info
    if incoming:
        #nu doesn't use 'GetValue(p_i)' since it has its own branch
        #FIXME:
        evt_id = IO.get_subtree().GetLeaf(nu_branch).GetValue()
        evt_
        evt_id = 0
    else:
        evt_id = IO.get_subtree().GetLeaf(id_branch).GetValue(p_i)

	return int(evt_id), dR.PDGTools.decode_ID(evt_id, quiet=True) #(ID, name)

@versioncontrol
def get_name_mc(p_i, inc=False, nu_branch="MC_INCOMING_PART", id_branch="MC_PART_ID"):
    return get_name_base(p_i, inc=inc, nu_branch, id_branch)




#FIXME: Different fill methods depending on MC, DATA, RECON
def fill_parts(evt):
    #Passed an event, instruct its particles to fill from the event index

    #Initialize a list of particles for the event
    p_i = 0
    for i in range(evt.n_parts):
        evt.particle_lst.append(Particle(p_i, evt.index))
        p_i += 1

    for part in evt.particle_lst:
        #Fill the particle's name, returning success/failure
        good_fill = fill_particle_mc(part)

    #Add the neutrino
    evt.nu = get_neutrino(p_i, evt.index)

    #Add the vertex
    #FIXME: we're getting a vertex from MC OR DATA - resolve conflicts?
    mc_vtx = get_vtx(evt.index, datatype=0)
    recon_vtx = get_vtx(evt.index, datatype=2)
    if 1:       #FIXME: condition for acceptable vertex discrepancy...
        evt.vtx = recon_vtx

    #Add the blobs
    

    #FIXME: Is nu part of the particle list or not?
    #evt.particle_lst.append()
    #p_i += 1



    evt.particle_lst.append(make_kine_neutron(p_i, evt.index))
    p_i += 1

    return good_fill

def calculate_total_P(evt):
    #For a filled event, find the total 4-vector of the identified particles
    #To be called before reconstructing

    #Make a list of particle momenta in the event
    P_lst = [ part.P for part in evt.particle_lst ]
    #Sum the particle momenta element-wise
    evt.P = np.sum(P_lst, axis=0)

    return True

def calculate_parts(evt):
    #Passed an event with particles, do strictly-CPU calculations on particle
    #attributes to find dereived quantities

    #Particle mass
    for particle in evt.particle_lst:

        good_calc = calculate_attrs(part)

    #Get tracked particles' total momentum
    good_P = calculate_total_P(evt)
    #Recreate a neutrino signature using event momentum
    good_nu = calculate_neutrino(evt)
    return None


def calculate_neutrino(evt):
    #Passed an Event object, build on the skeletal nu to get a fully-defined nu
    evt.nu.P = np.array(evt.nu.P[0], evt.P[1], evt.P[2], evt.P[3])

    #TODO: Use energy differential to discover something about the event?
    N_guess = evt.nu.P[0] - evt.P[0]



######################################################################
class Particle:
    """Representation of a particle pulled from a given event"""

    def __init__(self, particle_index, event_index):
        #metadata:
        self.event_index = event_index
        self.index = particle_index #the index of this particle within an event
        #identification
        self.ID = None
        self.name = None

        #Energy-momentum 4-vector
        self.P = [0,0,0,0]
        self.p = [0, 0, 0]

        #Other event data
        self.inc = False    #incoming neutrino?

        return
    #FIXME: how will we access the current tree? What is its name?
    #FIXME: two possible implementations for momentum leaf
    #           1) three separate leafs: mc_FSPartPx, mc_FSPartPy, ...
    #    --->   2) A leaf with subleafs: mc_FSPartP -> Values 0, 1, 2


######################################################################
#I / O FUNCTIONS FOR PARTICLE filling

#Inputs: particle index, names of ID branches
#Precondition: Expects particle information to be arranged under leafs such that
#GetLeaf(leaf).GetValue(particle-index) returns the corresponding Particle ID
#FIXME: What does incoming signify?
def get_name(p_i, inc=False, datatype=0):
    if datatype == 0:
        return get_name_mc(p_i, inc)
    elif datatype == 1:
        return get_name_data(p_i, inc)
    elif datatype == 2:
        #TODO:
        pass


def get_name_base(p_i, inc=False, nu_branch, id_branch):
	#Get the ID,name of a particle based on FS PDG or incoming info
    if incoming:
        #nu doesn't use 'GetValue(p_i)' since it has its own branch
        #FIXME:
        evt_id = IO.get_subtree().GetLeaf(nu_branch).GetValue()
        evt_
        evt_id = 0
    else:
        evt_id = IO.get_subtree().GetLeaf(id_branch).GetValue(p_i)

	return int(evt_id), dR.PDGTools.decode_ID(evt_id, quiet=True) #(ID, name)

@versioncontrol
def get_name_mc(p_i, inc=False, nu_branch="MC_INCOMING_PART", id_branch="MC_PART_ID"):
    return get_name_base(p_i, inc=inc, nu_branch, id_branch)

@versioncontrol
def get_name_data(p_i, inc=False, nu_branch="DATA_INCOMING_PART", id_branch="DATA_PART_ID"):
    return get_name_base(p_i, inc=inc, nu_branch, id_branch)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#Globally-scoped functions for modifying particle object
def fill_particle(part):

    #Particle name
    part.ID, part.name = get_name(part.index, part.inc)
    #particle
    part.P = get_4vec(part.index, part.event_index, datatype=0)

    #TODO: Assignment vs return
    return 1

#TODO: Decorator or not for this?
#@datatype
def get_4vec(p_i, e_i, datatype=0):
    #Highest level function to determine call-type for 4vector
    if datatype == 0:
        return get_4vec_mc(p_i, e_i)
    elif datatype == 1:
        return get_4vec_data(p_i, e_i)
    elif datatype == 2:
        #TODO:
        pass

def get_4vec_base(p_i, e_i, xyz_prefix, energy):
    #Get the 4-vector for a particle with index i at event evt
    #p_i is the particle index at event e_i
    out = [0,0,0,0]
    #Put momenta in indices 1-3
    for dim_i, dim in enumerate(["x", "y", "z"]):
        leaf = xyz_prefix + dim
        IO.get_subtree().GetEvent(e_i)  #FIXME: not necessary with subtreeing
        out[dim_i+1] = IO.get_subtree().GetLeaf(leaf).GetValue(p_i)

    #Put energy at index 0
    IO.get_subtree().GetEvent(e_i)
    out[0] = IO.get_subtree().GetLeaf(energy).GetValue(p_i)

    return np.array(out)

@versioncontrol
def get_4vec_mc(p_i, e_i, xyz_prefix="MC_PART_XYZ_PREFIX", energy="MC_PART_E"):
    return get_4vec_base(p_i, e_i, xyz_prefix, energy)
@versioncontrol
def get_4vec_data(p_i, e_i, xyz_prefix="DATA_PART_XYZ_PREFIX", energy="DATA_PART_E"):
    return get_4vec_base(p_i, e_i, xyz_prefix, energy)

######################################################################
# PROCESSING functions for particle calculations

def calculate_attrs(part):

    part.mass = MINERvAmath.get_mass(part.P)


def get_neutrino_base(p_i, e_i):
    #Generate a particle object representation for a neutrino
    nu = Particle(p_i, e_i)
    nu.inc = True

    #Get the neutrino name information
    nu.ID, nu.name = get_name(p_i, nu.inc)
    #Fill in what we can about energy - momentum isn't available!
    E = IO.get_subtree().GetLeaf(nu_energy).GetValue()
    nu.P = [E, 0, 0, 0]
    return


@versioncontrol
def get_neutrino_mc(p_i, e_i, nu_energy="MC_INCOMING_ENERGY"):
    return get_4vec_base(p_i, e_i, nu_energy)



def make_kine_neutron(p_i, e_i):
    #Passed an event number and particle index, generate a kinematic neutron


######################################################################

def EventParser(start, end, tree_handle):
    #Passed an open Rootfile, GENERATE Event objects in the event range (start, end)
    return [Event(i, tree_handle) for i in range(start, end)]
    # while start < end:
    #     #print "Iteration %i" % start
    #     yield Event(start, tree_handle)
    #     start += 1

#Crawl through the tree and run Event's main routine
def ParseEvents(start, end, tree_handle):

    return



if __name__ == "__main__":

    #MODEL FOR PARALLEL PROGRAMMING
    #OUTPUT LIST = FUNCTION MAPPED OVER (LIST OF EVENT OBJECTS)
    #What is the desired output?
    #result = map(function, EventGenerator(start, end))
    pass
    #get_4vec(1,2)
    #get_4vec_mc(1,2)
