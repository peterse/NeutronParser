"""histogram.py - main methods for interfacing data with ROOT histograms"""

class HistogramManager:
    """Managing a .root file for storing historgrams from processing events in another root file"""

    all_export_lst = [
                    ("n_trans_angle", (100,0,360), "deg" ),
                    ("p_trans_angle", (100, 0, 360), "deg" ),
                    ("nu_px", (100,-300, 300), "MeV/c" ),
                    ("nu_py", (100, -300, 300), "MeV/c"),
                    ("mu_x_err", (100,0,1) ),
                    ("mu_y_err", (100,0,1) ),
                    ("mu_z_err", (100, 0, 1) ),
                    ("N_blobs-N_neutrons", (20, -10, 10), "Number of Neutrons", "counts"),
                    ("theta_nvb", (90, 0, 180), "deg", "counts/deg"),
                    ("cos(theta_nvb)", (90, 0, 1), "-", "counts" ),
                    ("theta_nvb_vs_En_datatype", (30, 0, 1200, 30, 0, 180), "E (MeV)", "Theta (deg)" ),
                    ("v_n(mc)_dot_v_mu", (100, 0, 360) ),
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
                    ("Blob_find_efficiency", (50, 0, 1200) ),
                    ("theta_nvb_vs_Eblob", (20, 0, 450, 45, 0, 180), "E (MeV)", "theta (deg)" ),
                    ("theta_nvb_vs_rvb", (30, 0, 600, 45, 0, 180), "R_vb (mm)","theta (deg)"  ),
                    ("theta_nvb_vs_DZ", (30, 0, 600, 90, 0, 180), "DZ (mm)", "theta (deg)" ),
                    ("Z1_Nblob_vs_MC", (50, 0, 600, 50, 0, 600), "E_blob (MeV)", "E_MC (MeV)"),
                    ("Z6_Nblob_vs_MC", (50, 0, 600, 50, 0, 600), "E_blob (MeV)", "E_MC (MeV)")
                    ]

    def __init__(self):

        self.export_filename = None
