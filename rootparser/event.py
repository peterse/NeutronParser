from IO import versioncontrol
import numpy as np
import dctROOTv9 as dR

"""MC.py - Root tools for interfacing with an MC-generated Minerva tree"""


######################################################################
class Event:
    """A general event characterized by a list of particle objects and some metadata"""
    #Class-wide attributes

    def __init__(self, index, tree_handle):
        #Instance attributes
        self.particle_lst = []
        self.index = index          #event number
        self.tree = tree_handle     #active TTree
        #How do we want to init?
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

######################################################################
class Particle:
    """Representation of a particle pulled from a given event"""

    def __init__(self):
        #metadata
        self.event_index = None

        #identification
        self.ID = None
        self.name = None

        #Energy-momentum 4-vector
        self.P = [0,0,0,0]
        self.p = [0, 0, 0]

        return



def EventParser(start, end, tree_handle):
    #Passed an open Rootfile, GENERATE Event objects in the event range (start, end)
    while start < end:
        print "Iteration %i" % start
        yield Event(start, tree_handle)
        start += 1

def ParseEvents():

    return

#FIXME: how will we access the current tree? What is its name?
#FIXME: two possible implementations for momentum leaf
#           1) three separate leafs: mc_FSPartPx, mc_FSPartPy, ...
#           2) A leaf with subleafs: mc_FSPartP -> Values 0, 1, 2
@versioncontrol
def get_4vec(evt, xyz_prefix="PART_XYZ_PREFIX", energy="PART_E"):
    #Get the 4-vector for a particle with index i at event evt
    out = [0,0,0,0]
    #Put momenta in indices 1-3
    for dim_i, dim in enumerate(["x", "y", "z"]):
        leaf = xyz_prefix + dim
        out[dim_i+1] = evt.tree.GetLeaf(leaf).GetValue(evt.i)

    #Put energy at index 0
    out[0] = evt.tree.GetLeaf(energy).GetValue(evt.i)

    return np.array(out)

def get_4vec_mc(evt):
    return get_4vec(evt, xyz_prefix="MC_PART_XYZ_PREFIX", energy="MC_PART_E")

def get_4vec_data(evt):
    return get_4vec(evt, xyz_prefix="DATA_PART_XYZ_PREFIX", energy="DATA_PART_E")


@versioncontrol
def get_name(evt, nu_branch="INCOMING_PART", id_branch="PART_ID"):
	#Get the ID,name of a particle based on FS PDG or incoming info
	if incoming:
		leaf_obj = self.current_tree.GetLeaf(nu_branch) #FIXME: ????
		evt_id = 0
	else:
		evt_id = self.current_tree.GetLeaf(id_branch).GetValue(i)

	return int(evt_id), dR.PDGTools.decode_ID(evt_id, quiet=self.quiet) #(ID, name)

def get_name_mc(evt):
    return get_name(evt, nu_branch="MC_INCOMING_PART", id_branch="MC_PART_ID")

def get_name_data(evt):
    return get_name(evt, nu_branch="DATA_INCOMING_PART", id_branch="DATA_PART_ID")

if __name__ == "__main__":

    #MODEL FOR PARALLEL PROGRAMMING
    #OUTPUT LIST = FUNCTION MAPPED OVER (LIST OF EVENT OBJECTS)
    #What is the desired output?
    #result = map(function, EventGenerator(start, end))

    get_4vec(1,2)
    get_4vec_mc(1,2)

    Events = EventParser(1,10,None)
    for evt in Events:
        print str(evt)
