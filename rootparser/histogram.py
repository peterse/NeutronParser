"""histogram.py - main methods for interfacing data with ROOT histograms"""

from rootpy.plotting import Hist, Hist2D, HistStack, Legend, Canvas
from collections import OrderedDict

#accessing TCanvas
import rootpy.ROOT as ROOT
from rootpy.plotting.utils import draw

#errors, warnings
from rootparser_exceptions import log

#IO
from IO import versioncontrol
import IO   #get, put, histogram interfacing


import rootpy
import os   #getpid

#Some plotting
import MINERvAmath as Mm
import numpy as np

#Where we'll put the output histograms
class HistogramManager:
    """Managing a .root file for storing historgrams from processing events in another root file"""



    def __init__(self):

        self.export_filename = None



#list of all supported export types, (name, (bins, min max), y-units)
n_pairs = []        #global tupl pairs of neutrons to compare - init
n_singles = ["recon_kine_n_P", "mc_kine_n_P", "mc_n_P", "n_blob"]
all_export_lst = [
                 ("null", (100,-1,1), "-" ),

                # ("n_trans_angle", (100,0,360), "deg" ),
                # ("p_trans_angle", (100, 0, 360), "deg" ),
                # ("nu_px", (100,-300, 300), "MeV/c" ),
                # ("nu_py", (100, -300, 300), "MeV/c"),
                # ("mu_x_err", (100,0,1), "-"),
                # ("mu_y_err", (100,0,1), "-" ),
                # ("mu_z_err", (100, 0, 1), "-"),
                # ("N_blobs-N_neutrons", (20, -10, 10), "Number of Neutrons", "counts"),
                # ("theta_nvb", (90, 0, 180), "deg", "counts/deg"),
                # ("cos(theta_nvb)", (90, 0, 1), "-", "counts" ),
                # ("theta_nvb_vs_En_datatype", (30, 0, 1200, 30, 0, 180), "E (MeV)", "Theta (deg)" ),
                # ("v_n(mc)_dot_v_mu", (100, 0, 360), "deg" ),
                # ("phiT", (100, 0, 360), "deg" ),
                # ("Dphi_T", (100, 0, 360), "deg" ),
                # ("mu_dangle", (100, 0, 20), "deg" ),
                # ("r_vb", (25, 0, 2000), "R_vb (mm)", "counts/mm" ),
                # ("En_0blob", (50, 0, 1200), "Energy (MeV)", "Neutrons/MeV" ),
                # ("En_1blob", (50, 0, 1200), "E (Mev)", "1/MeV" ),
                # ("En_01blob", (50, 0, 1200), "E (MeV)", "1/MeV" ),
                # ("E_n_vs_N_blob", (6, 0, 6, 30, 0, 1200), "N / blobs", "E (MeV)" ),
                # ("phi_T_vs_Emu", (30, 0, 1200, 30, 170, 180), "E (MeV)", "phi_T (deg)" ),
                # ("phiT_vs_En", (30, 0, 1200, 30, 170, 180), "E (MeV)", "phi_T (deg)" ),
                # ("Blob_find_efficiency", (50, 0, 1200), "-" ),
                # ("theta_nvb_vs_Eblob", (20, 0, 450, 45, 0, 180), "E (MeV)", "theta (deg)" ),
                # ("theta_nvb_vs_rvb", (30, 0, 600, 45, 0, 180), "R_vb (mm)","theta (deg)"  ),
                # ("theta_nvb_vs_DZ", (30, 0, 600, 90, 0, 180), "DZ (mm)", "theta (deg)" ),
                # ("Z1_Nblob_vs_MC", (50, 0, 600, 50, 0, 600), "E_blob (MeV)", "E_MC (MeV)"),
                # ("Z6_Nblob_vs_MC", (50, 0, 600, 50, 0, 600), "E_blob (MeV)", "E_MC (MeV)")
                ]

#


#TODO: ALL POSSIBLE COMBINATIONS VS EVERYTHING WE'RE PLOTTING??
ANGLE_PAIRS = [("mc_mu", "mc_n_P"), ("n_blob", "mc_n_P"),
                ("mc_mu", "data_mu")]
NEUTRONS = ["recon_kine_n_P", "mc_kine_n_P", "mc_n_P", "n_blob"]
MUONS = ["mc_mu", "data_mu"]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#Neutron comparison names for backwards compatibility
def make_n_energy_name(n_name):
    return "ENERGY_" + n_name
def make_n_pz_name(n_name):
    return "PZ_" + n_name
def make_n_comp_theta_name(tupl):
    return "DTHETA_%s_vs_%s" % tupl
def make_n_comp_energy_name(tupl):
    return "ENERGIES_%s_vs_%s" % tupl
def make_n_comp_rel_e_name(tupl):
    return "RELATIVE_ENERGY_%s_over_%s" % (tupl[1], tupl[0])

#Muon plotnames for backwards compatibility
def make_thetaX_name(mu_name):
    return "%s_thetaX" % mu_name
def make_thetaY_name(mu_name):
    return "%s_thetaY" % mu_name
def make_phiZ_name(mu_name):
    return "%s_phiZ" % mu_name

def make_Dphi_name(name1, name2):
    return "DPHI_XY_%s_%s" % (name1, name2)
def make_DthetaX_name(name1, name2):
    return "DTHETA_XZ_%s_%s" % (name1, name2)
def make_DthetaY_name(name1, name2):
    return "DTHETA_YZ_%s_%s" % (name1, name2)

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
    #return a handle to the histogram
    hist_dct = IO.get_subhist()
    try:
        #log.info("getting PID %s from subhists" % os.getpid() )
        hist_dct.get(histname).Fill(*vals)
    except KeyError:
        #This requested histogram does not exist; name passed wrong?
        log.warning("Histogram %s does not exist - check requested histname" % histname)
        raise KeyError
    else:
        return hist_dct.get(histname)



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#EXTENDING THE LIST OF HISTOGRAMS BEYOND WHAT IS HARD-CODED
def extend_export_lst(target):
    #There are some special comparisons between neutrons that are not hard-coded
    # simulated neutron features
    target = init_permus(target)
    #angles of various particles
    target = init_thetas(target)
    return target

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

    #Setting up all ordered combinations for comparing neutrons
    global n_pairs
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
    	out.append( (name_energy, (50, 0, 1200, 50, 0, 800), "%s (MeV)" % tupl[0], "%s (MeV)" % tupl[1]) )
        #Energy 1 vs Energy 2
    	name_rel = make_n_comp_rel_e_name(tupl)
    	out.append( (name_rel, (30, 0, 2), "MeV/MeV") )

    return out

def init_thetas(target):

    #Transverse angle, X, Y
    global NEUTRONS, MUONS
    for particle_name in NEUTRONS + MUONS:

        thetaX_name = make_thetaX_name(particle_name)
        thetaY_name = make_thetaY_name(particle_name)
        phiZ_name = make_phiZ_name(particle_name)
        for histname in [thetaX_name, thetaY_name, phiZ_name]:
            target.append((histname,  (200, -180, 180), "deg") )

    #Transverse Dphi , Dtheta angles
    global ANGLE_PAIRS
    for pair in ANGLE_PAIRS:
        Dphi_name = make_Dphi_name(pair[0], pair[1])
        DthetaX_name = make_DthetaX_name(pair[0], pair[1])
        DthetaY_name = make_DthetaY_name(pair[0], pair[1])
        if pair == ("mc_mu", "mc_n_P"):
            target.append((Dphi_name,  (200, 0, 360), "deg") )
        else:
            target.append((Dphi_name,  (200, -180, 180), "deg") )
        target.append((DthetaX_name,  (200, -180, 180), "deg") )
        target.append((DthetaY_name,  (200, -180, 180), "deg") )
    return target

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#Plotting for the analysis

def make_comp_hists(lookup_dct):
    #Passed a dictionary of current neutron 4-vecs, plot comparisons
    global n_pairs
    for n_pair in n_pairs:
        n0 = lookup_dct.get(n_pair[0])
        n1 = lookup_dct.get(n_pair[1])
        if n1 is not None and n0 is not None:
            #ENERGIES
            E_compare = make_n_comp_energy_name(n_pair)
            #log.info("filling %s with %d, %d" % (E_compare, n0[0], n1[0]))
            fill_hist(E_compare, n0[0], n1[0])
            #DTHETA
            phi_compare = make_n_comp_theta_name(n_pair)
            dangle, D = Mm.compare_vecs(n0[1:], n1[1:])
            fill_hist(phi_compare, dangle)
    return

def make_neutron_hists(lookup_dct):
    #Passed a dictionary of current neutrons, plot individual properties
    global n_singles
    for n_name in n_singles:
        if lookup_dct.get(n_name) is None:
            continue
        #ENERGY
        E_name = make_n_energy_name(n_name)
        fill_hist(E_name, lookup_dct.get(n_name)[0])
        #PZ
        PZ_name = make_n_pz_name(n_name)
        fill_hist(PZ_name, lookup_dct.get(n_name)[3])
    return


def make_vec_angle_hists(name, P):
    #Plot distributions of muon angle about the z-axis
    histname_X= make_thetaX_name(name)
    histname_Y = make_thetaY_name(name)
    histname_Z = make_phiZ_name(name)
    fill_hist(histname_X, np.degrees(np.arctan2(P[1], P[3])) )
    fill_hist(histname_Y, np.degrees(np.arctan2(P[2], P[3])) )
    fill_hist(histname_Z, np.degrees(np.arctan2(P[2], P[1])) )
    # fill_hist(histname_X, np.degrees(np.arctan(P[3], P[1])) )
    # fill_hist(histname_Y, np.degrees(np.arctan(P[3], P[2])) )
    # fill_hist(histname_Z, np.degrees(np.arctan(P[1]P[1])) )
    return

def make_Dphi_hist(name1, name2, P1, P2):
    #Plot the differnce in phiZ for two particles
    histname = make_Dphi_name(name1, name2)
    #Plot centered at 180 for muon-neutron:
    if (name1, name2) == ("mc_mu", "mc_n_P"):
        mode = 1
    else:
        mode = 0

    phi_XY = Mm.calculate_phi_T(P1[1:], P2[1:], mode)
    fill_hist(histname, phi_XY  )
    return phi_XY

def make_Dtheta_hists(name1, name2, P1, P2):
    #Plot the differnce in thetaX, thetaY for two particles
    histname_X = make_DthetaX_name(name1, name2)
    histname_Y = make_DthetaY_name(name1, name2)

    theta_XZ = Mm.calculate_theta_Tx(P1[1:], P2[1:])
    theta_YZ = Mm.calculate_theta_Ty(P1[1:], P2[1:])

    fill_hist(histname_X, theta_XZ)
    fill_hist(histname_Y, theta_YZ)
    return theta_XZ, theta_YZ

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# FORMATTING

#TODO: Make this automatically cycle through a pallate?
#Define default characteristics for histograms
DEFAULTS = {}
def reformat_hist(h, fillstyle=None, fillcolor=None,
                    linecolor=None, linewidth=None,
                    markercolor=None
                    ):

    if fillstyle:
        h.fillstyle = fillstyle
    # else:
    #     h.fillstyle = None

    if fillcolor:
        h.fillcolor = fillcolor
    # else:
    #     h.fillcolor = None

    if linecolor:
        h.linecolor = linecolor
    # else:
    #     h.linecolor = None

    if linewidth:
        h.linewidth = linewidth
    # else:
    #     h.linewidth = None

    if markercolor:
        h.markercolor = markercolor
    # else:
    #     h.markercolor = None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#WRITING, POST=PROCESSING


def write_hists(path):
    #Precondition: Call from within the context of init_histograms
    #write a subprocess' histograms to a .root file at path
    #TODO: overwriting histograms?
    #FIXME: Ahead of time checking for write directory
    log.info("PID %i writing histograms to %s" % (os.getpid(), path))
    #recreate hists, because I assume I trashed them on the last analysis
    with rootpy.io.root_open(path, "recreate") as fh:
        for k, hist in IO.get_subhist().iteritems():
            hist.Write()
    return 0

def hist_compare(f1, f2, out, lst=None):
    """
    For two filepaths make a hist stack of all histograms that they
    have in common. Save the output to 'out'
    kwargs:
        lst: If provided, compare only these histograms
    """

    #Get the set union of both histogram lists
    h1 = IO.fetch_histlist(f1)
    h2 = IO.fetch_histlist(f2)
    all_hists = list(set(h1) & set(h2))

    log.info("Stacking histograms from files:\n  %s\n  %s" % (f1, f2))
    #suppress canvas drawing
    ROOT.gROOT.SetBatch(1)

    with rootpy.io.root_open(f1, 'r') as fh1:
        with rootpy.io.root_open(f2, 'UPDATE') as fh2:
                for hname in all_hists:
                    histlst = [fh1.Get(hname), fh2.Get(hname)]
                    xtitle = histlst[0].GetXaxis().GetTitle()
                    ytitle = histlst[0].GetYaxis().GetTitle()
                    #FIXME: skip over 2D hists...
                    try:
                        c = stack_hists_2file(histlst, xtitle=xtitle, ytitle=ytitle)
                    except TypeError:
                        continue
                    else:
                        c.Write(hname+"_stack")

def stack_hists_2file(histlst, xtitle=None, ytitle=None, title=None):
    #given a number of hist objs, combine them on a histstack
    #Return: A canvas object with the edited histograms overlaid

    #For style ref, see https://root.cern.ch/doc/master/classTColor.html#C05
    colors = (ROOT.kRed, ROOT.kBlue, ROOT.kCyan, ROOT.kGreen, ROOT.kViolet)
    #styles = ("\\", "/", "-")
    stack = HistStack()

    #Edit histogram colors and build the stack
    for i, arg in enumerate(histlst):
        reformat_hist(arg, markercolor=colors[i])
        stack.Add(arg)

    #Canvas and draw the stack
    canvas = Canvas(width=700, height=500)
    ROOT.gStyle.SetOptStat(0)
    draw(stack, pad=canvas, xtitle=xtitle, ytitle=ytitle)

    #Set up a legend
    #TODO: Fontsize...
    legend = Legend(histlst, leftmargin=0.45, margin=0.3, pad=canvas)
    ROOT.gStyle.SetLegendBorderSize(0)
    legend.Draw()

    return canvas

def post_process_hists(path):
    #Precondition: Call from within the context of init_histograms
    #Do a variety of tasks to make hists more viewable, etc.
    log.info("PID %i processing histograms in %s" % (os.getpid(), path))
    #suppress canvas drawing
    ROOT.gROOT.SetBatch(1)
    with rootpy.io.root_open(path, "UPDATE") as fh:

        #muon distribution overlays
        muons = ["mc_mu", "data_mu"]
        mu_stackX = get_and_stack_hists(muons, make_thetaX_name)
        mu_stackY = get_and_stack_hists(muons, make_thetaY_name)
        mu_stackZ =  get_and_stack_hists(muons, make_phiZ_name)
        #neutron distribution overlays
        neutrons = ["mc_n_P", "mc_kine_n_P", "n_blob"]
        n_stackX = get_and_stack_hists(neutrons, make_thetaX_name)
        n_stackY = get_and_stack_hists(neutrons, make_thetaY_name)
        n_stackZ = get_and_stack_hists(neutrons, make_phiZ_name)

def get_and_stack_hists(prefix_lst, name_func):
    """
    Given a list of histogram base names and a rule for expanding them,
    retrieve the histograms and write a histogram stack
    """
    histlst = []
    names = []
    for name in prefix_lst:
        #get the histogram object and recover its name
        histname = name_func(name)
        histlst.append(IO.get_subhist().get(histname))
        names.append(histname)

    #Make a canvas with a HistStack + Legend
    log.info("Stacking histograms: %s" % " ".join(names))
    stack = stack_hists(histlst, xtitle=",".join(names))
    stack.Write()
    return stack


def overlay_hists(histlst, xtitle=None, ytitle=None):
    #passed a list of histograms, plot them all on top of the first entry

    #Canvas and draw the stack
    canvas = Canvas(width=700, height=500)

    #Overlay histograms
    for i,hist in enumerate(histlst):
        if i == 0:
            base = hist
            draw(hist, xtitle=xtitle, ytitle=ytitle, pad=canvas)
        else:
            draw(hist, same=True)

    #Set up a legend
    legend = Legend(histlst, leftmargin=0.45, margin=0.3, pad=canvas)
    legend.Draw()

    #Write the objects
    canvas.Write()
    # legend.Write()
    # base.write()
    return base

def stack_hists(histlst, xtitle=None, ytitle=None, title=None):
    #given a number of hist objs, combine them on a histstack
    #Return: A canvas object with the edited histograms overlaid

    #For style ref, see https://root.cern.ch/doc/master/classTColor.html#C05
    colors = (ROOT.kRed, ROOT.kBlue, ROOT.kCyan, ROOT.kGreen, ROOT.kViolet)
    #styles = ("\\", "/", "-")
    stack = HistStack()

    #Edit histogram colors and build the stack
    for i, arg in enumerate(histlst):
        reformat_hist(arg, markercolor=colors[i])
        stack.Add(arg)

    #Canvas and draw the stack
    canvas = Canvas(width=700, height=500)
    ROOT.gStyle.SetOptStat(0)
    draw(stack, pad=canvas, xtitle=xtitle, ytitle=ytitle)

    #Set up a legend
    #TODO: Fontsize...
    legend = Legend(histlst, leftmargin=0.45, margin=0.3, pad=canvas)
    ROOT.gStyle.SetLegendBorderSize(0)
    legend.Draw()

    return canvas



def save_as_png(hist, target):
    #take a hist (canvas obj) and save it to a target dir

    #spawn a canvas and draw the histogram
    c = ROOT.TCanvas()
    hist.Draw()
    c.Update()

    c.SaveAs(target)
    return

#TODO: Stylizing!
# TCanvas* old_canv = gPad->GetCanvas();
#
#     gROOT->SetBatch(kTRUE);
#     gROOT->ForceStyle(kTRUE);
#
#     Int_t orig_msz = gStyle->GetMarkerSize();
#     Int_t orig_mst = gStyle->GetMarkerStyle();
#     Int_t orig_lt  = gStyle->GetLineWidth();
#
#     gStyle->SetMarkerSize(1.0+scale/5);
#     gStyle->SetMarkerStyle(20);
#     gStyle->SetLineWidth(orig_lt*scale);
#
#     if(filename = "") {
#         filename = old_canv->GetName();
#         filename += ".png";
#     }
#
#     Int_t old_width  = old_canv->GetWindowWidth();
#     Int_t old_height = old_canv->GetWindowHeight();
#
#     Int_t new_width = old_width * scale;
#     Int_t new_height= old_height* scale;
#
#     TCanvas* temp_canvas = new TCanvas("temp", "", new_width, new_height);
#     old_canv->DrawClonePad();
#
#     temp_canvas->Draw();
#     temp_canvas->SaveAs(filename);
#     temp_canvas->Close();
#
#     gStyle->SetMarkerSize(orig_msz);
#     gStyle->SetMarkerStyle(orig_mst);
#     gStyle->SetLineWidth(orig_lt);
#
#     gROOT->ForceStyle(kFALSE);
#     gROOT->SetBatch(kFALSE);

    # ROOT.gSystem.ProcessEvents()
    # img = ROOT.TImage(20,20)
    # img.FromPad(c)
    # log.info("PID %i saving histograms to %s" % (os.getpid(), target))
    # img.WriteImage(target)

# # # # # # # # # # # # # # # # # #
#Modifications called exactly once; cannot call within subprocess
#all_export_lst = extend_export_lst(all_export_lst)
# # # # # # # # # # # # # # # # # #



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #




def main():
    global all_export_lst

    all_export_lst = extend_export_lst(all_export_lst)
    subhist = init_hist_dct()

if __name__ == "__main__":
    main()
