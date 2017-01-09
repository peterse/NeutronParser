# !/usr/local/bin/python
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1F,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend


import math



import sys,os, time, string

from array import array


def THStacker(name,hists,process):
  nhists = len(process)
  h_s = THStack("s_"+name,"stack");
  print h_s
 # colors ={}
 # for i in range(1,nhists):
 #   colors[i] = gStyle.GetColorPalette(i*8)


  for i in range(1,nhists):
    if (hists[i].Integral() > 0):
      print "stacking",i
      hists[i].Print();
      h_s.Add(hists[i]);
    else:
      print "hist ", i, " seems unhappy"

#  h_s.Print();

  return h_s


def variableFiller(data_t,mc_t,select,process,var,thecut,wt,name,title,nbins,cutlow,cuthigh):
  data_h = TH1F(name,title,nbins,cutlow,cuthigh)
  thing = var+">>"+name
  data_t.Draw(thing,thecut)


  nhists = len(process)

  mc_hists = {}

  for type in range(1,nhists):

    typestring = "%1d"%(type)
    histname = name+"_"+typestring
    mc_hists[type] = TH1F(histname,title,nbins,cutlow,cuthigh)
    thing = var+">>"+histname
    if select == "mc_intType":
      cut = "(mc_intType == "+typestring+")"

    else:
      cut = "(truth_qelike ==  (2- "+typestring+"))"

    if thecut != "":
      cut = cut+"*"+thecut
    cut = cut + "*(1+(57.0/50)*(truth_genie_wgt_Rvn1pi[2]-1))"

    cut = cut +"* ((mc_intType != 8) + (mc_intType == 8)*.31)"
    print thing,cut
    mc_t.Draw(thing,cut)
#    mc_hists[type].GetXaxis().SetTitle(title)
    mc_hists[type].Scale(wt)
    mc_hists[type].Print()

  return [data_h,mc_hists,process]

  # canvas = TCanvas("new")
  # canvas.cd()

def variableWriter(name,data_h,mc_hists,nhists,thestack,legend):


  output = TFile.Open(name+".root","RECREATE")
  data_h.Write()
  for type in range(1,nhists):
    mc_hists[type].Write()
  thestack.Write()
  legend.Write()
  output.Close()
