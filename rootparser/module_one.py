from IO import versioncontrol
import numpy as np

"""MC.py - Root tools for interfacing with an MC-generated Minerva tree"""


######################################################################
class Event:
    """A general event characterized by a list of particle objects and some metadata"""
    #Class-wide attributes

    def __init__(self, index, f):
        #Instance attributes
        self.particle_lst = []

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



def EventParser(start, end, f):
    #Passed an open Rootfile, GENERATE Event objects in the event range (start, end)
    while start < end:
        print "Iteration %i" % start
        yield Event(start, f)
        start += 1

def ParseEvents():

    return

#FIXME: how will we access the current tree? What is its name?
@versioncontrol
def get_4vec(evt, i, xyz_prefix="PART_XYZ_PREFIX", energy="PART_E"):
    #Get the 4-vector for a particle with index i at event evt
    out = [0,0,0,0]
    #Put momenta in indices 1-3
    for dim_i, dim in enumerate(["x", "y", "z"]):
        leaf = xyz_prefix + dim
        #out[dim_i+1] = self.current_tree.GetLeaf(leaf).GetValue(i)

    #Put energy at index 0
    #out[0] = self.current_tree.GetLeaf(energy).GetValue(i)

    return np.array(out)

def get_4vec_mc(evt, i):
    return get_4vec(evt, i, xyz_prefix="MC_PART_XYZ_PREFIX", energy="MC_PART_E")

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
