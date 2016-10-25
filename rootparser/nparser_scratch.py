#v8 - treating MC efficiencies and DATA equally
#v7 - adapting for the combined files merged_CCQEAntiNuTool_minerva??_iso_v5.root
#Implementing Cheryl Patrick's selection criteria on the data as well...
#v6 no more sparsetest
#v3 - configured specificially for CutMCFull.root and tuple labels...
#v2 - configured specifically for SI_minerva_0050200 ...
#scratch pytho
import sys, os
#print sys.path
import ROOT as R
import dctROOTv9 as dR
from dctROOTv9 import trim_what as trimf
from collections import OrderedDict
import math
import numpy as np
from numpy.linalg import norm
from decimal import Decimal
#from CP_data_filter_v2 import CP_filter #This doesn't actually work...



#Notes for generalization
#-histogram framework setup
#-"get value" function for arbitrary path in a given rootfile
#

class MC_N_event:
	"""Characterizes a given set of events for a specified root file"""
	#Rotating frame -3deg => rotating all vectors +3deg
	correction_angle = np.radians(3) #degrees
	traits_list = ("Name", "ID", "4vec", "reconMass", "KE")
	#List of options available to export to histograms

	#PHYSICAL CONSTANTS
	c = 3E8 #m/s
	m_n = 939.6
	m_p = 938.3





	#Tag 2D histograms
	hist_2D = ["theta_nvb_vs_En_datatype", "E_n_vs_N_blob", "phi_T_vs_Emu", "theta_nvb_vs_Eblob", "theta_nvb_vs_rvb", "theta_nvb_vs_DZ", "phiT_vs_En", "Z1_Nblob_vs_MC", "Z6_Nblob_vs_MC"  ]

	hist_lines = []
	hist_efficiency = ["Blob_find_efficiency"]

	class_benchmarks = {"mu_n_180_evts":[]}

	#tolerance for position error in mc vs actual (pct)
	mc_r_tolerance = .05

	def __init__(self, filename, export_lst=[], benchmark=[], printing=True, export_fname="nparse_default", quiet=False, SPARSE=False):

		#export_lst is a list of strings with the same titles as those in export_lst

		self.quiet = quiet
		#Printing
		self.printing = printing

		self.get_rfile(filename)
		#Useful parameters and attributes
		self.rot_matrix = self.rot2D_matrix(self.correction_angle)
		self.BE_p = 30 #proton binding energy, MeV

		#Keep all trees, access as directories

		self.blob_count = 0
		self.point_count = 0

		#evt_splitter params
		self.SUMMARY = False #Whether we worry about a reconstructed nu. total

		# # # # # # # # # FILTERS # # # # # # # # #
		self.phi_T_min = 170
		self.theta_nvb_max = 180
		self.rvb_range = (0, 700)
		self.E_blob_range = (0,1200)
		self.E_n_range = (0,1200)
		self.one_blob_one_n = False
		self.one_blob_or_less = False
		self.QE_like_only = True


		#big_dangle_anal params for Arachnemaker
		self.BDA_thresh = (70,90)
		#self.BDA_thresh = (0,180)
		self.BDA_evts = []
		self.BDA_coords = []
		self.BDA_vals = []
		#Arachne values (tuples) - see Arachnemaker


		#Exporting
		self.export = any(export_lst)
		self.export_fname = export_fname
		self.export_lst = export_lst

		#The type of data or analysis we're conducting:

		#Do an analysis over a fraction of the data
		self.SPARSE = SPARSE
		self.MC_anal = True
		self.CCQE_str = "CCQEAntiNuTool_"
	#get relevant data from the sister rootfile
	def get_rfile(self, filename):
		self.sFT = dR.fileTools(filename)
		self.trees = self.sFT.tree_handle_dct

	def exe(self):

		#Exporting handled at exe; PyROOT doesn't seem to save ROOT mem locations
		if self.export:

			#Initialize all possible export histograms
			hout = R.TFile(self.export_fname+".root", "RECREATE")
			self.export_dct = dict((tupl[0], tupl[1]) for tupl in self.all_export_lst)
			#some janky setup for naming histograms
			self.export_names = {}
			for tupl in self.all_export_lst:
				#write hist titles
				try:
					xname = tupl[2]
				except:
					xname = "-"
				try:
					yname = tupl[3]
				except:
					yname = "-"
				self.export_names[tupl[0]] = (xname, yname)


			#add simulated neutrons to TH1F's
			self.n_comp_permus = self.init_permus()
			#Initialize dictionary using all the preset ranges
			for hname, ranges in self.export_dct.iteritems():
				#2D hists get special treatment
				if hname in self.hist_2D:
					self.export_dct[hname] = R.TH2F(hname, hname, ranges[0], ranges[1], ranges[2], ranges[3], ranges[4], ranges[5])
				#Lines/plots get different treatment too!
				#list is (x,y) pairs
				elif hname in self.hist_lines:
					self.export_dct[hname] = (R.TGraph(), [])
				else:
					self.export_dct[hname] = R.TH1F(hname, hname, ranges[0], ranges[1], ranges[2])

			#Get neutrons comparison permutations
			for tupl in self.n_comp_permus:
				name_theta = "theta_nvb_deg_%s_vs_%s" % tupl
				name_energy = "ENERGIES_%s_vs_%s" % tupl
				name_rel = "RELATIVE_ENERGY_%s_over_%s" % (tupl[1], tupl[0])
				self.export_dct[name_theta] =  R.TH1F(name_theta, name_theta, 90, 0, 180)
				self.export_dct[name_energy] =  R.TH2F(name_energy, name_energy, 50, 0, 600, 50, 0, 600)
				self.export_dct[name_rel] = R.TH1F(name_rel, name_rel, 30, 0, 2)
				self.export_dct[name_energy].GetXaxis().SetTitle(tupl[0])
				self.export_dct[name_energy].GetYaxis().SetTitle(tupl[1])
				self.hist_2D.append(name_energy)
			#export_dct is now populated w/ histograms at each key
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		#Splitting events, tree by tree
		for k, tree in self.trees.iteritems():
			#grab current tree
			self.current_tree = tree
			self.rnge = range(0,tree.GetEntries())
			if self.SPARSE:
				#process 1/5 events
				self.rnge = range(0, tree.GetEntries(), 100)
			#self.rnge = range(0,2000) # DEBUG

			for i in self.rnge:
				if not (i % 5000):
					print i,"/", tree.GetEntries(), "events processed"
				self.current_tree.GetEvent(i)


				#Pass the blob analyzer the particle dictionary
				blobs_n_found = self.compare_mc_neutrons(i)

				#print results of particle analysis
				if self.printing and blobs_n_found:
					print "\n\n"
					dR.dctTools(my_parts).printer()
					print "\n"
					dR.dctTools(summ).printer()


		#This is where we do functions on histograms

		#Efficiency of blob detection
		n_found = self.export_dct.get("En_1blob")
		n_missed = self.export_dct.get("En_0blob")
		blob_efficiency = self.export_dct.get("Blob_find_efficiency")
		blob_efficiency.Add(n_found, n_missed, 1.0, 1.0)
		blob_efficiency.Divide(n_found, blob_efficiency, 1.0, 1.0, "B")
		self.export_dct["Blob_find_efficiency"] = blob_efficiency
		#Write out histograms
		if self.export:
			for hname, hist in self.export_dct.iteritems():
				R.gStyle.SetOptStat(0)
				try:
					hist.GetXaxis().SetTitle(self.export_names.get(hname)[0])
					hist.GetYaxis().SetTitle(self.export_names.get(hname)[1])
				except TypeError:
					#For 2D's that already have names
					pass
				#special options for 2D histograms
				if hname in self.hist_2D:
					hist.SetOption("COLZ")
					hist.Write()

				else:
					hist.Write()
			#Print filters and parameters to the shell
			self.dump_anal_params()

		return 0
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	def init_permus(self):
	#Create all permutations of comparison between kinetic neutrons, blobs, and mc neutrs
		self.n_comp_dct = OrderedDict({"recon_kine_n_P": None})
		for k in ["mc_kine_n_P", "mc_n_P", "n_blob"]:
			self.n_comp_dct[k] = None

		#Individual energies, angles TH1's
		for n_name in self.n_comp_dct:
			self.export_dct["ENERGY " + n_name] = (100, 0, 1500)
			self.export_dct["PZ " + n_name] = (100, 0, 1500)
		#Setting up all combinations for comparing neutrons
		n_comp_permus = []
		for i, (k, v) in enumerate(self.n_comp_dct.iteritems()):
			current_k = k
			#grab every other neutron type, without repeats
			for j, (k2, v2) in enumerate(self.n_comp_dct.iteritems()):
				if j<=i:
					continue
				n_comp_permus.append( (current_k, k2))

		return n_comp_permus

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	def template_odct(self):
		dct = OrderedDict({})
		for trait in self.traits_list:
			dct[trait] = None
		return dct



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

			#Get mass, correct 4vec
			nth_dct["reconMass"] = self.vec_mass(nth_dct["4vec"])
			#Correct the yz coordinates of 4-vectors from detector -> beamline coords
			nth_dct["4vec"] = self.yz_rotation(nth_dct["4vec"])
			#mass = dR.PDGTools.fetch_mass(nth_dct["ID"])
			nth_dct["KE"] = nth_dct["4vec"][0] - nth_dct["reconMass"]

		if self.SUMMARY:
			#Get the summary of the reaction
			#summary = self.event_summary(event, mc_dct, nu_dct)

			#Get particle group info by summing up total momentum before adding neutrino
			P_out = self.get_P(mc_dct)
			nu_dct = self.recon_neutrino(mc_dct)
			self.i_recon_nu = N_parts
			#Add the neutrino at the N_parts index
			mc_dct[N_parts] = nu_dct

		return mc_dct


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	def compare_mc_neutrons(self, event):
	#Get the recon blob, vertexes, and neutron dict

		self.current_tree.GetEvent(event)
		#get particle summary for this event
		mc_dct = self.getMCParts(event)

		#Create a list of all particles found, and grab mc neutron
		all_recon = []
		for i_part, nth_dct in mc_dct.iteritems():
			name =nth_dct.get("Name")
			all_recon.append(name)
			if name == "neutron":
				mc_n_P = nth_dct.get("4vec")
				mc_n_E = mc_n_P[0]-self.m_n # kinetic energy
				mc_n_P = (mc_n_E, mc_n_P[1], mc_n_P[2], mc_n_P[3])
		#Check for number of QE particles
		N_p = all_recon.count("proton")
		N_n = all_recon.count("neutron")

		#FILTER QE with 1 n and 0 protons (already have, just being safe)
		# if not (N_p==0 and N_n==1) and self.QE_like_only:
		# 	#print "event %i rejected: %i neutrons; %i protons" % (event, N_n, N_p)
		# 	return 0

		#get mc muon
		mc_mu_P = mc_dct.get(self.i_big_lep).get("4vec")

		#get recon blobs, muon
		recon_results = self.getReconParts(event)
		if recon_results:
			recon_mu_P, r_blobs_lst, vtx = recon_results
		#Bad recon particles means blob data were inconsistent
		else:
			return 0

		if any(r_blobs_lst):
			N_blobs = len(r_blobs_lst)
		else:
			N_blobs = 0

		#make kinematic neutrons and check for negative energy
		recon_kine_n_P = self.makeKineNeutron(recon_mu_P)
		mc_kine_n_P = self.makeKineNeutron(mc_mu_P)
		if (not recon_kine_n_P) or (not mc_kine_n_P):
			return
		# -  -  -  -  -  -  Analysis -  -  -  -  -  -  -

		#FILTER QE events must have mu_dot_n in the transverse plane ~180 deg
		mu_dot_n_T, __ = self.compare_vecs(mc_mu_P[1:3], mc_n_P[1:3])
		#get phiT
		ex_flag = self.export and ("mu_stats" in self.export_lst)
		if ex_flag:
			self.export_dct["phiT"].Fill(mu_dot_n_T)

		#Only look at 1 blob 1 n
		if self.one_blob_one_n == True and N_blobs != 1:
			return

		#Get the best theta_nvb from the blobs in the sample
		dangle = 999
		cos_dangle = 0


		#Among many blobs, get the "best" blob
		#need to generalize this for when we don't have access to MC

		if N_blobs > 0:
			#get R_vb's in neutrino frame
			v_vtx_blob = [np.array(blob[1:])-np.array(vtx[:3]) for blob in r_blobs_lst]
			v_vtx_blob = [self.yz_rotation(vec) for vec in v_vtx_blob]
			for i, blob in enumerate(r_blobs_lst):
				v_vtx_blob[i] = np.array([blob[0] ] + list(v_vtx_blob[i]) )
			saved_i = 0
			for j_blob, v_b in enumerate(v_vtx_blob):
				#compare blob and neutron 3vecs
				temp_dangle, __ = self.compare_vecs(mc_n_P[1:], v_b[1:])

				temp_cos_dangle, __ = self.compare_vecs(mc_n_P[1:], v_b[1:], mode=1)
				#pick the blob with the smalles theta_nvb
				if temp_dangle < dangle:
					dangle = temp_dangle
					cos_dangle = temp_cos_dangle
					saved_i = j_blob
			#big 'R' is (E, DX, DY, DZ)
			R_vb = v_vtx_blob[saved_i]
			v_b = R_vb[1:]
			E_blob = R_vb[0]


		#Don't export 1-blob-1-n stats if more than 1 blob
		if N_blobs > 1 and self.one_blob_or_less:
			return True


		#Impose theta_nvb cutoff IF there was an angle comparison
		if dangle != 999:
			#satisfy theta_nvb maximum for ALL neutrons
			for n_vec in [recon_kine_n_P[1:], mc_kine_n_P[1:] ]:
				temp_dangle, __ = self.compare_vecs(n_vec, v_b)
				if temp_dangle > self.theta_nvb_max:
					return True
		#Else, we will continue to analyze events regardless of N_blob = 0 or 1
		else:
			pass

		#Statistics on difference in different muon vectors
		ex_flag = self.export and ("mu_stats" in self.export_lst)
		if ex_flag:
			recon_mu_p = recon_mu_P[1:]
			mc_mu_p = mc_mu_P[1:]
			for i, dim in enumerate(["mu_x_err", "mu_y_err", "mu_z_err"]):
				#Error in mc muon vs CCQE muon
				err_i =  abs((mc_mu_p[i] - recon_mu_p[i]) / mc_mu_p[i])
				self.export_dct[dim].Fill(err_i)
				mu_dangle, __ = self.compare_vecs(mc_mu_p, recon_mu_p)
				self.export_dct["mu_dangle"].Fill(mu_dangle)
				#Angle between mc muon and mc neutron
				mu_dot_n, __ = self.compare_vecs(mc_mu_p, mc_n_P[1:])
				self.export_dct["v_n(mc)_dot_v_mu"].Fill(mu_dot_n)
				# ... in the Transverse plane
				mu_dot_n_T, __ = self.compare_vecs(mc_mu_p[:2], mc_n_P[1:3])
				self.export_dct["Dphi_T"].Fill(mu_dot_n_T)
				self.export_dct["phi_T_vs_Emu"].Fill(mc_mu_P[0], mu_dot_n_T)
				self.point_count += 1


		#Statistics on single neutron, N blobs
		ex_flag = ("En_distribution" in self.export_lst)
		if ex_flag:
			#energy of single neutron, mc
			if N_blobs == 0:
				#count false negatives
				self.export_dct["En_0blob"].Fill(mc_n_E)
			self.export_dct["E_n_vs_N_blob"].Fill(N_blobs, mc_n_E)
			diff = N_blobs - N_n
			self.export_dct["N_blobs-N_neutrons"].Fill(diff)





		#Finish efficiency plotting
		if ex_flag and N_blobs == 1:
			#count good detections
			self.export_dct["En_1blob"].Fill(mc_n_E)

		#blobs are necessary to continue analysis
		if N_blobs == 0:
			return

		#FILTER for RVB
		rvb = norm(v_b)
		if rvb < self.rvb_range[0]:
			return

		#Battery of analyses on 1 neutron 1 blob
		ex_flag = ("1_blob_1_n" in self.export_lst) and self.export
		if ex_flag: #These are optimized for a single neutron and blob...
			self.export_dct["theta_nvb"].Fill(dangle)
			self.export_dct["cos(theta_nvb)"].Fill(cos_dangle)
			self.export_dct["r_vb"].Fill(norm(v_b) )
			#Angle of separation vs. neutron energy
			self.export_dct["theta_nvb_vs_En_datatype"].Fill(mc_n_E, dangle)
			#2D histograms of angle of separation vs blob energy and vertex-blob distance
			self.export_dct["theta_nvb_vs_Eblob"].Fill(R_vb[0], dangle)
			self.export_dct["theta_nvb_vs_rvb"].Fill(rvb, dangle)
			self.export_dct["theta_nvb_vs_DZ"].Fill(v_b[2], dangle)
			self.export_dct["phiT_vs_En"].Fill(mc_n_E, mu_dot_n_T)

		#Compare vectors and energies over all pairs of (a, b) for r_vb, kine_n_P, and mc_n_P
		ex_flag = ("kine_mc_blob" in self.export_lst) and self.export
		if ex_flag:
			#Fill a dct LIKE self.n_comp_dct
			n_combos = OrderedDict({"recon_kine_n_P": recon_kine_n_P})
 			for (k, v) in [("mc_kine_n_P", mc_kine_n_P), ("n_blob", R_vb), ("mc_n_P", mc_n_P)]:
				n_combos[k] = v


			#stats on individual neutrons
			for n_name, n in n_combos.iteritems():
				#fill with energies of each of the neutrons
				self.export_dct["ENERGY " + n_name].Fill(n[0])
				self.export_dct["PZ " + n_name].Fill(n[3])

			#Stats on pairs of neutrons
			for tupl in self.n_comp_permus:

				#funtion-ize a histogram naming scheme?
				name_theta = "theta_nvb_deg_%s_vs_%s" % tupl
				name_energy = "ENERGIES_%s_vs_%s" % tupl
				name_rel = "RELATIVE_ENERGY_%s_over_%s" % (tupl[1], tupl[0])

				#Ordered dict is very important
				n1 = n_combos.get(tupl[0])
				n2 = n_combos.get(tupl[1])

				n_dangle, __ = self.compare_vecs(n1[1:], n2[1:])

				#Compare angles (TH1F) and energies (TH2F)
				self.export_dct[name_theta].Fill(n_dangle)
				self.export_dct[name_energy].Fill(n1[0], n2[0])
				self.export_dct[name_rel].Fill((n2[0])/(n1[0]))

				#Look at energy distributions for different Z materials
				if self.MC_anal and tupl == ("n_blob", "mc_n_P"):
					Z_evt = self.current_tree.GetLeaf("mc_targetZ").GetValue()
					if Z_evt==1:
						self.export_dct["Z1_Nblob_vs_MC"].Fill(n1[0], n2[0])
					elif Z_evt==6:
						self.export_dct["Z6_Nblob_vs_MC"].Fill(n1[0], n2[0])

		return True



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	def getReconParts(self, event):
		#Get recon muon and list of blobs, pass along

		#Get recon muon
		recon_leafs = ["E_mu","px_mu", "py_mu", "pz_mu"]
		recon_mu_p = self.fetch_nleaf_vec(event, recon_leafs, tree=self.current_tree)

		#Get list of blob positions
		r_blobs_lst = self.fetch_blob(event)

		#get vertex, check for consistency
		vtx = self.fetch_vec(event, leafname=self.CCQE_str+"vtx")
		mc_vtx = self.fetch_vec(event, leafname="mc_vtx", tree=self.current_tree)
		dtheta, d_vtx = self.compare_vecs(vtx, mc_vtx)
		err = d_vtx / norm(vtx)
		if (err > self.mc_r_tolerance):
			return None

		return recon_mu_p, r_blobs_lst, vtx


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


		#dR.dctTools(n_dct).printer()
		#print "vtx:", type(vtx), "mc_vtx", mc_vtx
		#print "vtx angle err:", dtheta, "vtx d:", d_vtx
		#print self.fetch_blob(even	t)


	def big_dangle_anal(self):
	#An analysis on events with big theta_nvb
		for i, event in enumerate(self.BDA_evts):
			self.current_tree.GetEvent(event)
			Q2 = self.current_tree.GetLeaf("CCQEAntiNuTool_Q2").GetValue()
			mu = self.BDA_mus[i]
			n = self.BDA_ns[i]
			ang = self.BDA_ang[i]
			print "\n", event, ang
			print mu
			print n
			print Q2
		return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	def arachne_out(self, evt_lst=None, outname=None, det=None, write=True):
	#Formatevts in evt_lst to be read by arachnemaker.py
		if outname==None:
			outname = "arachne_default_out"
		if det==None:
			det = 'SIM_minerva'
		if evt_lst == None:
			evt_lst = self.BDA_evts

		with open(outname+".html", "w+") as f:
			#Website parameters
			width = "90%"
			height = "2000"
			version = 'v10r8p4'
			#Construct urls of all large angle events
			for i, event in enumerate(evt_lst):
				self.current_tree.GetEvent(event)
				run = self.current_tree.GetLeaf("mc_run").GetValue()
				subrun = self.current_tree.GetLeaf("mc_subrun").GetValue()
				#'gate' denotes mc_nthEvt !!!MUST ADD 1!!!
				gate = self.current_tree.GetLeaf("mc_nthEvtInFile").GetValue() + 1
				tslice = self.current_tree.GetLeaf("CCQEAntiNuTool_time_slice").GetValue()

				if run < 800 or run > 100000:
					print "bad run"
					continue
				vals_str = "<p> E_blob: %d E_n: %d |r_vb|: %d  theta_nvb: %d </p> \n" % self.BDA_vals[i]
				coords_str = "<p> X_blob: %d U_blob: %d V_blob: %d  Z_blob: %d </p> \n" % self.BDA_coords[i]
				url_str = "<a href=http://minerva05.fnal.gov/Arachne/arachne.html?det=%s&recoVer=%s&run=%d&subrun=%d&gate=%d&slice=%d> %d-%d-%d-%d </a> \n" % (det,version,run,subrun,gate,tslice,run,subrun,gate,tslice)
				#Visit Arachne stuff: blob energy, coords, link
				url =  vals_str + coords_str + url_str
				#print url
		  		#label = "%s-%s-%d-%s<p> \n" % (run,subrun,gate,tslice)
		  		#frame ="<iframe width=%s height=%s src=http://minerva05.fnal.gov/Arachne/arachne.html?det=SIM_minerva&recoVer=v10r6p13&run=%d&subrun=%d&gate=%d&slice=%d>   </iframe> <p> " %(height,width,run,subrun,gate,tslice)
				if write:
					f.write(url)


	def dump_anal_params(self):

		#QE like?
		print "Parameters for histogram exports:"
		if self.QE_like_only:
			print "Filter: 1 neutron 0 proton only"
		else:
			print "No filter imposed on QE vs not QE"
		if self.phi_T_min:
			print "Filter: phi_T > %i" % self.phi_T_min
		else:
			print "No filter imposed on phi_T"
		if self.one_blob_one_n:
			print "Filter: One blob only"
		else:
			print "No filter imposed on number of blobs"
		if self.theta_nvb_max:
			print "Filter: theta_nvb < %i" % self.theta_nvb_max
		else:
			print "No filter imposed on theta_nvb"
		print "%d < r_vb < %d" % self.rvb_range
		print "%d < E_n,mc < %d" % self.E_n_range



	def fetch_vec(self, event, leafname = "vtx", tree=None):
	#Return a generic 4vector from a given leaf
		if leafname == "vtx":
			leafname = self.CCQE_str+"vtx"
		#Default to CCQE experiment vals
		if tree == None:
			tree = self.current_tree
		leaf_obj = tree.GetLeaf(leafname)
		mc_vtx = [0, 0, 0, 0]

		for i, dim in enumerate([ "x", "y", "z", "t"]):
			mc_vtx[i] = leaf_obj.GetValue(i)

		return tuple(mc_vtx)
		leaf1 = self.current_tree.GetLeaf(self.CCQE_str+"vtx")
		leaf2 = self.current_tree.GetLeaf("mc_vtx")

	def fetch_nleaf_vec(self, event, leaflist, tree=None):
	#Given a tree and an ordered list of vectors, concatenate into a tuple
		if tree == None:
			tree = self.current_tree
		vec_out = [0 for i in leaflist]
		for i, leafname in enumerate(leaflist):
			vec_out[i] = tree.GetLeaf(self.CCQE_str+leafname).GetValue()
		return tuple(vec_out)

	def fetch_blob(self, event):
	#Return a list of tuples for each blob in the event
	#tuples are (E_blob, X, Y, Z)

		base_string = self.CCQE_str+"isoblob"
		#Check blob nubmer consistency over all dims
		for i,dim in enumerate(["X_sz", "Y_sz", "Z_sz"]):
			if i==0:
				num_blobs = int(self.current_tree.GetLeaf(base_string + dim).GetValue())
				#Skip empty events as early as possible
				if num_blobs == 0:
					return [None]
			elif (int(self.current_tree.GetLeaf(base_string + dim).GetValue())!= num_blobs):
				print "Error at event %i: Inconsistent number of blobs"
				return None

		vecs_out = [[0,0,0,0] for i in range(num_blobs)]
		#Iterate over x, y, z positions and fetch blob vecs
		for dim, suffix in enumerate(["E", "X", "Y", "Z"]):
			#get energy
			if dim==0:
				leaf_obj = self.current_tree.GetLeaf(self.CCQE_str+"isoblobE")
			#get position
			else:
				leaf_obj = self.current_tree.GetLeaf(base_string + suffix)

			for i in range(num_blobs):
				val = leaf_obj.GetValue(i)
				#Reject bad values
				if val < -9999:
					return None
				vecs_out[i][dim] = val

		self.blob_count += num_blobs
		return vecs_out
		#print "\n", event, "num blobs: ", num_blobs, "tot blobs", self.blob_count
		#print vecs_out


	@staticmethod
	def compare_vecs(a, b, mode=0):
	#Given two spacial 3vecs (unnormalized), compares angle between them and separation at endpoints
	#Pass this v_n*time and vec(vtx->blob) in (m)
		norm_a = norm(a)
		norm_b = norm(b)
		a = np.array(a)
		b = np.array(b)
		dot = np.dot(a,b)
		#law of cosines
		cos = dot/(norm_a*norm_b)
		theta = np.degrees(np.arccos(cos))
		d = np.sqrt(norm_a*norm_a + norm_b*norm_b - 2*dot)
		#Return the angle
		if mode==0:
			return theta, d
		#Return the cosine of the angle
		elif mode==1:
			return cos, d
		#print norm_a

	@staticmethod
	def xyz2xuvz(xyz_tup):
	#passed an (x,y,z), return (x,u,v,z) based on minerva scinitillator tilts
		x_out = xyz_tup[1]
		u_out = np.sin(np.pi/3)*xyz_tup[0] + np.cos(np.pi/3)*xyz_tup[1]
		v_out = np.sin(-np.pi/3)*xyz_tup[0] + np.cos(-np.pi/3)*xyz_tup[1]
		return (x_out, u_out, v_out, xyz_tup[2])


	@staticmethod
	def cart2spherical(tupl):
	#convert a 3vector from cartesian to (r, phi, theta)
		r = sum([x*x for x in tupl])**0.5
		phi = np.arctan2(tupl[1],tupl[0])
		theta = np.arccos(tupl[2]/r)
		return r, phi, theta



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	#KINDA DEPRECATED, I DON'T KNOW...
	def event_summary(self, event, dct, nu_dct):
	#Summarizes the full event
		summ_dct = OrderedDict({"event": event})

		all_parts = [nth_dct["Name"] for __, nth_dct in dct.iteritems()]

		#Outgoing, ingoing baryons
		summ_dct["out"] = {}
		summ_dct["in"] = {}
		for part in ["proton", "neutron"]:
			summ_dct["out"][part] = all_parts.count(part)


		#Particles involved in initial reaction are deterministic
		summ_dct["in"]["proton"] = summ_dct.get("out").get("proton") + 1
		summ_dct["in"]["neutron"] = summ_dct.get("out").get("neutron") - 1

		#Total outgoing momentum, mass
		summ_dct["out"]["P_out"] = self.get_P(dct)
		summ_dct["out"]["mass_out"] = sum([nth_dct["reconMass"] for __, nth_dct in dct.iteritems()]).real
		summ_dct["out"]["KE_out"] = sum([nth_dct["KE"] for __, nth_dct in dct.iteritems()]).real
		summ_dct["Z"] = self.current_tree.GetLeaf("mc_targetZ").GetValue()
		#! ! ! ! ! ! !
		#Q = (KE_out + m_mu) - (E_in)
		summ_dct["reconQ"] = summ_dct["out"]["KE_out"] + dct.get(self.i_big_lep).get("reconMass") - nu_dct["4vec"][0]
		summ_dct["mc_Q2"] = self.current_tree.GetLeaf("mc_Q2").GetValue()
		return summ_dct

	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	#DEPRECATED
	def trans_plane_angle(self, v_b, v_mu, v_nu):
	#Given the 4-vectors of nu and mu (v_nu, v_mu), find the angle (deg) of neutron out of this plane


		#print "input vectors: ", v_b (baryon), v_mu, v_nu
		v_nu = v_nu[1:]
		v_mu = v_mu[1:]

		#set up vector normal to mu - nu plane
		v_plane = np.cross(v_nu, v_mu)
		mag = sum(map(lambda x: x*x, v_plane)) ** .5
		v_plane = v_plane / mag

		#Find angle between the vectors (which is the complement of the angle we're looking for)
		v_b = v_b[1:]
		nmag = sum(map(lambda x: x*x, v_b)) ** .5
		v_b = np.array(v_b) / nmag
		not_phi = np.dot(v_plane, v_b)

		#print mag, nmag
		#print v_plane,"\n", v_b

		return 90 - np.arccos(not_phi)

	#DEPRECATED
	def azi_angle(self, v_b, v_mu):
	#Passed a baryon and muon 4vec, return the angle (deg) between them in the transverse plane
		azi_b = np.degrees(np.arctan2(v_b[2], v_b[1]))
		azi_mu = np.degrees(np.arctan2(v_mu[2], v_mu[1]))
		diff = azi_b - azi_mu
		#Range: 0-360
		if diff < 0:
			diff = diff + 360
		return diff



class DATA_N_event(MC_N_event):
	"""N_event analysis on real data inheriting from the MC event analysis"""

	def filter(self, filtered_name):

		#Currently broken
		print "Couldn't get arr references to work w ROOT"
		raise Exception
		return

		#Run CP's filters and set source to new, filtered files
		mc = False
		#If this is data, we need to filter using Cheryl's params
		global CP_filter
		#for now, only deal with a single tree...
		for tree_name, tree_handle in self.trees.iteritems():

			#Output a filtered rootfile
			filtered_name = CP_filter(tree_handle, filtered_name, mc)
		#Re-run root analysis on this file and continue with exe
		self.get_rfile(filtered_name)
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	def init_permus(self):
	#Overload to only permute DATA and RECON_KINE
		self.n_comp_dct = OrderedDict({"recon_kine_n_P": None})
		self.n_comp_dct["n_blob"] = None

		#Individual energies, angles TH1's
		for n_name in self.n_comp_dct:
			self.export_dct["ENERGY " + n_name] = (100, 0, 1500)
			self.export_dct["PZ " + n_name] = (100, 0, 1500)
		#Setting up all combinations for comparing neutrons
		#This works for two entries! Did you know that 2 items choose 2 == 1?!?
		n_comp_permus = []
		for i, (k, v) in enumerate(self.n_comp_dct.iteritems()):
			current_k = k
			#grab every other neutron type, without repeats
			for j, (k2, v2) in enumerate(self.n_comp_dct.iteritems()):
				if j<=i:
					continue
				n_comp_permus.append( (current_k, k2))

		return n_comp_permus
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

	def exe(self):

		self.MC_anal = False
		self.CCQE_str = "CCQEAntiNuTool_"
		#Exporting handled at exe; PyROOT doesn't seem to save ROOT mem locations

			#export_dct is now populated w/ histograms at each key
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

		#Splitting events, tree by tree
		for k, tree in self.trees.iteritems():
			#grab current tree
			self.current_tree = tree
			self.rnge = range(0,tree.GetEntries())
			if self.SPARSE:
				#process 1/5 events
				self.rnge = range(0, tree.GetEntries(), 5)
			#self.rnge = range(0,2000) # DEBUG

			for i in self.rnge:
				if not (i % 5000):
					print i,"/", tree.GetEntries(), "events processed"
				self.current_tree.GetEvent(i)

				#Pass the blob analyzer the particle dictionary
				blobs_n_found = self.compare_data_neutrons(i)

				#print results of particle analysis
				if self.printing and blobs_n_found:
					print "\n\n"
					dR.dctTools(my_parts).printer()
					print "\n"
					dR.dctTools(summ).printer()


		#This is where we do functions on histograms

		#Efficiency of blob detection
		n_found = self.export_dct.get("En_1blob")
		n_missed = self.export_dct.get("En_0blob")
		blob_efficiency = self.export_dct.get("Blob_find_efficiency")
		blob_efficiency.Add(n_found, n_missed, 1.0, 1.0)
		blob_efficiency.Divide(n_found, blob_efficiency, 1.0, 1.0, "B")
		self.export_dct["Blob_find_efficiency"] = blob_efficiency
		#Write out histograms
		if self.export:
			print self.export_names
			for hname, hist in self.export_dct.iteritems():
				R.gStyle.SetOptStat(0)
				try:
					hist.GetXaxis().SetTitle(self.export_names.get(hname)[0])
					hist.GetYaxis().SetTitle(self.export_names.get(hname)[1])
				except TypeError:
					#For 2D's that already have names
					pass
				if hname in self.hist_2D:
					hist.SetOption("COLZ")
					hist.Write()

				else:
					hist.Write()
			#Print filters and parameters to the shell
			self.dump_anal_params()

		return 1

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	def getReconParts(self, event):
		#Overload to ignore checking mc vertex position
		#and removed "CCQEANtiNuTool" tags

		#Get recon muon
		recon_leafs = ["E_mu","px_mu", "py_mu", "pz_mu"]
		recon_mu_p = self.fetch_nleaf_vec(event, recon_leafs, tree=self.current_tree)

		#Get list of blob positions
		r_blobs_lst = self.fetch_blob(event)

		#get vertex, check for consistency
		vtx = self.fetch_vec(event, leafname="vtx")

		return recon_mu_p, r_blobs_lst, vtx


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	def compare_data_neutrons(self, event):
	#Get the recon blob, vertexes, and neutron dict

		self.current_tree.GetEvent(event)

		#get recon blobs, muon
		recon_results = self.getReconParts(event)
		if recon_results:
			recon_mu_P, r_blobs_lst, vtx = recon_results
		#Bad recon particles means blob data were inconsistent
		else:
			return 0

		if any(r_blobs_lst):
			N_blobs = len(r_blobs_lst)
		else:
			N_blobs = 0


		#make kinematic neutrons
		recon_kine_n_P = self.makeKineNeutron(recon_mu_P)

		#'None' indicates a negative kinetic energy calculation...
		if recon_kine_n_P==None:
			return
		recon_E = recon_kine_n_P[0]
		# -  -  -  -  -  -  Analysis -  -  -  -  -  -  -
		#Only look at 1 blob 1 n
		if self.one_blob_one_n == True and N_blobs != 1:
			return


		#Statistics on single neutron, N blobs
		ex_flag = ("En_distribution" in self.export_lst)
		if ex_flag:
			#energy of single neutron, mc
			if N_blobs == 0:
				#count false negatives
				self.export_dct["En_0blob"].Fill(recon_E)
			self.export_dct["E_n_vs_N_blob"].Fill(N_blobs, recon_E)


		#Get the best theta_nvb from the blobs in the sample
		dangle = 999
		cos_dangle = 0
		#Among many blobs, get the "best" blob
		if N_blobs > 0:
			#get R_vb's in neutrino frame
			v_vtx_blob = [np.array(blob[1:])-np.array(vtx[:3]) for blob in r_blobs_lst]
			v_vtx_blob = [self.yz_rotation(vec) for vec in v_vtx_blob]
			for i, blob in enumerate(r_blobs_lst):
				v_vtx_blob[i] = np.array([blob[0] ] + list(v_vtx_blob[i]) )
			saved_i = 0
			for j_blob, v_b in enumerate(v_vtx_blob):
				#compare blob and recon neutrons
				temp_dangle, __ = self.compare_vecs(recon_kine_n_P[1:], v_b[1:])
				temp_cos_dangle, __ = self.compare_vecs(recon_kine_n_P[1:], v_b[1:], mode=1)
				#pick the blob with the smalles theta_nvb
				if temp_dangle < dangle:
					dangle = temp_dangle
					cos_dangle = temp_cos_dangle
					saved_i = j_blob
			#big 'R' is (E, DX, DY, DZ)
			R_vb = v_vtx_blob[saved_i]
			v_b = R_vb[1:]
			E_blob = R_vb[0]

		#require a maximum angle between the reconstructed neutron and blob
		if dangle > self.theta_nvb_max:
			return

		#FILTER for RVB
		rvb = norm(v_b)
		if rvb < self.rvb_range[0]:
			return

		#FILTER for E_n,mc, E_n,kine recon, E_n,kine mc
		if recon_kine_n_P[0] < self.E_n_range[0]:
			return

		#Finish efficiency plotting
		if ex_flag and N_blobs == 1:
			#count good detections
			self.export_dct["En_1blob"].Fill(recon_E)

		#remaining analyses require blobs
		if N_blobs == 0:
			return

		#Battery of analyses on 1 neutron 1 blob
		#These get blob values
		ex_flag = ("1_blob_1_n" in self.export_lst) and self.export
		if ex_flag: #These are optimized for a single neutron and blob...
			self.export_dct["theta_nvb"].Fill(dangle)
			self.export_dct["cos(theta_nvb)"].Fill(cos_dangle)
			self.export_dct["r_vb"].Fill(norm(v_b) )
			#Angle of separation vs. neutron energy
			self.export_dct["theta_nvb_vs_En_datatype"].Fill(E_blob, dangle)
			#2D histograms of angle of separation vs blob energy and vertex-blob distance
			self.export_dct["theta_nvb_vs_Eblob"].Fill(R_vb[0], dangle)
			self.export_dct["theta_nvb_vs_rvb"].Fill(rvb, dangle)
			self.export_dct["theta_nvb_vs_DZ"].Fill(v_b[2], dangle)

		#Compare vectors and energies over all pairs of (a, b) for r_vb, kine_n_P, and mc_n_P
		ex_flag = ("kine_mc_blob" in self.export_lst) and self.export #whatever keep it
		if ex_flag:

			#Fill a dct with only recon and blob
			n_combos = OrderedDict({"recon_kine_n_P": recon_kine_n_P})
			n_combos["n_blob"] = R_vb

			#stats on individual neutrons
			for n_name, n in n_combos.iteritems():
				#fill with energies of each of the neutrons
				self.export_dct["ENERGY " + n_name].Fill(n[0])
				self.export_dct["PZ " + n_name].Fill(n[3])

			#Stats on pairs of neutrons
			for tupl in self.n_comp_permus:
				#funtion-ize a histogram naming scheme?
				name_theta = "theta_nvb_deg_%s_vs_%s" % tupl
				name_energy = "ENERGIES_%s_vs_%s" % tupl
				name_rel = "RELATIVE_ENERGY_%s_over_%s" % (tupl[1], tupl[0])

				#Ordered dict is very important
				n1 = n_combos.get(tupl[0])
				n2 = n_combos.get(tupl[1])

				n_dangle, __ = self.compare_vecs(n1[1:], n2[1:])

				#Compare angles (TH1F) and energies (TH2F)
				self.export_dct[name_theta].Fill(n_dangle)
				self.export_dct[name_energy].Fill(n1[0], n2[0])
				self.export_dct[name_rel].Fill((n2[0])/(n1[0]))

		return True



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__":
	R.gStyle.SetOptStat(11100011)

	ex_lst = [] #Default no export
	bench_lst = [] #default no benchmarks
	fname = "default_nparser_hist"
	ALL_EXPORT = ["1_blob_1_n", "En_distribution", "mu_stats", "kine_mc_blob"]


	case = 1
	data_file = "merged_CCQEAntiNuTool_minervadata_iso_v5.root"
	mc_file = "selected_CCQEAntiNuTool_minervamc_iso_v5.root"
	filtered_file = data_file.replace("merged", "selected")

	#Data analysis
	Nparse_filtered = DATA_N_event(filtered_file , export_lst=ALL_EXPORT, printing=False, quiet=True, SPARSE=False)
	Nparse_unfiltered = DATA_N_event(filtered_file , export_lst=ALL_EXPORT, printing=False, quiet=True, SPARSE=False)

	#MC analysis
	Nparse_MC = MC_N_event(mc_file, export_lst=ALL_EXPORT, printing=False, quiet=True, SPARSE=False)
	Nparse_unMC = MC_N_event(mc_file, export_lst=ALL_EXPORT, printing=False, quiet=True, SPARSE=False)

	#MC in the data analysis
	Nparse_CROSS = DATA_N_event(mc_file, export_lst=ALL_EXPORT, printing=False, quiet=True, SPARSE=False)
	Nparse_unCROSS = DATA_N_event(mc_file, export_lst=ALL_EXPORT, printing=False, quiet=True, SPARSE=False)

	#SPARSE TEST
	if case == 1:
		print "MC, DATA ANALYSIS"
		#DATA
		Nparse_filtered.phi_T_min = 170
		Nparse_filtered.theta_nvb_max = 20
		Nparse_filtered.rvb_range = (200, 700)
		Nparse_filtered.E_n_range = (50,1200)
		Nparse_filtered.export_fname = "DATA_CP_filtered_rvb_gt%i_theta_kvblt%i_En_gt%i_30BE_v9" % (Nparse_filtered.rvb_range[0], Nparse_filtered.theta_nvb_max, Nparse_filtered.E_n_range[0])
		#unfiltered analysis
		Nparse_unfiltered.export_fname = "DATA_CP_filtered_rvb_gt%i_theta_kvblt%i_En_gt%i_30BE_v9" % (Nparse_unfiltered.rvb_range[0], Nparse_unfiltered.theta_nvb_max, Nparse_unfiltered.E_n_range[0])


		#MC
		Nparse_MC.phi_T_min = 170
		Nparse_MC.theta_nvb_max = 20
		Nparse_MC.rvb_range = (200, 700)
		Nparse_MC.E_n_range = (50,1200)
		Nparse_MC.export_fname = "MC_rvb_gt%i_theta_kvblt%i_En_gt%i_30BE_v9" % (Nparse_MC.rvb_range[0], Nparse_MC.theta_nvb_max, Nparse_MC.E_n_range[0])
		#unfiltered analysis
		Nparse_unMC.export_fname = "MC_rvb_gt%i_theta_kvblt%i_En_gt%i_30BE_v9" % (Nparse_unMC.rvb_range[0], Nparse_unMC.theta_nvb_max, Nparse_unMC.E_n_range[0])

		#execute
		#Nparse_filtered.exe()
		#Nparse_unfiltered.exe()

		Nparse_MC.exe()
		Nparse_unMC.exe()
		sys.exit()
		print "CROSS ANALYSIS"
		#MC_IN_DATA CROSS ANALYSIS

		Nparse_unCROSS.export_fname = "CROSS_rvb_gt%i_theta_kvblt%i_En_gt%i_30BE_v9" % (Nparse_unCROSS.rvb_range[0], Nparse_unCROSS.theta_nvb_max, Nparse_unCROSS.E_n_range[0])

		Nparse_CROSS.phi_T_min = 170
		Nparse_CROSS.theta_nvb_max = 20
		Nparse_CROSS.rvb_range = (200, 700)
		Nparse_CROSS.E_n_range = (50,1200)
		Nparse_CROSS.export_fname = "CROSS_rvb_gt%i_theta_kvblt%i_En_gt%i_30BE_v9" % (Nparse_CROSS.rvb_range[0], Nparse_CROSS.theta_nvb_max, Nparse_CROSS.E_n_range[0])

		Nparse_unCROSS.exe()
		Nparse_CROSS.exe()
