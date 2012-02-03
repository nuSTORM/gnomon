export GEANT_PREFIX=`geant4-config --prefix`
#export GEANT_PREFIX=/Users/tunnell/work/Geant4-9.5.0-Darwin

export XD=/Users/tunnell/.cache/0install.net/implementations/sha1new=d89a1862c49e0613589ee865103afa0d01fa8494

./configure macosx --with-g4-libdir=${GEANT_PREFIX}/lib --with-clhep-incdir=`clhep-config --prefix`/include --with-clhep-libdir=`clhep-config --prefix`/lib/ --with-boost-incdir=/opt/local/include --with-boost-libdir=/opt/local/lib --with-g4-incdir=${GEANT_PREFIX}/include/Geant4 --with-xercesc-incdir=${XD}/include --with-xercesc-libdir=${XD}/lib