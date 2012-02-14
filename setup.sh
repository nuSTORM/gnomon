source /Users/tunnell/work/genie-trunk2/root/bin/thisroot.sh

XLIB=~/.cache/0install.net/implementations/sha1new=7b74a95224b4470762beb7f4de4a3a14a021e47d/lib
LIBS=`pwd`/lib:`geant4-config --prefix`/lib:`clhep-config --prefix`/lib:${XLIB}

export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:${LIBS}
export PYTHONPATH=$PYTHONPATH:${LIBS}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${LIBS}
