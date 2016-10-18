#!/bin/bash
#InstallLocalPython.sh
#Installation script to get all of the necessar modules for this library
#Installed using python's "home" installation option
#call "source InstallLocalPython.sh" to

#python 2.7.12 - need to modify depending on the version
# cd /tmp
# wget https://www.python.org/ftp/python/2.7.12/Python-2.7.12.tgz
# cd Python-2.7.12
#
# #configure and install HOME bin & lib
# ./configure
# make altinstall prefix=~ exec-prefix=~
#
# #go link this executable and alias it; same on bashrc
# cd ~/bin
# ln -s python2.7 python
#
# #set up aliasing and append to .bashrc
# alias python="~/bin/python"
# echo 'alias python="~/bin/python"' >> ~/.bashrc

#get conda for environment management
#Make sure you do not alias python or set PYTHONPATH!!!
if [ ! -f ~/tmp ]; then
   mkdir ~/tmp
fi
cd ~/tmp
wget https://repo.continuum.io/archive/Anaconda2-4.2.0-Linux-x86_64.sh
bash archive/Anaconda2-4.2.0-Linux-x86_64.sh
#alias and add to .bashrc
alias conda="~/bin/anaconda2/bin/conda"
alias anaconda="~/bin/anaconda2/bin/anaconda"
echo 'alias conda="~/bin/anaconda2/bin/conda"' >> ~/.bashrc
echo 'alias anaconda="~/bin/anaconda2/bin/anaconda"' >> ~/.bashrc

conda update conda
conda config --add channels https://conda.anaconda.org/NLeSC


#CERN ROOT conda - interface courtesy of the Netherlands
#https://nlesc.gitbooks.io/cern-root-conda-recipes/content/installing_root-numpy_and_rootpy_via_conda.html
conda install anaconda-client
#Create an environment to package conda libs in
#FIXME: root env works with ROOT, but not new env
conda create -n NeutronParser
source activate NeutronParser

#root-numpy with older version of root?
conda install root-numpy root=5
conda install rootpy root=5
