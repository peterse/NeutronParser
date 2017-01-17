#!/bin/bash

#Run the main program
#Specify the settings and inputs for the run
SCRIPT_HOME="$(dirname "$PWD")"
echo $SCRIPT_HOME

SOURCE_FILE="merged_CCQEAntiNuTool_minervamc_nouniverse_nomec.root"
SOURCE_PATH="/home/epeters/NeutronParser/sample4"

TARGET_FILE="Deck1Hist.root"
TARGET_PATH="/home/epeters/NeutronParser/runs/deck1"

TMP_DEST="/home/epeters/NeutronParser/runs/deck1/split_files"
TMP_DEST_HIST="/home/epeters/NeutronParser/runs/deck1/split_hists"
TMP="/home/epeters/NeutronParser/runs/deck1/temp"

FILTER="/home/epeters/NeutronParser/runs/deck1/filter.txt"

#Run the script with inputs
python $SCRIPT_HOME/rootparser/main.py $SOURCE_FILE $SOURCE_PATH $TARGET_FILE $TARGET_PATH $TMP_DEST $TMP_DEST_HIST $TMP $FILTER

exit
