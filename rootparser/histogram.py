"""histogram.py - main methods for interfacing data with ROOT histograms"""

from rootpy.plotting import Hist, Hist2D
from collections import OrderedDict

#errors, warnings
from rootparser_exceptions import log

#IO
import IO   #get, put, histogram interfacing
import rootpy
import os   #getpid


#Where we'll put the output histograms
class HistogramManager:
    """Managing a .root file for storing historgrams from processing events in another root file"""



    def __init__(self):

        self.export_filename = None



#list of all supported export types, (name, (bins, min max), y-units)
all_export_lst = [
                ("null", (100,-1,1), "-" ),
                ("n_trans_angle", (100,0,360), "deg" ),
                ("p_trans_angle", (100, 0, 360), "deg" ),
                ("nu_px", (100,-300, 300), "MeV/c" ),
                ("nu_py", (100, -300, 300), "MeV/c"),
                ("mu_x_err", (100,0,1), "-"),
                ("mu_y_err", (100,0,1), "-" ),
                ("mu_z_err", (100, 0, 1), "-"),
                ("N_blobs-N_neutrons", (20, -10, 10), "Number of Neutrons", "counts"),
                ("theta_nvb", (90, 0, 180), "deg", "counts/deg"),
                ("cos(theta_nvb)", (90, 0, 1), "-", "counts" ),
                ("theta_nvb_vs_En_datatype", (30, 0, 1200, 30, 0, 180), "E (MeV)", "Theta (deg)" ),
                ("v_n(mc)_dot_v_mu", (100, 0, 360), "deg" ),
                ("phiT", (100, 0, 360), "deg" ),
                ("Dphi_T", (100, 0, 360), "deg" ),
                ("mu_dangle", (100, 0, 20), "deg" ),
                ("r_vb", (25, 0, 2000), "R_vb (mm)", "counts/mm" ),
                ("En_0blob", (50, 0, 1200), "Energy (MeV)", "Neutrons/MeV" ),
                ("En_1blob", (50, 0, 1200), "E (Mev)", "1/MeV" ),
                ("En_01blob", (50, 0, 1200), "E (MeV)", "1/MeV" ),
                ("E_n_vs_N_blob", (6, 0, 6, 30, 0, 1200), "N / blobs", "E (MeV)" ),
                ("phi_T_vs_Emu", (30, 0, 1200, 30, 170, 180), "E (MeV)", "phi_T (deg)" ),
                ("phiT_vs_En", (30, 0, 1200, 30, 170, 180), "E (MeV)", "phi_T (deg)" ),
                ("Blob_find_efficiency", (50, 0, 1200), "-" ),
                ("theta_nvb_vs_Eblob", (20, 0, 450, 45, 0, 180), "E (MeV)", "theta (deg)" ),
                ("theta_nvb_vs_rvb", (30, 0, 600, 45, 0, 180), "R_vb (mm)","theta (deg)"  ),
                ("theta_nvb_vs_DZ", (30, 0, 600, 90, 0, 180), "DZ (mm)", "theta (deg)" ),
                ("Z1_Nblob_vs_MC", (50, 0, 600, 50, 0, 600), "E_blob (MeV)", "E_MC (MeV)"),
                ("Z6_Nblob_vs_MC", (50, 0, 600, 50, 0, 600), "E_blob (MeV)", "E_MC (MeV)")
                ]



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#Neutron comparison names for backwards compatibility
def make_n_energy_name(n_name):
    return "ENERGY_" + n_name
def make_n_pz_name(n_name):
    return "PZ_" + n_name
def make_n_comp_theta_name(tupl):
    return "theta_nvb_deg_%s_vs_%s" % tupl
def make_n_comp_energy_name(tupl):
    return "ENERGIES_%s_vs_%s" % tupl
def make_n_comp_rel_e_name(tupl):
    return "RELATIVE_ENERGY_%s_over_%s" % (tupl[1], tupl[0])

def init_permus(target):
    #Add histogram tuples to the given list:
    #   -all individual simulated neutrons energy and momentum
    #   -permutations of comparison between kine neutrons, blobs, and mc neutrs

    #orderedDict makes permuting easier, but requires ordered construction
    n_dct = OrderedDict({"recon_kine_n_P": None})
    for n_name in ["mc_kine_n_P", "mc_n_P", "n_blob"]:
        n_dct[n_name] = None

    #Individual energies, angles TH1's for simulated n's
    for n_name in n_dct:
        histname1 = make_n_energy_name(n_name)
        target.append( (histname1, (100, 0, 1500), "MeV") )
        histname2 = make_n_pz_name(n_name)
    	target.append( (histname2, (100, 0, 1500), "MeV/c") )

    #Setting up all combinations for comparing neutrons
    n_pairs = []
    for i, (k, v) in enumerate(n_dct.iteritems()):
    	current_k = k
    	#grab every other neutron type, without repeats
    	for j, (k2, v2) in enumerate(n_dct.iteritems()):
    		if j<=i:
    			continue
    		n_pairs.append( (current_k, k2) )

    #Comparisons between types of neutrons
    pair_lst = make_pair_lst(n_pairs)
    target += pair_lst

    return target

def make_pair_lst(n_pairs):
    #passed a list of pairs of neutron types, set up tuples to init histograms
    out = []
    for tupl in n_pairs:
        #angle between the neutrons
    	name_theta = make_n_comp_theta_name(tupl)
        out.append( (name_theta, (90, 0, 180), "deg") )
        #Energy comparisons
        name_energy = make_n_comp_energy_name(tupl)
    	out.append( (name_energy, (50, 0, 600, 50, 0, 600), "MeV", "MeV") )
        #Energy 1 vs Energy 2
    	name_rel = make_n_comp_rel_e_name(tupl)
    	out.append( (name_rel, (30, 0, 2), "MeV/MeV") )

    return out

def init_hist_dct(export_lst):
    #initialize a dictionary of histograms like {name: handle}
    out = {}

    for tupl in export_lst:
        D2 = False
    	#get hist titles
    	try:
    		xname = tupl[2]
    	except IndexError:
    		xname = "-"
    	try:
    		yname = tupl[3]
    	except IndexError:
    		yname = "-"

        #initialize hist handle in dictionary and check for 1D, 2D
        name = tupl[0]
        xbins = tupl[1][0]
        xmin = tupl[1][1]
        xmax = tupl[1][2]
        xlab = tupl[2]
        try:
            ybins = tupl[1][3]
            ymin = tupl[1][4]
            ymax = tupl[1][5]
            ylab = tupl[3]
        except IndexError:
            D2 = False
        else:
            D2 = True
        #Different inits depending on 1D or 2D hist
        if D2:
            out[name] = Hist2D(xbins, xmin, xmax, ybins, ymin, ymax, name=name, title=name)
            out[name].SetOption("COLZ")
        else:
            out[name] = Hist(xbins, xmin, xmax, name=name, title=name)

        #set axes titles
        out[name].GetXaxis().SetTitle(xlab)
        if D2:
            out[name].GetYaxis().SetTitle(ylab)

    return out

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def init_histograms():
    #FIXME: 'path' is read location? write location?
    #Initialize a single PID's histograms to the subhist dct
    global all_export_lst
    hists = init_hist_dct(all_export_lst)

    IO.put_subhist(hists)

def fill_hist(histname, *vals):
    #wrapper for Fill() method that gets a pid's respective histogram dict
    #Should be good for 1D, 2D, etc.
    hist_dct = IO.get_subhist()
    try:
        log.info("getting PID %s from subhists" % os.getpid() )
        hist_dct.get(histname).Fill(*vals)
    except KeyError:
        #This requested histogram does not exist; name passed wrong?
        log.warning("Histogram %s does not exist - check requested histname" % histname)
        raise KeyError
    else:
        return 0

def write_hists(path):
    #Precondition: Call from within the context of init_histograms
    #write a subprocess' histograms to a .root file at path
    #TODO: overwriting histograms?
    log.info("PID %i writing histograms to %s" % (os.getpid(), path))
    with rootpy.io.root_open(path, "recreate") as fh:
        for k, hist in IO.get_subhist().iteritems():
            hist.Write()
    return 0

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def extend_export_lst(target):
    #There are some special comparisons between neutrons that are not hard-coded
    # simulated neutron features
    target = init_permus(target)

    return target

# # # # # # # # # # # # # # # # # #
#Modifications called exactly once; cannot call within subprocess
all_export_lst = extend_export_lst(all_export_lst)
# # # # # # # # # # # # # # # # # #

def main():
    global all_export_lst

    all_export_lst = extend_export_lst(all_export_lst)
    subhist = init_hist_dct()

if __name__ == "__main__":
    main()
