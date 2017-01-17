#!/bin/bash

TMP_HOME=$PWD

cd ~/NeutronParser/src/
source activate root
bash Deck1.sh
bash Deck2.sh

cd /home/epeters/HistCompOSU_clean/
source deactivate root
./run_comparison ~/NeutronParser/runs/deck1/split_hists/hist0.root ~/NeutronParser/runs/deck2/split_hists/hist0.root phiT_analysis_2
