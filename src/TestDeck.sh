#!/bin/bash

#Run the main program
#Specify the settings and inputs for the run
SCRIPT_HOME="$(dirname "$PWD")"
echo $SCRIPT_HOME

SOURCE_FILE="SmallCompleteFile.root"
SOURCE_PATH="/home/epeters/NeutronParser/tests"

TARGET_FILE="Analysis.root"
TARGET_PATH="/home/epeters/NeutronParser/runs/testdeck/"

TMP_DEST="/home/epeters/NeutronParser/runs/testdeck/split_files"
TMP_DEST_HIST="/home/epeters/NeutronParser/runs/testdeck/split_hists"
TMP="/home/epeters//NeutronParser/runs/testdeck/temp"

FILTER="/home/epeters/NeutronParser/runs/testdeck/filter.txt"

#Run the script with inputs
python $SCRIPT_HOME/rootparser/main.py $SOURCE_FILE $SOURCE_PATH $TARGET_FILE $TARGET_PATH $TMP_DEST $TMP_DEST_HIST $TMP $FILTER

exit
