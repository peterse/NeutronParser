#!/bin/bash

#Run the main program
#Specify the settings and inputs for the run
SCRIPT_HOME="$(dirname "$PWD")"
echo $SCRIPT_HOME

SOURCE_FILE="merged_CCQEAntiNuTool_minervamc_nouniverse_nomec.root"
SOURCE_PATH="~/NeutronParser/sample4"

TARGET_FILE="~/NeutronParse/runs/deck1/Analysis.root"
TARGET_PATH=$SOURCE_PATH

TMP_DEST="~/NeutronParser/runs/deck1/split_files"
TMP_DEST_HIST="~/NeutronParser/runs/deck1/split_hists"
TMP="~/NeutronParser/runs/deck1/temp"
#Run the script with inputs
python $SCRIPT_HOME/rootparser/main.py $SOURCE_FILE $SOURCE_PATH $TARGET_FILE $TARGET_PATH $TMP_DEST $TMP_DEST_HIST $TMP

exit
