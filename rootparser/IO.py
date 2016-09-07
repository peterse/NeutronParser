"""IO.py - supports I/O for parsing rootfiles, particularly naming
conventions for finding specific values in the tree"""

import ROOT


#A conversion dictionary for the VALUE_YOU_NEED: branch_to_access
lookup_dct = {
            "MC_N_PART": "mc_nFSpart",
            "MC_PART_XYZ_PREFIX": "mc_FSPartP",
            "MC_PART_E": "mc_FSPartE",
            "MC_PART_ID": "mc_FSPartPDG",
            "MC_INCOMING_PART": "mc_incoming",
            "DATA_PART_E": "derp",
            "DATA_PART_XYZ_PREFIX": "derp2"


            }


#Set up wrappers for implementing functions specific to a version of a tree
def versioncontrol(func):
    #Replace function default values with their matching value in the lookup dict
    def substitute_and_call(*args, **kwargs):
        substitute = []
        for key in func.func_defaults:
            if key in lookup_dct:
                substitute.append(lookup_dct[key])
            else:
                substitute.append(key)
        func.func_defaults = tuple(substitute)
        return func(*args, **kwargs)

    return substitute_and_call


#BASE Particle utilities must take the names of the branches they're searching as args



if __name__ == "__main__":

    get_4vec(1,2)
