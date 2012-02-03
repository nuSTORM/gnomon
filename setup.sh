XLIB=~/.cache/0install.net/implementations/sha1new=d89a1862c49e0613589ee865103afa0d01fa8494/lib
LIBS=`pwd`/lib:`geant4-config --prefix`/lib:`clhep-config --prefix`/lib:${XLIB}

export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:${LIBS}
export PYTHONPATH=$PYTHONPATH:${LIBS}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${LIBS}
