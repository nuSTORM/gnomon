LIBS=`pwd`/lib:`geant4-config --prefix`/lib:`clhep-config --prefix`/lib

export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:${LIBS}
export PYTHONPATH=$PYTHONPATH:${LIBS}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${LIBS}
