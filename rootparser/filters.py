"""filter.py - functions for filtering event.Event() objects according to interaction type."""

from rootparser_exceptions import log

#checkign N_THREADS
import parallel

#Filter criteria
FIL = {
        EVENT_MAX = None,         #Stopping point
        PHI_T_DIFF_MAX = None,    #transverse angle of mu,n from (x,180deg)
        E_N_MIN = None,           #neutron (and kine neutron!) minimum angle
        RVB_MIN = None,           #minimum vertex-blob distance
        MU_BLOB_THETA_MIN = None, #Muon vs. Blob minimum approach
        ONE_BLOB_ONE_N = None
        }


#TODO: dealing with MC vs. recon or real

def SetFilters(deck, report=True):
    """
    Passed an input deck, set the filters that will be used to
    discriminate on event acceptance

    Must be called after parallel module is initialized w/
    N_THREADS
    """
    if report:
        print_lst = []

    with open(deck, 'r') as fh:
        content = fh.readlines()
        #filters use fields 'name' 'value'
        global FIL
        for line in content:
            splitline = line.strip().split(" ")
            k = splitline[0]
            val = float(splitline[1])
            if k in FIL:
                FIL[k] = val
            else:
                log.error("%s filter not recognized. Check filter deck %s before continuing" % (k, deck))
                raise KeyError

    log.info("Setting filters...")
    if report:
        for k, v in FIL.iteritems():
            print_lst.append((k, v))
        print "\n\t".join([a+"="+str(b) for (a,b) in print_lst])

    return FIL

def event_max(evt):
    return evt.index >= EVENT_MAX

def AntiQE_like_event(evt):
    #Attempt to determine if event was QE-like for antinu -> mu+

    #MC case
    if evt.datatype == 0:
        #get proper leaf from MC for evt type
        #FIXME: check that this is the correct event type
        return evt.int_type == 1

    #Data, recon case
    elif datatype == 1 or datatype == 2:
        #FIXME: is this going to work if MC evts are filling n_protons etc?
        #one blob, one neutron, no protons
        if evt.n_neutrons == 1 and evt.n_protons == 0:
            return True

def phiT_good(evt):
    #Require the muon/neutron transverse angle to be within
    # 'diff' of 180deg devrees
    upper = 180 + PHI_T_DIFF_MAX
    lower = 180 - PHI_T_DIFF_MAX
    return evt.phiT < upper and evt.phiT > lower

def mu_blob_theta_good(evt):
    #Require the blob to be outside of X deg. of the muon track
    return evt.THETA_mu_blob > MU_BLOB_THETA_MIN

def QE_like_event(evt):
    #Attempt to determine if the event was QE-like for nu -> mu-

    #MC case
    if evt.datatype == 0:
        #get proper leaf from MC for evt type
        #FIXME: check that this is the correct event type
        return evt.int_type == 2

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
    return True

def kine_neutrons_good(evt):
    #A prerequisite for plotting kine neutrons
    #TODO:
    return True



def E_N_good(evt):
    #Precondition: evt must be filtered for 1 neutron first
    return evt.final_E_n > E_N_MIN

def RVB_good(evt):
    #Precondition: evt must be filtered for 1 neutron
    #Filter based on minimum distance vertex-blob
    return evt.RVB > RVB_MIN
