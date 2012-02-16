export GNOMON_ENV=/Users/tunnell/env/gnomon

source ${GNOMON_ENV}/bin/activate

#source /Users/tunnell/work/genie-trunk2/root/bin/thisroot.sh

export XLIB=/Users/tunnell/.cache/0install.net/implementations/sha1new=3e6859300df7f1a7458a61613d21ee2d0cbe3f0a/lib/
LIBS=`pwd`/lib:`geant4-config --prefix`/lib:`clhep-config --prefix`/lib:${XLIB}

export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:${LIBS}
export PYTHONPATH=$PYTHONPATH:${LIBS}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${LIBS}
