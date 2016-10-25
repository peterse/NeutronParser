"""filter.py - functions for filtering event.Event() objects according to interaction type.""""


#Filter criteria
PHI_T_MIN = 175     #transverse angle of mu,n -> should be 180deg
E_N_MIN = 50        #neutron (and kine neutron!) minimum angle
RVB_MIN = 0         #minimum vertex-blob distance

#TODO: dealing with MC vs. recon or real

def AntiQE_like_event(evt):
    #Attempt to determine if event was QE-like for antinu -> mu+

    #MC case
    if evt.datatype == 0:
        #get proper leaf from MC for evt type
        #FIXME: check that this is the correct event type
        return evt.type == 1

    #Data, recon case
    elif datatype == 1 or datatype == 2:
        #FIXME: is this going to work if MC evts are filling n_protons etc?
        #one blob, one neutron, no protons
        if evt.n_neutrons == 1 and evt.n_protons == 0:
            return True

def QE_like_event(evt):
    #Attempt to determine if the event was QE-like for nu -> mu-

    #MC case
    if evt.datatype == 0:
        #get proper leaf from MC for evt type
        #FIXME: check that this is the correct event type
        return evt.type == 2

    #Data, recon case
    elif datatype == 1 or datatype == 2:
        #FIXME: is this going to work if MC evts are filling n_protons etc?
        #one blob, one neutron, no protons
        if evt.n_neutrons == 0 and evt.n_protons == 1:
            return True

def one_blob_one_n(evt):
    #Precondition: Evt was either QE or AntiQE
    #Determine if one-neutron-one-blob is true
    return evt.n_neutrons == 1 and evt.n_blobs == 1

def recon_good(evt):
    #Demonstrate that the recon data was valid
    #TODO
    return

def kine_neutrons_good(evt):
    #A prerequisite for plotting kine neutrons
    #TODO:
    return

def phiT_good(evt):
    #Require the muon/neutron to be move at ~180deg in the xverse plane
    return evt.mu_dot_n_T < PHI_T_MIN

def E_N_good(evt):
    #Precondition: evt must be filtered for 1 neutron first
    return evt.final_E_n > E_N_MIN

def RVB_good(evt):
    #Precondition: evt must be filtered for 1 neutron
    #Filter based on minimum distance vertex-blob
    return evt.rvb > RVB_MIN
