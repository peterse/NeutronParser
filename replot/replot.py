#!/usr/local/bin/python
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1F,TCanvas, TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString

from comp_utils import THStacker,variableFiller,variableWriter

import math

ME = False

select = "mc_intType"

#select = "qelike"


if select == "mc_intType":
  process=["data","QE","RES","DIS","Other","","","","2p2h","","background","qelike"]
  minp=1
  maxp=8
else:
    process=["data","","","","","","","","","","background","qelike"]
    minp=10
    maxp=11

import sys,os, time, string

from array import array

# POT numbers from Wine and Cheese

gROOT.Reset();
gStyle.SetOptStat("");
gStyle.SetLineWidth(2)
#gROOT.SetStyle("Plain");
gStyle.SetLabelSize(0.04,"x");
gStyle.SetLabelSize(0.04,"y");
#gStyle.SetTitleFont(90);

#gStyle.SetPalette(69)
gStyle.SetPalette(69)

gStyle.SetPadColor(0);
gStyle.SetPadBorderMode(0);

gStyle.SetCanvasColor(0);
gStyle.SetCanvasBorderMode(0);

gStyle.SetFrameBorderMode(0);
gStyle.SetPadTickY(1)
gStyle.SetPadTickX(1)
#gStyle.SetTitleColor(0);
#gStyle.SetTitleBorderSize(1);


#gStyle.SetTitleX(0.10);
#gStyle.SetTitleY(0.96);
#gStyle.SetTitleW(0.5);
#gStyle.SetTitleH(0.06);

#gStyle.SetLabelOffset(1e-04);
#gStyle.SetLabelSize(0.05);
#gStyle.SetTitleSize(0.05);
  #  gStyle.SetOptStat("nemruo");
  #gStyle.SetStatColor(0);
  #gStyle.SetStatX(0.90);
#gStyle.SetStatY(0.98);

gStyle.SetLegendFillColor(0);

tone = 255.
red  = array('d',[ 180./tone, 190./tone, 209./tone, 223./tone, 204./tone, 228./tone, 205./tone, 152./tone,  91./tone])
green = array('d',[  93./tone, 125./tone, 147./tone, 172./tone, 181./tone, 224./tone, 233./tone, 198./tone, 158./tone])
blue  = array('d',[ 236./tone, 218./tone, 160./tone, 133./tone, 114./tone, 132./tone, 162./tone, 220./tone, 218./tone])
stops = array('d',[ 0.00, 0.05,0.1,0.2,0.3,0.4,0.7,0.8,1.0])
TColor.CreateGradientColorTable(9, stops, red, green, blue, 255, 0.5);


noMEC = False

POT_MEC = 2.485E21
POT_MC = 9.25E20
POT_DATA = 1.02E20
POT_DATA = 1.01994E20
#POT_DATA = 5.44923e+19

if ME:
  POT_DATA=5.44923e+19
  POT_MC=6.08291e+19
 # POT_MC=1e18
if noMEC:
  POT_MEC = 1E40

fid_mass_DATA = 1.74554E30

print sys.argv

#thevar = sys.argv[1]
#thecut = sys.argv[2]
thefile = sys.argv[1]
thename = sys.argv[2]
#thetitle = sys.argv[4]
#thenbins = string.atoi(sys.argv[5])
#thecutlow = string.atof(sys.argv[6])
#thecuthigh = string.atof(sys.argv[7])
option = sys.argv[3]
if len(sys.argv) > 4:
  max = string.atof(sys.argv[4])
else:
  max = 0.0

print "maximum set to ",max

thewt = POT_DATA/POT_MC

print "data/mc ratio is ",thewt


t = TCanvas()
pad = t.GetPad(0)
pad.SetBottomMargin(0.15)
pad.SetLeftMargin(0.15)

if "logy" in option:
  t.SetLogy()
name = thename
input = TFile.Open(thefile,"READONLY")


data = input.Get(name+"_0")
type(data)
#mc = input.Get("s_"+name)
#[data,mc_hists,process] = variableFiller(data_t,mc_t,select, process,thevar,thecut,thewt,thename,thetitle,thenbins,thecutlow,thecuthigh)
#mc = THStacker(thename,mc_hists,process)
#data.SetTitle("top;bottom;side")
#data.Print("")
#print data.GetTitle()
#print data.GetXaxis().GetTitle()
thetitle=data.GetTitle().replace("p_{z}","p_{#parallel}")
data.SetTitle(thetitle)
data.GetXaxis().SetTitle(thetitle)
data.GetXaxis().SetTitleSize(0.05)
print "thetitle",thetitle
data.GetYaxis().SetTitle("Entries        \n")
data.GetYaxis().SetTitleSize(0.05)
data.SetMarkerSize(1)
data.SetMarkerStyle(20)
if not "logy" in option:
  data.SetMaximum(data.GetMaximum()*1.2)
  data.SetMinimum(0)
else:
  data.SetMaximum(data.GetMaximum()*10.)
  data.SetMinimum(1)
if max != 0:
  data.SetMaximum(max)


data.GetYaxis().SetNdivisions(505)
data.GetYaxis().SetTitleOffset(1.35)
data.GetXaxis().SetTitleOffset(1.2)
data.GetYaxis().CenterTitle()
data.GetXaxis().CenterTitle()
data.GetXaxis().SetNdivisions(505)
if data.GetName() == "PZ":
  data.GetXaxis.SetRangeUser(0.0,15.)


data.Draw("PE")


leg = TLegend(0.55,0.5,0.9,0.87)
#leg2 = TLegend(0.72,0.5,0.87,0.87)
leg.SetNColumns(2)
leg.SetBorderSize(0)

entry = leg.AddEntry("grm","data","p")
entry.SetMarkerStyle(20)
#if "area" in option:
#  entry = leg.AddEntry("grm","Area Norm","")
#else:
#  entry = leg.AddEntry("","POT Norm","")
entry = leg.AddEntry("","","")

#leg2.AddEntry("","")
mc_hists = {}

colors = {1:ROOT.kBlue-6,
2:ROOT.kMagenta-6,
3:ROOT.kRed-6,
4:ROOT.kYellow-6,
5:ROOT.kWhite,
6:ROOT.kWhite,
7:ROOT.kWhite,
8:ROOT.kGreen-6,
9:ROOT.kTeal-6,
11:ROOT.kBlue-10,
12:ROOT.kMagenta-10,
13:ROOT.kRed-10,
14:ROOT.kYellow-10,
15:ROOT.kGray,
16:ROOT.kBlack,
17:ROOT.kBlack,
18:ROOT.kGreen-6,
19:ROOT.kTeal-6}
tot_data = data.Integral()
tot_mc = 0
tot_signal = 0
mc = THStack("newstack",thetitle)


for ib in range(1,-1,-1):
  #  for it in range(minp,maxp+1):
  for it in [2,3,4,5,6,1,8]:
    i = it+ib*10
    mc_hists[i] = input.Get(name+"_%d"%i)
    tot_mc += mc_hists[i].Integral()
    if i < 10:
      tot_signal += mc_hists[i].Integral()

for ib in range(1,-1,-1):
  #  for it in range(minp,maxp+1):
  for it in [2,3,4,5,6,1,8]:
    i = it+ib*10
    mc_hists[i].Print()
    mc_hists[i].SetFillColor(colors[it]);
    mc_hists[i].SetLineWidth(2)
    

    if (ib != 0):
      mc_hists[i].SetFillStyle(3224+it)

    if mc_hists[i].Integral()>0.:
      if "area" in option:
        mc_hists[i].Scale(tot_data/tot_mc)
      else:
        mc_hists[i].Scale(thewt)
      print "colors",colors[i]
      print process[it]
      mc.Add(mc_hists[i])


# make a legend

entry2 = leg.AddEntry(mc_hists[5],"qelike","f")
mc_hists[15].SetFillColor(ROOT.kBlack)
entry2 = leg.AddEntry(mc_hists[15],"background","f")


#for it in [1,2,3,4,8]:
for it in [2,3,4,1,8]:
  for ib in range(0,2):
    i = it+ib*10
    if mc_hists[i].Integral()<=0.:
      entry=leg.AddEntry("","","")
      continue
    if (ib == 0):
      entry=leg.AddEntry(mc_hists[i],process[it],"f")
    else:
      #mc_hists[i].SetFillStyle(3224)
      entry=leg.AddEntry(mc_hists[i],process[it],"f")


#entry2 = leg.AddEntry(mc_hists[5],"qelike","f")
#mc_hists[15].SetFillColor(ROOT.kBlack)
#entry2 = leg.AddEntry(mc_hists[15],"background","f")

leg.SetFillColor(0)

leg.Draw("same")
#variableWriter(thename,data,mc_hists,len(process),mc,leg)

print "totals ",tot_data,tot_mc,tot_signal," purity = ", tot_signal/tot_mc


mc.Draw("HIST same")


data.Draw("E same")
data.SetTitle("MINERvA anti-#nu;"+thetitle+";Entries")

data.Draw("AXIS same")

#data.Draw("PE same")


outname=thename+".pdf"
if option != "":
  outname = thename+"_"+option+".pdf"
pad.Print(outname)
pad.Draw()
ROOT.gROOT.SaveContext()


















#--------------- end of the body of the program -------

## wait for input to keep the GUI (which lives on a ROOT event dispatcher) alive
if __name__ == '__main__':
  rep = ''
  while not rep in [ 'q', 'Q' ]:
    rep = raw_input( 'enter "q" to quit: ' )
    if 1 < len(rep):
      rep = rep[0]


